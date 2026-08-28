# Metodologia — notas fixas (referência para o relatório final)

## Métrica principal: Cap Rate short-stay
- **Fórmula:** (ocupação estimada × mediana de R$/noite do Airbnb × 365) ÷ preço de compra (VivaReal `sale_price`).
- **Métrica de checagem (C):** eficiência por m² = receita anual ÷ área útil (`usable_area`).
- **CONCEITO — atenção:** Cap Rate *short-stay* ≠ Cap Rate de locação tradicional. O
  `rental_price` do VivaReal está **100% nulo**; a "receita" vem do valor de curta
  temporada (Airbnb `Price_AV`), não de aluguel mensal de longo prazo. O número é um
  **retorno bruto de operação de temporada**, sem custos operacionais/condomínio/IPIU.

## Viés da janela temporal (jan–abr 2025)
- O `Price_AV` cobre apenas **105 dias: 2025-01-06 a 2025-04-20** (verão/março).
- Itapema é balneário de forte sazonalidade curta — esta janela captura o pico.
- **Qualquer receita anualizada a partir dessa janela tende a ser SUPER-estimada**
  (mais que a média anual real), porque o verão é caro e ocupado.
- Defesa no relatório: apresentar o Cap Rate como **estimativa de pico/verão** e,
  idealmente, mostrar um *cenário descontado* (ocupa real anual mais baixa) para não
  sobrevender o retorno. Não extrapolar a janela linearmente como se fosse o ano.

## Divisor de perímetro: localização (bairro)
- Coordenação entre Airbnb (Mesh) e Venda (VivaReal) **por nome de bairro**.
- Os vocabulários de bairro **divergem** entre as bases (ex.: "Jardim Praiamar" vs
  "Jardim Praia Mar"; há bairros só em um lado).
- A normalização é feita **sob supervisão humana** (mapa aprovado antes de aplicar) —
  não merge cego por string.
- **Merge consciente (aprovado):** `Meia Praia - Frente Mar` (VivaReal) → `Meia Praia`.
  O lado Airbnb (Mesh) não tem a granularidade "frente mar"; manter separado quebraria o
  join. **Perda consciente:** o efeito "primeira linha do mar / frente mar" fica invisível
  no lado Airbnb após o merge.
- **Outros mergers aprovados:** `Jardim Praiamar` ≡ `Jardim Praia Mar` (variante
  ortográfica); `Tabuleiro`/`Taboleiro` → `Tabuleiro dos Oliveiras`.
- **Órfãos excluídos do ranking pareado** (só existem em uma das bases):
  VivaReal: `Andorinha`, `Castelo Branco`, `Estreito`, `Itapema` (genérico), `Ocean Tower`;
  Airbnb: `Areal`, `Lameiro`, `Leopoldo Zarling`. Nota de transparência será incluída no
  relatório final. **`Sertaozinho` é distinto de `Sertao do Trombudo`** — não colapsar.

### Reincorporação de Morretes (revisão por longitude) — história do processo
- **Decisão inicial:** Morretes foi descartado do ranking por ser lido como "bairro de
  interior" (longitude a oeste, aparentemente longe da praia) e fora do alvo beira-mar da
  Seazone.
- **Revisão:** ao checar no mapa, Morretes tem faixa costeira. Reprocessamos a longitude
  dos listings Airbnb de Morretes: **92% dos imóveis (47 de 51) estão na faixa
  -48.616 a -48.609**, a MESMA borda costeira de Meia Praia. Apenas ~8% (4) são realmente
  interior, e esses poucos têm preço menor (median R$376 vs R$500).
- **Conclusão:** a leitura original ("Morretes = interior") era incorreta. O Cap de Morretes
  2q (14%) vem de imóveis **na faixa costeira compartilhada com Meia Praia**, não de imóveis
  de interior espurios. **Morretes 2q foi REINCORPORADO ao conjunto de células recomendadas**
  como opção viável, sem tratamento de "wildcard".
- **Ressalva honesta:** não é primeira linha de mar como parte de Meia Praia — os títulos
  do VivaReal indicam imóveis a ~300-600m da praia. Rendimento bom por **preço de compra
  mais baixo**, não por estar na praia.
- **Lição registrada:** exclusão de bairro por pré-noção cartográfica sem checagem por
  coordenada real pode descartar ativos bons. Este é um exemplo de revisão pelo dado.

### Ressalvas metodológicas (decisão de portfólio)
- **Confiança média metodológica ≠ menor risco de negócio.** "Confiança média" = volume
  suficiente nas duas bases; NÃO é resistência a choque de demanda. Morretes 2q tem o
  melhor Cap Rate, mas é o **mais exposto a choque de ocupação** (bairro a ~300-600m da
  praia, não primeira linha; sem marca consolidada).
- **Liquidez alta (1.010 anúncios VivaReal em Morretes) pode refletir OVERSUPPLY, não apenas
  facilidade de comprar/sair.** Oferta muito maior que a demanda de short-stay no bairro
  pode deprimir a ocupação média real.
- **Cap Rate alto + muita oferta de venda é sinal de possível market inefficiency**
  (mercado não precificando receita como sustentável), ou de receita sazonal irreal.
- **Suposição de ocupação única para todos os bairros é fraca** — sem dado real de
  ocupação, usamos premissas explícitas por perfil de bairro (sensibilidade diferencial).

## Escopo do ranking residencial (definição de produto)
- **Casas EXCLUÍDAS do ranking principal de Cap Rate.** Justificativa: em Itapema, casa é
  imóvel grande e caro (mediana casa 4q ≈ R$5,2M), não o produto de short-stay compacto da
  Seazone. O bin "casa" também é heterogêneo demais (sale_price varia ~9x de 2q p/ 4q).
  *Se sobrar tempo: apêndice separado de casas por nº de quartos para validar a exclusão.*
- **Excluídos de ambos os lados (não são residencial short-stay):** `hotel`, `terreno`,
  `comercial`, `outros` do `listing_type`/Details.

## Binagem de tipologia (apartamentos)
- `1qto` (inclui studios, `number_of_bedrooms` 0 ou 1), `2q`, `3q`, `4q+`.
- **FINDING (levar ao relatório/vídeo):** em Itapema *studio* quase não existe no lado
  Airbnb — no Centro há **116 de 1 quarto vs 2 studios** (global: 233 vs 38). A tese
  interna trata "studio/1qto" como sinónimos, mas os dados não sustentam "studio é a
  aposta" — sustentam **"1 quarto no Centro"**. (Este é um *achado*, não uma decisão de
  binagem.)

## Corte de volume das células (para ranking pareado)
- **Mínimos: N≥20 listagens Airbnb E M≥15 anúncios VivaReal por célula**
  `bairro × tipo` — calibrado sobre os dados (19 células sobrevivem; o corte pouca muda o
  volume, só remove células periféricas finas). Casa excluída, então aplica aos
  apartamentos.

## Guerra de outliers
- `sale_price` (até 44M), `monthly_condo_fee` (3,15M), `yearly_iptu` (2,8M),
  `usable_area` (até 188.000 m²) precisam de filtro de outliers antes de qualquer
  média/mediana, para não distorcer Cap Rate/m².