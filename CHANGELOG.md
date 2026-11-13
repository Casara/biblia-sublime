# Changelog

Mudanças do pacote do Sublime Text. As do programa `biblia` estão no
`CHANGELOG.md` do [biblia-cli](https://github.com/Casara/biblia-cli).

## [0.2.0] - 2026-11-13

### Adicionado

- Comandos na paleta: **Bíblia: consultar referência selecionada**,
  **inserir texto no lugar da referência**, **consultar…**, **passagens
  paralelas da referência selecionada** e **inserir o texto das passagens
  paralelas**.
- Configurações e atalhos em *Preferences › Package Settings › Bíblia* e
  na paleta (*Preferences: Bíblia Settings*, *Preferences: Bíblia Key
  Bindings*), abrindo lado a lado com os padrões.
- Atalhos sugeridos, sem ativar nenhum: `Ctrl+Alt+B`, `Ctrl+Alt+Shift+B`,
  `Ctrl+Alt+L` e `Ctrl+Alt+Shift+L`.
- Formato do texto inserido pelo tipo do arquivo (`auto`: `.md` → `md`,
  `.typ` → `typ`), configurável em `formatos_por_extensao`.
- O programa `biblia` é procurado no `PATH` e em `~/.local/bin` e
  `~/go/bin`; no Windows, também como `biblia.exe`, sem abrir janela de
  console.

[0.2.0]: https://github.com/Casara/biblia-sublime/tree/0.2.0
