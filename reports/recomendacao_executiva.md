# Recomendação Executiva — Investimento short-stay em Itapema (SC)

**Análise de 2026-08-28 · Jovens Talentos AI Builder 2026 · Seazone**

---

## Resumo em 1 minuto

Itapema comporta **uma aposta principal viável** para o modelo short-stay da Seazone: **apartamentos de 1 quarto na Meia Praia**. Em segundo lugar de aporte de valor, **apartamentos de 2 quartos em Morretes** oferecem o maior retorno potencial condicionado à ocupação. A tese interna "studios/1qto no Centro é a melhor aposta" **não se sustenta nos dados**.

---

## 1. O que comprar hoje (ordem de prioridade)

| Prioridade | Célula | Preço compra mediano | R$/noite | Receita bruta* | Cap Rate* | Payback* | Confiança |
|---|---|---|---|---|---|---|---|
| **1ª · aposta principal** | **Meia Praia 1q** | ~R$878k | R$495 | R$99k–R$127k | **11,3%–14,4%** | 6,9–8,8 anos | baixa |
| **2ª · upside** | **Morretes 2q** | ~R$794k | R$500 | R$100k–R$128k | 10,3%–16,1% | 6,2–7,9 anos | média |
| **3ª · mais segura** | **Centro 2q** | ~R$1,15M | R$611 | R$123k–R$156k | 10,7%–13,6% | 7,4–9,4 anos | média |
| Fora | Centro 1q | ~R$895k | R$471 | R$95k–R$120k | 10,6%–13,4% | 7,4–9,5 anos | baixa-fina |

\* Receita e Cap Rate são **brutos** e apresentados nas faixas de ocupação por perfil de bairro: **45–70% para Morretes** (inclui o cenário pessimista de ocupação real mais baixa), **55–70% para os demais**. Cap Rate = receita anual ÷ preço de compra. Janela de preço é verão (jan–abr), o que **superestima** — ver Seção 5.

\** **Nota sobre Centro 1q vs Centro 2q:** os Cap Rates são próximos (10,6–13,4% vs 10,7–13,6%) — a distinção **não** é de retorno, e sim de **confiança de dados** (Centro 1q tem apenas 18 anúncios de venda contra 89 do Centro 2q) e do fato de Centro 1q ser exatamente a tese interna que os dados refutam.

### Por que esta ordem (premissa diferencial)

- **Meia Praia 1q (1ª):** melhor **eficiência por m²** da cidade (R$2.710/m²/ano a 60% de ocupação — a maior), beira-mar consolidado, maior demanda e ocupação sustentável (estimada 60–65% vs 45–55% de Morretes). No cenário de ocupação **diferencial por perfil de bairro**, é o que lidera (Cap 12,4%–13,4%). É também o mais alinhado à marca Seazone (beira-mar, produto de temporada).
- **Morretes 2q (2ª · upside):** melhor Cap **potencial** (até 16,1% a 70% de ocupação) e preço de compra ~10% menor. **Mas**: a 300–600m da praia (não primeira linha), bairro mais periférico, com ocupação real provável menor. No cenário diferencial cai para 10,3%–12,6% (abaixo da Meia Praia). Entra como **opção de valor**, não como líder.

  *Seleção dentro do bairro:* dentro de Morretes 2q, imóveis na faixa mais oriental (litoral, mesma longitude de Meia Praia) rendem ~R$550/noite mediano vs ~R$400 no subgrupo mais interior — diferença de ~37%. Isso é insight de seleção prática: dentro do bairro, priorizar a compra na faixa costeira. Não refinamos o Cap Rate porque o VivaReal não tem coordenadas por anúncio, então a estimativa de compra fica para o Morretes inteiro.
- **Centro 2q (3ª · segura):** o Cap Rate (10,7–13,6%) é quase igual ao de Centro 1q — a diferença **não é retorno**. Entra na recomendação por **confiança de dados** bem melhor (89 anúncios de venda vs 18) e pelo sinal forte de **gestão profissional** (+54% de R$/noite quando `is_professional` — o mais forte de todas as células). Boa opção se a prioridade for estabilidade e operação madura.
- **Centro 1q (FORA):** o Cap Rate (10,6–13,4%) é quase idêntico ao Centro 2q, mas duas coisas tiram ele da recomendação. Primeiro: a confiança de dados é a mais baixa das quatro células (apenas 18 anúncios de venda no VivaReal, contra 89 do Centro 2q). Segundo, e mais importante: essa célula **é** a tese interna "studio/1qto no Centro" que estamos testando — e os dados mostram que ela não lidera em nenhuma métrica. Manter ela na recomendação seria confirmar a tese que os próprios dados refutam.

---

## 2. Posição sobre a tese interna

**Tese testada:** *"studios/1qto no Centro é a melhor aposta."*

**Veredicto: NÃO se sustenta nos dados — em dois níveis.**

1. **O recorte "studio" quase não existe em Itapema.** No Centro há **116 apartamentos de 1 quarto vs apenas 2 studios**. A tese trata "studio/1qto" como sinônimos, mas o mercado itapemense é de **1 quarto**, não de studio.
2. **O Centro não é o melhor retorno.** Meia Praia 1q e Morretes 2q superam o Centro (em Cap, eficiência ou risco). O Centro 1q tem ainda a menor confiança de dados.

