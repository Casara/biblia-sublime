# Bíblia para o Sublime Text

Consulte versículos sem sair do Sublime Text: em várias traduções ao
mesmo tempo, com o original hebraico/grego, os números de Strong, os
sentidos dos dicionários e as passagens paralelas, e insira-os em
Markdown ou Typst prontos para citar. Feito para referências e traduções
em português (ARA, NVI, NAA...), mas inglês, espanhol e as outras
traduções da [Bíblia Online](https://www.bibliaonline.com.br) também
funcionam.

*Read this in [English](https://github.com/Casara/biblia-sublime/blob/main/README.md).*

Este pacote é a interface do [biblia-cli](https://github.com/Casara/biblia-cli)
para o Sublime Text e é desenvolvido lá; problemas e sugestões, lá
também.

## Requisito: o programa `biblia`

Quem faz cada consulta é o programa de linha de comando **`biblia`**,
que precisa ser instalado à parte. Sem ele, os comandos avisam
*executável não encontrado*.

1. **Baixe-o** na
   [página de versões](https://github.com/Casara/biblia-cli/releases/latest):
   - Linux: `biblia_<versão>_linux_amd64.tar.gz` (ou `arm64`);
   - macOS: `biblia_<versão>_darwin_arm64.tar.gz` (Apple silicon) ou
     `darwin_amd64` (Intel);
   - Windows: `biblia_<versão>_windows_amd64.zip`.

   Descompacte e ponha o `biblia` (`biblia.exe` no Windows) numa pasta
   que esteja no `PATH`, como `~/.local/bin`.

   Ou, com o Go instalado:
   `go install github.com/casara/biblia-cli/cmd/biblia@latest`.

2. **Confira** num terminal: `biblia jo 3.16` deve mostrar João 3.16.

3. **Opcional:** `biblia dados baixar` baixa o texto original, os
   dicionários e as passagens paralelas (cerca de 220 MB, ou 75 MB com
   `-enxuto`). Sem eles, a consulta de versículos funciona, mas os
   comandos de passagens paralelas não.

O pacote procura o `biblia` no `PATH` e depois em `~/.local/bin` e
`~/go/bin`, que o Sublime Text aberto pelo menu muitas vezes não
enxerga. Se estiver em outro lugar, informe o caminho completo na opção
`executavel`.

## Comandos

Todos estão na paleta de comandos (`Ctrl+Shift+P`, digite "Bíblia"):

| Comando | O que faz |
| --- | --- |
| **Bíblia: consultar referência selecionada** | mostra o texto numa janela, sem mexer no arquivo |
| **Bíblia: inserir texto no lugar da referência** | troca a referência selecionada pelo texto |
| **Bíblia: consultar…** | pergunta a referência e mostra o texto |
| **Bíblia: passagens paralelas da referência selecionada** | mostra o texto e a lista de passagens paralelas (citações do AT no NT, paralelos dos Evangelhos...) |
| **Bíblia: inserir o texto das passagens paralelas** | mantém a referência e insere, nas linhas seguintes, o texto de cada paralelo, dizendo o que ele é |

Sem seleção, vale a linha do cursor. As referências são escritas como no
Brasil: `Jo 3.16`, `1 Co 13.4-7`, `Rm 5.8; 6.23`, `Sl 23`.

## Atalhos

O pacote não ativa atalho nenhum. Os sugeridos, livres no Sublime Text e
nos atalhos comuns dos desktops, estão no keymap dele: abra
**Preferences › Package Settings › Bíblia › Key Bindings** (ou
*Preferences: Bíblia Key Bindings* na paleta) e copie-os para o seu
keymap, à direita, sem as barras de comentário:

```json
[
  { "keys": ["ctrl+alt+b"], "command": "biblia_consultar" },
  { "keys": ["ctrl+alt+shift+b"], "command": "biblia_inserir" },
  { "keys": ["ctrl+alt+l"], "command": "biblia_paralelos" },
  { "keys": ["ctrl+alt+shift+l"], "command": "biblia_inserir_paralelos" },
]
```

## Configurações

**Preferences › Package Settings › Bíblia › Settings**:

| Opção | Padrão | O que faz |
| --- | --- | --- |
| `executavel` | `biblia` | o programa, pelo nome ou pelo caminho completo |
| `versoes` | (vazio) | traduções separadas por vírgula (`ara,naa`); vazio usa o arquivo de configuração do programa |
| `formato` | `auto` | formato do texto inserido: `auto`, `linha`, `md`, `typ` ou um modelo seu |
| `formatos_por_extensao` | `.md` → `md`, `.typ` → `typ` | no `auto`: extensão do arquivo → formato; sem par, decide a sintaxe do arquivo (Markdown, Typst) |

No `auto`, arquivos Markdown recebem uma citação com a referência,
arquivos Typst recebem o `#bref(...)` precedido da linha
`// conferido: ARA · ... · data`, e os demais usam o `formato_filtro` do
programa. Os formatos, os campos dos modelos e o arquivo de configuração
do programa estão no
[README do biblia](https://github.com/Casara/biblia-cli/blob/main/README.pt-BR.md).

## Fontes e créditos

- **Texto bíblico:** [Bíblia Online](https://www.bibliaonline.com.br),
  pelo serviço que o site publica para programas, até 5 versículos por
  consulta. Cada tradução tem seus titulares de direitos; nem o pacote
  nem o programa trazem texto bíblico.
- **Original, léxicos e gramática:** [STEPBible](https://www.stepbible.org)
  (Tyndale House, Cambridge, CC BY 4.0), baixados sob demanda.
- **Dicionários e passagens paralelas:** Sociedade Bíblica Unida
  ([ubs-open-license](https://github.com/ubsicap/ubs-open-license), CC
  BY-SA 4.0), baixados sob demanda.

## Licença

MIT. Os dados mantêm as licenças das suas fontes.
