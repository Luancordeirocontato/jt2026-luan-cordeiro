# Cartão do investimento — passo 8
# Para as 3 células-alvo da tese: Centro 1q, Centro 2q, Meia Praia 1q.
# Fórmulas:
#   Receita anual = ocupacao x R$/noite x 365            (bruta, sem custos)
#   Cap Rate      = Receita anual / preco de compra
#   Payback       = preco de compra / Receita anual = 1 / Cap Rate
# Valores de R$/noite e preço de compra vêm da tabela cruzada (células já filtradas/cortadas).
# RESSALVAS (não são "recomendação precisa", são limites da estimativa):
#   - Cap Rate short-stay, NÃO locação tradicional (receita Airbnb).
#   - Receita BRUTA, sem condomínio/IPTU/limpeza/taxas.
#   - Janela jan-abr (verão) superestima: valores são teto, não média anual.

import pandas as pd

raw = [
    # bairro, tipo, n_air, n_viv, rei/naite, preço, conf
    ('Centro', '1q',  78, 18, 471, 895_000, 'baixa-fina'),
    ('Centro', '2q',  65, 89, 611, 1_150_000, 'media'),
    ('Meia Praia', '1q', 28, 58, 495, 877_500, 'baixa'),
    ('Morretes', '2q', 51, 1_010, 500, 793_950, 'media'),
]

rows = []
for bairro, tipo, n_air, n_viv, preco_noite, preco_venda, conf in raw:
    for occ in (0.55, 0.70):
        rec = occ * preco_noite * 365
        cap = rec / preco_venda
        payback = 1 / cap
        rows.append({
            'bairro': bairro, 'tipo': tipo,
            'n_airbnb': n_air, 'n_vivareal': n_viv,
            'preco_noite_med': preco_noite,
            'preco_compra_med': preco_venda,
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
              'preco_compra_med','ocupacao','receita_anual_bruta',
              'cap_rate_pct','payback_anos','confianca']].to_string(index=False))