**O que os dados SUSTENTAM:** a direção da tese ("compacto rende mais que grande") está correta — apartamentos de 1–2 quartos têm retorno superior a 3q/4q+ (10–14% vs ~8%), e **1 quarto** é o mais eficiente por m². Mas a localização vencedora é a **faixa costeira consolidada (Meia Praia)**, não o Centro.

---

## 3. Características que explicam as melhores receitas

Testamos, dentro dos compactos da beira-mar, quais características separam os imóveis que conseguem R$/noite maior:

| Característica | Efeito no R$/noite | Veredicto |
|---|---|---|
| **Gestão profissional (`is_professional`)** | **+25% a +54%** | ✅ **Única defensável** — priorize |
| Reserva instantânea (`can_instant_book`) | +31% isolado, mas sem prêmio próprio quando profissional | ⚠️ Proxy do profissional (não recomendação separada) |
| Superhost | inconsistente (às vezes −14%/−25%) | ⚠️ Sinal invertido — precisa análise mais profunda |
| Star rating ≥ 4.8 | inconsistente (Centro 2q −27%, Meia Praia 1q +48%) | ⚠️ Mesmo tratamento |
| Nº de reviews ≥ 20 | inconsistente (Centro 2q −46%) | ⚠️ Mesmo tratamento |

**Recomendação prática:** no perfil compacto, **priorize imóveis operáveis por gestão profissional** — o que combina com o modelo da Seazone (adquire e opera). Superhost/rating não passaram no teste; aparecem como sinal inconsistente que exigiria regressão para interpretar (fora do escopo de 1 dia).

---

## 4. Transparência de processo (o que foi validado e revisado)

- **Normalização de bairros** manual e supervisionada. Contagens **brutas (pré-normalização)**: 15 nomes distintos no Airbnb, 25 no VivaReal — que colapsam para ~12 bairros pareados após tratar variações ortográficas e caixa (ex.: "MEIA PRAIA"/"Meia praia"/"meia praia" → Meia Praia). Órfãos (5 do VivaReal: Andorinha, Castelo Branco, Estreito, Itapema genérico, Ocean Tower; 3 do Airbnb: Areal, Lameiro, Leopoldo Zarling) foram **excluídos do ranking pareado** por falta de dado do outro lado; representam oferta em bairros sem contraparte de preço de compra.
- **Reincorporação de Morretes (revisão importante):** Morretes foi primeiro descartado por ser lido como "interior". Ao checar por **longitude** dos listings, **92% dos imóveis (47 de 51) estão na faixa costeira compartilhada com Meia Praia** (‑48.616 a ‑48.609); o preço/noite sobe do interior (R$402) para a costa (R$550), mas a mediana do bairro inteiro (R$498) sustenta o perfil — **a célula foi reincorporada como opção válida**, sem tratamento especial. Não são primeira linha (300–600m do mar).
- **Duas visões de ocupação** são reportadas (Seção 5): a **simétrica** (70% para todos) faz Morretes liderar; a **diferencial** (por perfil de bairro, mais realista) faz Meia Praia liderar. **A recomendação segue a diferencial**, porque nenhum analista assumiria mesma ocupação para bairro de primeira linha e bairro a 600m da praia.

---

## 5. Limitações e premissas (leia antes de decidir)

**A maior incerteza é a ocupação real anual.** Não temos dado de ocupação observada (só preço de diária cotado e preço de venda). Assumimos, por perfil:

| Bairro | Ocupação assumida (realista) |
|---|---|
| Meia Praia (beira-mar) | 60–65% |
| Centro (consolidado) | 55–60% |
| Morretes (~600m da praia) | 45–55% |

**O que este modelo NÃO captura (limitações):**
- **Cap Rate é short-stay, não locação tradicional** — receita de curta temporada, com sazonalidade e volatilidade próprias.
- **Receita bruta** — NÃO descontam condomínio, IPTU, limpeza, utilities, taxas da plataforma, manutenção. O payback real (líquido) é maior que o reportado.
- **Janela jan–abr (verão) superestima receita anual** — os Cap Rates são **teto de verão**, não média anual.
- **Condição real do imóvel, condomínio, IPTU** não entram (campos parciais no VivaReal).
- **Financiamento/alavancagem** não modelados — tudo é capital próprio.
- **Regulação de locação de curta temporada** em Itapema não avaliada.
- **Oversupply:** Morretes tem 1.010 anúncios de venda — liquidez alta, mas oferta grande pode pressionar ocupação.
- **Confiança de dados ≠ risco de negócio:** "média/baixa" refere-se a volume de dados, não a segurança do investimento.

---

## 6. Próximos passos sugeridos pela Seazone

1. Validar ocupação real de Itapema com dados proprietários da Seazone (o insumo que mais muda a resposta).
2. Simular **3 imóveis-alvo** (1 Meia Praia 1q, 1 Morretes 2q, 1 Centro 2q) com custos reais (condomínio+IPTU+gestão) para checar o retorno líquido.
3. Verificar regulação de short-stay em Itapema/SC antes de estruturar a compra.
4. Usar `is_professional` como critério de aquisição/parceria com gestoras locais.

---

*Reproduzível em `analise/01_analise_principal.ipynb` · metodologia e ressalvas em `docs/metodologia.md`.*