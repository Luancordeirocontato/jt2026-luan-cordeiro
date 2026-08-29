# Jovens Talentos AI Builder 2026 — Seazone | Itapema-SC

**Link do vídeo (3 min):** _preencher após gravar — https://drive.google.com/..._

## Recomendação em uma frase

Comprar **apartamentos de 1–2 quartos na faixa costeira de Itapema**, com preferência para
gestão profissional — priorizando **Meia Praia 1q** (retorno sólido + eficiência por m²),
**Morretes 2q** (upside de valor), e **Centro 2q** (estabilidade). A tese interna
"studios/1qto no Centro" **não se sustenta nos dados**.

## O que este repo entrega

- **Recomendação executiva** (sem código, para decisor): [reports/recomendacao_executiva.md](reports/recomendacao_executiva.md)
- **Análise reproduzível** (notebook executado, com números): `analise/01_analise_principal.ipynb`
- **Metodologia e ressalvas**: `docs/metodologia.md`
- **Considerações finais** (o que eu faria com mais uma semana + como usei a IA): [no fim deste README](#considerações-finais) · lista completa na seção 7 do relatório
- **Scripts auxiliares** (cap rate, deep-dive, cartão): `scripts/`

Responde as perguntas do desafio:
- Melhor perfil de imóvel: **apartamento de 1–2 quartos** (Cap Rate 10–13% vs ~8% dos 3q+)
- Melhor localização em receita: **faixa costeira** (Meia Praia lidera; Morretes costeiro inclui)
- Características que explicam as melhores receitas: **gestão profissional (`is_professional`)**
  é o único sinal robusto (até +54% no R$/noite)
- O que comprar hoje: **cartão de investimento** no relatório (seção 1)
- Tese interna testada (a favor e contra): **não se sustenta** — "studio" quase não existe
  (116×2 no Centro) e o Centro não lidera retorno

## Dados

Snapshot estático do mercado de Itapema em `data/`, a mesma base para todos os candidatos:

| Arquivo | Conteúdo | Chave de ligação |
|---|---|---|
| `Details_Itapema.csv` | Anúncios Airbnb (título, reviews, rating, quartos, tipo) | listing |
| `Hosts_ids_Itapema.csv` | Anfitriões (reviews, anos, superhost) | `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Localização (lat/long + bairro) | listing |
| `Price_AV_Itapema.csv` | Preço por noite (por data de estadia/captura) | listing |
| `VivaReal_Itapema.csv` | Anúncios de venda (preço, condomínio, área) | mercado de compra |

## Como rodar

```bash
# 1. Ambiente (recomendado: Python 3.10+)
py -m venv .venv
# .venv\Scripts\activate  (Windows)
# source .venv/bin/activate  (Linux/macOS)
pip install -r requirements.txt

# 2. Executar a análise (do diretório raiz do repo)
py -m jupyter nbconvert --to notebook --execute --inplace analise/01_analise_principal.ipynb

# ou abrir interativamente
jupyter notebook analise/
```

O notebook executa de ponta a ponta (preparação → Cap Rate → sensibilidade →
ocupação diferencial → eficiência → confiança → deep-dive → cartão → mapas →
considerações finais). Todo o raciocínio e decisões
metodológicas estão em `docs/metodologia.md` e o transcript da sessão em `ai-log/`.

## Como abrir (sem rodar nada)

*Sobre os arquivos `.html`: o GitHub os mostra como código. Use o link "Ver online" (renderiza no navegador via raw.githack) ou baixe o arquivo ("Raw" → salvar) e abra no navegador.*

- **Recomendação executiva (leitura de 5 min, sem código):** [reports/recomendacao_executiva.md](reports/recomendacao_executiva.md)
  — resposta direta às 5 perguntas do desafio, com o cartão de investimento e a posição sobre a tese.
- **Apresentação (HTML sem código, pronto pra tela):**
  - [**Ver online** (renderizado)](https://raw.githack.com/Luancordeirocontato/jt2026-luan-cordeiro/main/analise/apresentacao.html)
  - [Ou **baixar arquivo** e abrir no navegador](analise/apresentacao.html)
  - versão do notebook com só markdown, tabelas, gráficos e os mapas (sem células de código).
- **Notebook completo (HTML com o código à vista):**
  - [**Ver online** (renderizado)](https://raw.githack.com/Luancordeirocontato/jt2026-luan-cordeiro/main/analise/notebook_completo.html)
  - [Ou **baixar arquivo** e abrir no navegador](analise/notebook_completo.html)
  - mesma análise da apresentação, mas com todas as células de código — para quem quiser
    conferir como cada número foi calculado sem rodar nada.
- **Mapa interativo (Cap Rate por bairro × tipo):**
  - [**Ver online** (renderizado)](https://raw.githack.com/Luancordeirocontato/jt2026-luan-cordeiro/main/analise/mapa_interativo.html)
  - [Ou **baixar arquivo** e abrir no navegador](analise/mapa_interativo.html)
  - mapa com os centroides dos bairros de Itapema, coloridos por Cap Rate (vermelho → amarelo → verde), com popup de bairro/tipo/Cap/nº imóveis.

Para regenerar os HTMLs: `py scripts/apresentacao.py` — executa o notebook e grava `analise/apresentacao.html` e `analise/notebook_completo.html` no mesmo passo.

## Estrutura

```
data/            CSVs brutos (imutáveis)
analise/         notebook principal de análise (executado)
scripts/         scripts auxiliares reproduzíveis
docs/            metodologia e notas técnicas
reports/         recomendação executiva (output final)
ai-log/          transcript da sessão (preenchido ao final do dia)
README.md        este arquivo
```

## Notas rápidas de leitura

- **Cap Rate é short-stay bruto** (sem custos operacionais) e **baseado em janela jan–abr
  (verão)**, que superestima a média anual. Trate os números como teto de cenário.
- A maior incerteza é a **ocupação real anual**; testamos 45–70% por perfil de bairro
  (premissa diferencial — veja o relatório, seção 5).

## Considerações finais

Esta seção espelha a **seção 11 da apresentação** (`analise/apresentacao.html`): a mesma
síntese, em texto aqui e em visual lá.

### O que eu faria com mais uma semana

Os três pontos que **mudariam a resposta**, não apenas a precisão decimal.

**1. Sair da premissa de ocupação.** Todo Cap Rate aqui depende da faixa assumida de
45–70% — a maior incerteza do trabalho e a única capaz de inverter o ranking de novo.
Os dados dão uma pista: o `Price_AV` traz até 3 capturas por par *(imóvel, data de
estadia)*, e uma data que some entre capturas provavelmente foi reservada.

**2. Cap Rate líquido, não bruto.** Condomínio (preenchido em 70,1% dos anúncios) e IPTU
(67,4%) estão na base e foram tratados como campo indisponível. Com eles, o retorno sai
de bruto para líquido em dois terços da amostra — e o payback real cresce.

**3. Regressão para o sinal invertido.** Superhost, rating e nº de reviews aparecem com
efeito negativo no deep-dive, o que tem mais cara de confundimento com gestão profissional
do que de descoberta. Uma regressão com controles diria qual dos dois é.

*Lista completa, com mais três itens de reforço de confiança, na seção 7 do relatório.*

### Como usei a IA no processo

Ao longo do dia, tratei a IA como parceira de raciocínio, não como executora. Trabalhei
majoritariamente pelo OpenCode com o DeepSeek, e usei o Claude Code numa segunda frente,
para revisão e acabamento — cada ferramenta virou um log próprio. Todos os logs completos
estão em `ai-log/`, um arquivo por sessão. Ali dá pra acompanhar iteração por iteração o
que foi pedido, o que a IA respondeu, e onde eu segurei o processo. Nesta seção do README,
quero destacar os momentos que mais moldaram a análise, porque foi neles que a colaboração
deu o melhor resultado.

O primeiro princípio que segui foi **não aceitar a primeira resposta**. Quando defini o
corte de volume mínimo por célula, a IA sugeriu N=20 e M=15 sem defesa clara. Em vez de
fixar esses números, pedi que ela calibrasse com os próprios dados — quantas células
sobreviveriam com cortes diferentes, e qual seria a cobertura de volume em cada cenário.
Só depois de ver essa tabela é que fechei o corte. Isso é uma bobagem numérica, mas foi um
sinal de método: qualquer chute que sobrevivesse à análise teria que passar pelo dado antes.

Esse mesmo princípio guiou o momento mais interessante do dia, que foi a **reincorporação
de Morretes**. A IA tinha descartado o bairro cedo, classificando como "interior" com base
em uma leitura superficial das coordenadas. Eu não estava convencido — olhei o mapa por
fora e vi que Morretes tem faixa litorânea. Pedi que rodasse a longitude imóvel a imóvel, e
descobrimos que 92% deles estão na mesma faixa costeira da Meia Praia. Com esse dado,
Morretes voltou ao ranking e virou uma das quatro células recomendadas. Se eu tivesse
aceitado a leitura inicial da IA, a análise teria perdido justamente a célula que mais
mostra o valor de rever premissas com base em evidência.

O terceiro momento onde a colaboração fez diferença foi no **deep-dive das características
que explicam receita**. A IA levantou dois fatores fortes num primeiro corte: gestão
profissional e reserva instantânea, ambos com efeito positivo. Poderia ter parado por aí —
dois fatores é bom, encaixa direto na narrativa da Seazone. Em vez disso, pedi um cross-tab
entre os dois, e o resultado inverteu a leitura: reserva instantânea sozinha (sem gestão
profissional) rendia até menos que a média, o que revelou que ela é só um sintoma de gestão
profissional, não um driver próprio. Reduzimos a recomendação a um único fator defensável,
mas ele é sólido.

Também insisti que a IA **não forçasse narrativas convenientes**. Ainda no deep-dive, o
"superhost" apareceu com efeito negativo em algumas células — imóveis com selo cobravam
menos que os sem selo. Seria fácil descartar o dado, ou inventar uma explicação. Preferimos
registrar como sinal inconsistente e deixar de fora da recomendação, com uma nota de que
isso mereceria uma regressão dedicada — algo que ficou fora do escopo de um dia. Fazer isso
é rigor, não fraqueza.

Ao final, **testei a IA contra ela mesma**. Pedi que avaliasse a análise inteira como se
fosse a banca, apontando o que criticaria. Ela levantou dois pontos válidos que eu ainda
não tinha visto com clareza: a célula principal (Meia Praia 1q) repousa em uma amostra
pequena (n=28 no lado Airbnb), e toda a inversão do ranking depende da premissa de ocupação
diferencial por bairro. Os dois viraram texto explícito no relatório — o primeiro em forma
de nota que recomenda validar com dados proprietários da Seazone antes de qualquer commit
de capital, e o segundo como o pilar defendido publicamente da metodologia.

Uma última coisa que deu certo foi a **auditoria numérica cruzada**. Durante a sessão,
rotinei validações independentes dos resultados que a IA me devolveu — quando ela dizia
"Morretes 2q rende 14%", eu rodava a conta separada e conferia. Isso pegou pelo menos um
erro pequeno de contagem no número de studios, que corrigimos antes de entrar no relatório.

No geral, o processo foi menos "a IA fez a análise" e mais "a análise nasceu do conflito
entre eu e a IA". Ela é rápida, é boa em varrer possibilidades e é excelente para gerar
código. Mas ela também é confiante demais, tende a defender a primeira hipótese, e passa
por cima de nuances quando ninguém segura. Meu papel foi segurar. E é esse trabalho — de
segurar, questionar, cruzar, refutar — que os arquivos em `ai-log/` mostram em detalhe.
