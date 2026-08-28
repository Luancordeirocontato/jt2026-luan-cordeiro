# AI log — sessão Claude (Claude Code / Opus 5)

**Data:** 2026-08-28
**Projeto:** Jovens Talentos AI Builder 2026 — Seazone · Itapema-SC
**Escopo da sessão:** revisão de consistência analítica e acabamento visual dos
entregáveis em HTML. Nenhum número da análise foi recalculado por decisão da IA —
as premissas e os resultados vêm do trabalho anterior; o que mudou foi **como**
eles aparecem e **onde** o notebook contradizia o relatório.

**Commits gerados:**

| Hash | Assunto |
|---|---|
| `5a792b6` | resolve inconsistência: adiciona seção de ocupação diferencial |
| `0c6bb22` | tipografia dos HTMLs: Playfair Display + Bebas Neue + Inter/Lato |
| `18c484f` | legibilidade das tabelas: cabeçalho nítido, números pt-BR, fim do MathJax |
| `b94dc76` | matriz do deep-dive (seção 8): paleta suave e cabeçalho de uma linha |

---

## 1. Leitura inicial do repositório

Pedido: ler a pasta e entender o projeto.

A IA mapeou a estrutura (`data/`, `analise/`, `scripts/`, `docs/`, `reports/`) e
leu `README.md`, `reports/recomendacao_executiva.md` e `docs/metodologia.md`.

Resumo do que foi entendido, para registro:

- Tese entregue: comprar compactos (1–2 quartos) na faixa costeira, na ordem
  Meia Praia 1q → Morretes 2q → Centro 2q.
- Tese interna refutada: "studios/1qto no Centro" — studio quase não existe
  (116 de 1 quarto contra 2 studios no Centro) e o Centro não lidera retorno.
- Único sinal robusto de receita: `is_professional` (+25% a +54% no R$/noite).

Pendências apontadas na leitura: link do vídeo ainda em branco no `README.md`
e a pasta `ai-log/` vazia, apesar de citada como entregável.
**Este arquivo resolve a segunda.**

---

## 2. Inconsistência entre o notebook e o relatório

### O problema (levantado pelo autor, não pela IA)

O notebook, nas seções 4 e 5, calculava o Cap Rate com **ocupação simétrica**
(a mesma para todos os bairros) e afirmava textualmente que *"o ranking é estável
à ocupação"*, com **Morretes 2q** como vencedor absoluto. O relatório executivo
recomenda **Meia Praia 1q**, porque aplica **ocupação diferencial por perfil de
bairro**. Quem lesse os dois documentos em sequência veria uma contradição.

A raiz é conceitual e vale registrar: o ranking por `k = R$/noite × 365 ÷ preço`
é de fato invariante à ocupação **enquanto a ocupação for a mesma para todos**.
A frase "o ranking é estável à ocupação" era verdadeira dentro daquela premissa e
enganosa fora dela. Ocupação diferente por bairro deixa de ser um fator de escala
comum e passa a reordenar as células.

### O que foi feito

Nova **seção 5b — "Ocupação diferencial por perfil de bairro (visão realista)"**,
inserida entre a 5 e a 6, sem renumerar as seguintes. Contém:

- o texto explicando por que a premissa simétrica é fraca (Meia Praia é beira-mar
  consolidado; Morretes fica a ~500m da praia e tem 1.010 anúncios de venda no
  VivaReal, sinal de oversupply);
- as faixas assumidas — Meia Praia 60–65%, Centro 55–60%, Morretes 45–55% —
  com a ressalva explícita de que **não vêm dos dados, e sim de leitura de mercado**;
- uma tabela ordenada pelo Cap diferencial da faixa alta;
- duas linhas impressas que tornam a inversão explícita:

  ```
  Lider sob ocupacao simetrica  : morretes 2q
  Lider sob ocupacao diferencial: meia praia 1qto
  ```

O texto da seção 5 foi corrigido para não afirmar mais estabilidade sem
qualificação, e agora aponta para a 5b.

Os números da 5b batem exatamente com o relatório: Meia Praia 1q 12,4–13,4%,
Morretes 2q 10,3–12,6%, Centro 2q 10,7–11,6%, Centro 1q 10,6–11,5%.

### Sobreposição de rótulos no mapa estático

No mesmo pedido, o autor mostrou um print em que os rótulos do mapa estático se
sobrepunham entre si e à legenda. A causa era um offset **fixo** `(8, 6)` para
todos os rótulos: células do mesmo bairro compartilham praticamente o mesmo
centroide, então os textos empilhavam.

Solução: declutter com detecção de colisão em pixels. Marcadores e a caixa da
legenda entram como regiões ocupadas; cada rótulo, na ordem decrescente de Cap
Rate (o vencedor escolhe primeiro), recebe o primeiro de 12 offsets candidatos
que não colide. Rótulos afastados ganham linha-guia até o ponto e todos têm
fundo branco semitransparente.

