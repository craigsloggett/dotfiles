# GPG Master Key and Subkeys

## Generate the GPG Master Key Pair

```shell
gpg --full-generate-key
```

The default selections are good choices:

```shell
Please select what kind of key you want:
   (1) RSA and RSA
   (2) DSA and Elgamal
   (3) DSA (sign only)
   (4) RSA (sign only)
   (9) ECC (sign and encrypt) *default*
  (10) ECC (sign only)
  (14) Existing key from card
Your selection? 9
```

```shell
Please select which elliptic curve you want:
   (1) Curve 25519 *default*
   (4) NIST P-384
   (6) Brainpool P-256
```

```shell
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 1y
```

At this point, it will ask for your name and email and a password for the key pair. To confirm the key,

```shell
gpg --list-secret-keys --with-subkey-fingerprints
```

For increased security, it is recommended that you use only subkeys on your regular machine and store your master key offline.

## Generate the GPG Signing Subkey

```shell
gpg --edit-key XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

At the `gpg>` prompt, type `addkey` and hit enter:

```shell
gpg> addkey
Please select what kind of key you want:
   (3) DSA (sign only)
   (4) RSA (sign only)
   (5) Elgamal (encrypt only)
   (6) RSA (encrypt only)
  (10) ECC (sign only)
  (12) ECC (encrypt only)
  (14) Existing key from card
Your selection? 10
```

Again, the default selections are good choices:

```shell
Please select which elliptic curve you want:
   (1) Curve 25519 *default*
   (4) NIST P-384
   (6) Brainpool P-256
Your selection? 1
```

```shell
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 1y
```

To remove the Sign capability from the primary key, type `change-usage` at the `gpg>` prompt:

```shell
Possible actions for this ECC key: Sign Certify Authenticate
Current allowed actions: Sign Certify

   (S) Toggle the sign capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? S
```

## Export and Backup Keys

```shell
gpg --output public-keys.gpg --armor --export XXXXXXXXXXXXXXXXXXXXXXXXXXXX
gpg --output secret-keys.gpg --armor --export-secret-key XXXXXXXXXXXXXXXXXXXXXXXXXXXX
gpg --output secret-subkeys.gpg --armor --export-secret-subkeys XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Backup these files to an offline location like an external USB drive.

## Remove the Primary Key

We need to remove the primary key from our main machine:

```shell
gpg --delete-secret-keys XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Then import just the subkeys which allow us to sign and encrypt from our local device, but not
be able to generate new subkeys without re-importing the master key.

```shell
gpg --import secret-subkeys.gpg
```

Now, we want to trust the imported keys by entering in `trust` in the `gpg>` prompt:

```shell
gpg --edit-key XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

```shell
Please decide how far you trust this user to correctly verify other users' keys
(by looking at passports, checking fingerprints from different sources, etc.)

  1 = I don't know or won't say
  2 = I do NOT trust
  3 = I trust marginally
  4 = I trust fully
  5 = I trust ultimately
  m = back to the main menu

Your decision? 5
```
