# Changelog

Mudanças do pacote do Sublime Text. As do programa `biblia` estão no
`CHANGELOG.md` do [biblia-cli](https://github.com/Casara/biblia-cli).

## [0.4.0] - 2026-11-16

### Mudado

- O nome do pacote aparece como **Biblia**, sem acento, onde é digitado
  ou procurado: os comandos da paleta (*Biblia: consultar…*,
  *Preferences: Biblia Settings*), o menu *Package Settings › Biblia* e o
  arquivo de configurações, que passa a ser `Biblia.sublime-settings`.
  Quem já tinha um `Packages/User/biblia.sublime-settings` precisa
  renomeá-lo.
- Os atalhos sugeridos estão em `Example.sublime-keymap`, sem comentar:
  o Sublime Text não lê esse arquivo, e copiar fica mais fácil.

## [0.3.2] - 2026-11-13

### Documentação

- README com imagens das extensões funcionando.

## [0.3.1] - 2026-11-13

### Documentação

- README: o que sai do computador do usuário (só as referências
  consultadas, para a Bíblia Online).

## [0.3.0] - 2026-11-13

### Adicionado

- **Bíblia: consultar com o original (hebraico/grego e Strong)**: o `-s`
  do programa, numa aba *Bíblia* só de leitura. Atalho sugerido:
  `Ctrl+Alt+O`.
- **Bíblia: Strong…**: o verbete do número sob o cursor ou selecionado
  (também na aba *Bíblia*); sem número, pergunta o número, a
  transliteração (`-tr`) ou a glosa (`-glosa`).
- **Bíblia: consultar em outras traduções…** e **inserir texto em outras
  traduções…**: pergunta as traduções só para aquela vez, começando da
  última escolha.

### Corrigido

- O `versoes` das configurações não é mais enviado aos subcomandos que
  não aceitam `-v` (`strong`, `versoes`).

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

[0.4.0]: https://github.com/Casara/biblia-sublime/tree/0.4.0
[0.3.2]: https://github.com/Casara/biblia-sublime/tree/0.3.2
[0.3.1]: https://github.com/Casara/biblia-sublime/tree/0.3.1
[0.3.0]: https://github.com/Casara/biblia-sublime/tree/0.3.0
[0.2.0]: https://github.com/Casara/biblia-sublime/tree/0.2.0