---

## 3. Tipografia dos HTMLs

Pedido: Playfair Display nos títulos, Bebas Neue nos destaques de impacto,
Inter/Lato no corpo.

**Decisão de implementação:** a troca foi feita nos **geradores**
(`scripts/apresentacao.py`, `scripts/map_cell.py`, `scripts/template_sem_codigo.tpl`)
e não nos HTMLs de saída, para sobreviver ao próximo
`py scripts/apresentacao.py`. Editar o HTML gerado teria funcionado uma vez e
sumido na regeneração seguinte.

| Papel | Fonte | Onde |
|---|---|---|
| Títulos | Playfair Display | `h1`, `h2`, `h3` |
| Destaque | Bebas Neue | cabeçalho de tabela, Cap Rate nos popups do mapa, escala da legenda, classe `.impacto` |
| Corpo | Inter → Lato | `p`, `li`, `td`, blockquote |

Código e saída de terminal seguem monoespaçados de propósito.

### Dois detalhes que exigiram cuidado

- **Bebas Neue só tem o peso 400.** O `th` estava em `font-weight: 700`, o que
  produziria bold sintético (borrado). Foi para 400, compensado com caixa alta,
  tracking e corpo maior.
- **`--jp-content-font-family` do nbconvert vencia a regra do `body`.** Na
  primeira rodada os títulos e cabeçalhos já estavam certos, mas `p`, `li` e `td`
  continuavam em `system-ui`. Foi preciso sobrescrever a própria variável do
  Jupyter. Detectado por verificação no browser, não a olho.

Fallbacks para leitura offline: Georgia (título), Arial Narrow (impacto),
Segoe UI (corpo).

---

## 4. Legibilidade das tabelas

Pedido: cabeçalhos embaçados e a coluna "Receita anual bruta" ilegível, em outra fonte.

### 4.1 Cabeçalhos embaçados

Bebas Neue a 15px, em branco sobre fundo escuro, fica fino e "lava" no
antialiasing. Como a fonte não tem peso acima de 400, engrossar com bold não era
opção. Corrigido pelo corpo e pela renderização: 17px, tracking de 0,055 para
0,045em, `subpixel-antialiased`, `optimizeLegibility` e `font-synthesis: none`.

### 4.2 A coluna em serif itálico — não era fonte, era MathJax

Diagnóstico que mudou completamente a solução. A string era
`R$ 108.405 a R$ 117.439`, com **dois cifrões**. O MathJax embutido pelo nbconvert
lê `$...$` como delimitador de LaTeX inline, capturou `108.405 a R` e tipografou o
trecho como matemática — daí o `R108,405aR` em serif itálico que aparecia no print.

Solução: helper `brl_faixa()` que usa **um único cifrão** —
`R$ 108.405 a 117.439`. Verificado depois que
`document.querySelectorAll('mjx-container').length === 0` na página inteira.

Registro da lição: em relatório em português gerado por nbconvert, qualquer célula
com dois `R$` é candidata a virar equação sem aviso.

### 4.3 Números em padrão brasileiro (ajuste adjacente ao pedido)

Os valores saíam no padrão inglês — `R$ 877,500` e `12.4%` — que num documento em
português se lê como *877 reais e 50 centavos*. Foram criados os helpers
`num_br` / `brl` / `pct_br` na célula de helpers e aplicados em todas as tabelas.

### 4.4 Bug encontrado durante a verificação (fora do pedido)

A regra `table.no-index th:first-child { display: none }` estava escondendo a
**primeira coluna de dados de todas as tabelas** do HTML de apresentação: o `#`
do ranking em cinco delas e a coluna `Recomendação` — com os fundos verde, oliva,
dourado e cinza do 1º/2º/3º/Fora — no cartão do investimento.

A regra existia para esconder o índice do pandas, mas todos os `display()` já usam
`Styler.hide(axis='index')`, que remove o índice no próprio HTML. Auditadas as 11
tabelas: nenhuma sai com `<th>` vazio à esquerda, então a regra só tinha coluna
real para consumir. Removida.

Foi notado porque a tabela do print começava em "BAIRRO / TIPO" — a coluna de
prioridade, que é o ponto do cartão, nunca havia aparecido no HTML.

---

## 5. Matriz do deep-dive (seção 8)

Pedido em seis itens: cores menos saturadas, cabeçalho de uma linha, caixa normal,
fundo neutro para sinal fraco, mais respiro vertical, números maiores e semibold.

