# Jovens Talentos AI Builder 2026 — Seazone | Itapema-SC

**Link do vídeo (3 min):** _preencher após gravar — https://drive.google.com/..._

## O que este repo entrega

Recomendação de investimento imobiliário em **Itapema (SC)**, derivada de dados de
mercado Airbnb + VivaReal. Responde:

- Qual perfil de imóvel maximiza retorno (tipologia, nº de quartos, tipo de anúncio)
- Melhor localização por receita
- Quais características explicam as melhores receitas
- O que a Seazone deveria comprar hoje + estimativa de retorno
- **Tese interna testada com dados:** "studios/1qto no Centro é a melhor aposta" — a favor e contra

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
# 1. Ambiente
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Análise (notebooks numerados na ordem de execução)
jupyter notebook
```

O pipeline completo (limpeza → junção → métricas → recomendação) roda na ordem
`notebooks/01_` → `02_` → `03_` → etc. Todo o raciocínio e decisões estão em `ai-log/`.

## Estrutura

```
data/            CSVs brutos (imutáveis)
notebooks/       análise reproduzível, numerada
ai-log/          conversas com IA (processo, lido pela banca)
outputs/         tabelas e gráficos gerados
README.md        este arquivo
```