return {
  "hrsh7th/nvim-cmp",
  config = function()
    require("cmp").setup({
      snippet = {
        expand = function(args)
          vim.fn["vsnip#anonymous"](args.body)
        end,
      },
      window = {
        completion = require("cmp").config.window.bordered(),
        documentation = require("cmp").config.window.bordered(),
      },
      mapping = require("cmp").mapping.preset.insert({
        ['<C-b>'] = require("cmp").mapping.scroll_docs(-4),
        ['<C-f>'] = require("cmp").mapping.scroll_docs(4),
        ['<C-Space>'] = require("cmp").mapping.complete(),
        ['<C-e>'] = require("cmp").mapping.abort(),
        ['<CR>'] = require("cmp").mapping.confirm({ select = true }),
      }),
      sources = require("cmp").config.sources({
        { name = 'nvim_lsp' },
      }),
      {
        { name = 'buffer' },
      }
    })
  end,
}