| Item | Antes | Depois |
|---|---|---|
| Cores | verde `#138a4f` / vermelho `#c0452e`, texto branco | mint `#d6efe0` / salmão `#fadfd7`, texto escuro |
| Cabeçalho | 3 faixas (`CELULA` e `CARAC` quase vazias) | 1 faixa, só os bairros |
| Caixa | `IS_PROFESSIONAL`, `CENTRO 1QTO` | `is_professional`, `Meia Praia 1qto` |
| Sinal fraco | pastel colorido | cinza neutro `#f2f1ed` |
| Respiro | linhas coladas | padding 15px + 3px de vão |
| Números | herdados do corpo | Inter 15px semibold, tabulares |

**Origem da caixa alta:** não vinha do notebook. Era a regra global de `th`
(Bebas Neue + `text-transform: uppercase`) introduzida no item 3 desta mesma
sessão. Boa nas tabelas de ranking, atropelava a matriz, onde os rótulos são nomes
de campo. Resolvido com a classe `.deep-dive`, que devolve a fonte de corpo em
caixa normal apenas ali. Os rótulos de coluna usam `.capitalize()` por palavra e
não `.title()`, que transformaria `1qto` em `1Qto`.

### Dois ajustes que surgiram da verificação

- **`-5%` estava pintado de salmão.** O valor real é −5,4%: exibia `-5%`, dentro
  da faixa de ruído, mas era colorido como sinal forte. O teste passou a comparar
  o valor **arredondado**, o mesmo que o leitor vê. É justamente o
  `is_professional` no Centro 1qto — a célula fraca da linha mais importante da
  matriz.
- **Contraste do cinza.** O primeiro tom escolhido dava 3,04:1, abaixo do mínimo
  WCAG AA. Escurecido para `#6f6a5e` (4,77:1), continuando recuado em relação às
  células com sinal.

Contrastes finais: mint 6,61 · salmão 6,05 · cabeçalho 6,41 · rótulos de linha
14,19 · ruído 4,77. Todos em AA.

Os estilos estruturais foram duplicados no `Styler.set_table_styles` para a tabela
sair correta também no notebook e no nbviewer, onde o CSS de
`scripts/apresentacao.py` não é aplicado.

---

## 6. Como o trabalho foi verificado

Registro do método, já que o critério do desafio inclui uso responsável de IA:

- **Helpers de formatação** testados isoladamente antes de entrar no notebook
  (`brl(877500)` → `R$ 877.500`, `pct_br(0.134)` → `13,4%`).
- **Notebook reexecutado de ponta a ponta** a cada mudança, via
  `scripts/apresentacao.py`, que executa e regenera o HTML no mesmo passo.
- **Verificação no browser por DOM computado**, não a olho: famílias de fonte
  efetivamente aplicadas por elemento, contagem de linhas de cabeçalho,
  `text-transform`, cores de fundo por célula, contagem de `mjx-container` e
  razões de contraste calculadas.
- **Mapa estático** conferido por imagem depois do declutter, com os 8 rótulos
  legíveis e sem colisão com a legenda.

O painel de navegador não ficou visível no fim da sessão, então a validação da
seção 8 foi feita só por DOM, e isso foi comunicado em vez de afirmar conferência
visual.

---

## 7. Pendências deixadas em aberto

1. **Popup do mapa conta cotações, não imóveis.** Em `scripts/map_cell.py` a
   agregação usa `n=('airbnb_listing_id', 'count')` sobre uma base com uma linha
   por listing × data de preço; o correto seria `nunique()`. Por isso o popup de
   Meia Praia 1qto diz "3494 imóveis". O raio do marcador satura em `min(n, 60)`,
   então visualmente não aparece — só o texto está inflado. Levantado pela IA,
   não corrigido por estar fora do escopo pedido.
2. **Link do vídeo** ainda em branco no `README.md`.
3. **`analise/apresentacao_bruta.html`** é resíduo de uma versão anterior do
   pipeline e está fora do controle de versão; vale um `.gitignore`.

---

## 8. Divisão de trabalho nesta sessão

- **Direção, diagnóstico de negócio e critérios visuais:** do autor. A
  inconsistência entre notebook e relatório, a especificação da seção 5b
  (título, texto, colunas da tabela, ordenação) e os seis itens da matriz do
  deep-dive vieram prontos no pedido.
- **Execução, investigação de causa-raiz e verificação:** da IA. As causas do
  serif itálico (MathJax), da coluna sumida (`no-index`), do borrão no cabeçalho
  (Bebas Neue sem peso 700) e do `p` em `system-ui`
  (`--jp-content-font-family`) foram diagnosticadas na sessão, não relatadas
  pelo autor — que reportou apenas os sintomas visíveis.
- **Achados fora do pedido** (coluna `Recomendação` oculta, `-5%` mal colorido,
  contraste abaixo de AA, popup do mapa) foram comunicados explicitamente, com
  a distinção entre o que foi corrigido e o que ficou em aberto.
