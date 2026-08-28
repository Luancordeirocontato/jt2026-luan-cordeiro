# Jovens Talentos AI Builder 2026 — Seazone | Itapema-SC

**Link do vídeo (3 min):** _preencher após gravar — https://drive.google.com/..._

## Recomendação em uma frase

Comprar **apartamentos de 1–2 quartos na faixa costeira de Itapema**, com preferência para
gestão profissional — priorizando **Meia Praia 1q** (retorno sólido + eficiência por m²),
**Morretes 2q** (upside de valor), e **Centro 2q** (estabilidade). A tese interna
"studios/1qto no Centro" **não se sustenta nos dados**.

## O que este repo entrega

- **Recomendação executiva** (sem código, para decisor): `reports/recomendacao_executiva.md`
- **Análise reproduzível** (notebook executado, com números): `analise/01_analise_principal.ipynb`
- **Metodologia e ressalvas**: `docs/metodologia.md`
- **Scripts auxiliares** (cap rate, deep-dive, cartão): `scripts/`

Responde as perguntas do desafio:
- Melhor perfil de imóvel: **apartamento de 1–2 quartos** (Cap Rate 10–16% vs ~8% dos 3q+)
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
eficiência → confiança → deep-dive → cartão). Todo o raciocínio e decisões metodológicas

## Como abrir (sem rodar nada)

- **Apresentação (HTML sem código, pronto pra tela):** [abrir `analise/apresentacao_sem_codigo.html`](analise/apresentacao_sem_codigo.html)
  — versão do notebook com só markdown, tabelas, gráficos e os mapas (sem células de código).
- **Mapa interativo (Cap Rate por bairro × tipo):** [abrir `analise/mapa_interativo.html`](analise/mapa_interativo.html)
  — mapa com os centroides dos bairros de Itapema, coloridos por Cap Rate (vermelho → amarelo → verde), com popup de bairro/tipo/Cap/nº imóveis.
- **Notebook interativo (nbviewer):** [abrir no nbviewer](https://nbviewer.org/github/Luancordeirocontato/jt2026-luan-cordeiro/blob/main/analise/01_analise_principal.ipynb)
  — o notebook executado renderiza o folium ao vivo e as imagens, sem precisar clonar o repo.

Para regenerar o HTML de apresentação: `py scripts/apresentacao.py` (gera `analise/apresentacao_sem_codigo.html`).
estão em `docs/metodologia.md` e o transcript da sessão em `ai-log/`.

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