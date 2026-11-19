import AVFoundation
import CoreML
import Foundation

struct Request: Decodable {
    let id: String
    let windowStart: Double
    let mask: [[Double]]
}

struct Embedding: Encodable {
    let id: String
    let embedding: [Float]
}

enum EmbedError: Error {
    case usage
    case unreadableAudio
    case missingOutput(String)
    case unexpectedShape([NSNumber])
}

enum Window {
    static let sampleRate = 16000.0
    static let samples = 160_000
    static let frames = 589
    static let frameStep = 270.0 / 16000.0
    static let frameCenter = 991.0 / 16000.0 / 2.0
}

func samples(from path: String) throws -> [Float] {
    let file = try AVAudioFile(forReading: URL(fileURLWithPath: path))
    let source = file.processingFormat
    guard
        let target = AVAudioFormat(
            commonFormat: .pcmFormatFloat32,
            sampleRate: Window.sampleRate,
            channels: 1,
            interleaved: false
        ),
        let converter = AVAudioConverter(from: source, to: target),
        let input = AVAudioPCMBuffer(pcmFormat: source, frameCapacity: 1 << 16),
        let output = AVAudioPCMBuffer(pcmFormat: target, frameCapacity: 1 << 16)
    else {
        throw EmbedError.unreadableAudio
    }

    converter.downmix = true
    var samples: [Float] = []
    var isExhausted = false
    while true {
        output.frameLength = 0
        var failure: NSError?
        let status = converter.convert(to: output, error: &failure) { _, inputStatus in
            if !isExhausted {
                do {
                    try file.read(into: input, frameCount: input.frameCapacity)
                } catch {
                    isExhausted = true
                }
            }

            if isExhausted || input.frameLength == 0 {
                isExhausted = true
                inputStatus.pointee = .endOfStream
                return nil
            }

            inputStatus.pointee = .haveData
            return input
        }
        if let failure {
            throw failure
        }

        let count = Int(output.frameLength)
        if let channel = output.floatChannelData?[0] {
            samples.append(contentsOf: UnsafeBufferPointer(start: channel, count: count))
        }

        let isDrained = count == 0 && isExhausted
        if status == .endOfStream || status == .error || isDrained {
            return samples
        }
    }
}

func array(at name: String, in features: MLFeatureProvider) throws -> MLMultiArray {
    guard let array = features.featureValue(for: name)?.multiArrayValue else {
        throw EmbedError.missingOutput(name)
    }

    return array
}

func embedding(
    for request: Request,
    in audio: [Float],
    from fbank: MLModel,
    to embedder: MLModel
) throws -> Embedding {
    let window = try MLMultiArray(
        shape: [1, 1, NSNumber(value: Window.samples)], dataType: .float32
    )
    let weights = try MLMultiArray(shape: [1, NSNumber(value: Window.frames)], dataType: .float32)
    let windowSamples = window.dataPointer.bindMemory(to: Float.self, capacity: Window.samples)
    let frameWeights = weights.dataPointer.bindMemory(to: Float.self, capacity: Window.frames)
    let offset = Int((request.windowStart * Window.sampleRate).rounded())
    for index in 0 ..< Window.samples {
        let sample = offset + index
        windowSamples[index] = audio.indices.contains(sample) ? audio[sample] : 0
    }

    for frame in 0 ..< Window.frames {
        let instant = request.windowStart + Double(frame) * Window.frameStep + Window.frameCenter
        let isHeard = request.mask.contains { span in
            span.count == 2 && instant >= span[0] && instant <= span[1]
        }
        frameWeights[frame] = isHeard ? 1 : 0
    }

    let heard = try MLDictionaryFeatureProvider(dictionary: ["audio": window])
    let features = try array(at: "fbank_features", in: fbank.prediction(from: heard))
    let weighted = try MLDictionaryFeatureProvider(
        dictionary: ["fbank_features": features, "weights": weights]
    )
    let vector = try array(at: "embedding", in: embedder.prediction(from: weighted))
    guard
        vector.shape.first?.intValue == 1,
        let dimension = vector.shape.last?.intValue,
        let stride = vector.strides.last?.intValue
    else {
        throw EmbedError.unexpectedShape(vector.shape)
    }

    var values: [Float] = []
    values.reserveCapacity(dimension)
    for index in 0 ..< dimension {
        values.append(vector[index * stride].floatValue)
    }

    return Embedding(id: request.id, embedding: values)
}

func run(_ arguments: [String]) throws {
    guard arguments.count == 5 else {
        throw EmbedError.usage
    }

    let audio = try samples(from: arguments[1])
    let models = URL(fileURLWithPath: arguments[2])
    let configuration = MLModelConfiguration()
    // The embedding model answers `.cpuAndGPU` with a wrongly shaped array, so never ask for it.
    configuration.computeUnits = .all
    let fbank = try MLModel(
        contentsOf: models.appendingPathComponent("FBank.mlmodelc"),
        configuration: configuration
    )
    let embedder = try MLModel(
        contentsOf: models.appendingPathComponent("Embedding.mlmodelc"),
        configuration: configuration
    )
    let requests = try JSONDecoder().decode(
        [Request].self, from: Data(contentsOf: URL(fileURLWithPath: arguments[3]))
    )
    var embeddings: [Embedding] = []
    embeddings.reserveCapacity(requests.count)
    for request in requests {
        try embeddings.append(embedding(for: request, in: audio, from: fbank, to: embedder))
    }

    try JSONEncoder().encode(embeddings).write(to: URL(fileURLWithPath: arguments[4]))
}

do {
    try run(CommandLine.arguments)
} catch EmbedError.usage {
    let usage = "usage: embed <audio> <models> <requests.json> <out.json>\n"
    FileHandle.standardError.write(Data(usage.utf8))
    exit(2)
} catch {
    FileHandle.standardError.write(Data("embed: \(error)\n".utf8))
    exit(1)
}
