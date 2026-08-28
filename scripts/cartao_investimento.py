# Cartão do investimento — passo 8
# Para as 4 células do ranking: Centro 1q, Centro 2q, Meia Praia 1q, Morretes 2q.
# Fórmulas:
#   Receita anual = ocupacao x R$/noite x 365            (bruta, sem custos)
#   Cap Rate      = Receita anual / preco de compra
#   Payback       = preco de compra / Receita anual = 1 / Cap Rate
# Valores de R$/noite e preço de compra vêm da tabela cruzada (células já filtradas/cortadas).
# OCUPAÇÃO: diferencial por perfil de bairro, a mesma premissa da seção 5b do
# notebook e do relatório executivo. Não é a faixa simétrica 55/70% usada como
# referência na seção 4 (essa fica em scripts/cap_rate.py).
# RESSALVAS (não são "recomendação precisa", são limites da estimativa):
#   - Cap Rate short-stay, NÃO locação tradicional (receita Airbnb).
#   - Receita BRUTA, sem condomínio/IPTU/limpeza/taxas.
#   - Janela jan-abr (verão) superestima: valores são teto, não média anual.
#   - As faixas de ocupação são leitura de mercado, não saem dos dados.

import pandas as pd

# Faixa de ocupação (baixa, alta) por perfil de bairro:
#   beira-mar consolidado sustenta ocupação maior que bairro periférico.
OCC_DIFF = {
    'Meia Praia': (0.60, 0.65),   # beira-mar consolidado, demanda estabelecida
    'Centro':     (0.55, 0.60),   # turístico consolidado
    'Morretes':   (0.45, 0.55),   # periférico, ~500m da praia, oferta grande
}

raw = [
    # bairro, tipo, n_air, n_viv, R$/noite, preço de compra, confiança
    ('Centro', '1q',  78, 18, 471, 895_000, 'baixa-fina'),
    ('Centro', '2q',  65, 89, 611, 1_150_000, 'media'),
    ('Meia Praia', '1q', 28, 58, 495, 877_500, 'baixa'),
    ('Morretes', '2q', 51, 1_010, 500, 793_950, 'media'),
]

rows = []
for bairro, tipo, n_air, n_viv, preco_noite, preco_venda, conf in raw:
    for cenario, occ in zip(('faixa baixa', 'faixa alta'), OCC_DIFF[bairro]):
        rec = occ * preco_noite * 365
        cap = rec / preco_venda
        payback = 1 / cap
        rows.append({
            'bairro': bairro, 'tipo': tipo,
            'n_airbnb': n_air, 'n_vivareal': n_viv,
            'preco_noite_med': preco_noite,
            'preco_compra_med': preco_venda,
            'cenario': cenario,
            'ocupacao': f'{int(occ*100)}%',
            'receita_anual_bruta': rec,
            'cap_rate': cap,
            'payback_anos': payback,
            'confianca': conf,
        })

cartao = pd.DataFrame(rows)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
# cap_rate e payback sao proporcoes/razao; exibir com notacao amigavel
cartao['cap_rate_pct'] = cartao['cap_rate'] * 100
cartao['payback_anos'] = cartao['payback_anos'].round(1)
print(cartao[['bairro','tipo','n_airbnb','n_vivareal','preco_noite_med',
              'preco_compra_med','cenario','ocupacao','receita_anual_bruta',
              'cap_rate_pct','payback_anos','confianca']].to_string(index=False))