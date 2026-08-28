# Cap Rate short-stay por bairro x tipologia (métrica A)
# O que esta saída permite concluir:
#  - Ranking de retorno bruto anual (%) por célula bairro x tipo (apartamentos),
#    respondendo as perguntas a/b/d do desafio.
#  - Ver se o vencedor é estável e se o "1qto no Centro" se destaca.
#  - Ancorar o que comprar em retorno sobre o preço de compra.
# METODOLOGIA (docs/metodologia.md):
#  - Cap Rate = ocupacao x mediana(R$/noite) x 365 / mediana(sale_price)
#  - Janela jan-abr(2025) superestima receita; ocupacao é cenário (50/60/70%).
#  - Casas/hotel/terreno/comercial/outros excluídos. Corte N>=20 E M>=15.

import pandas as pd
import unicodedata

def norm(s):
    if not isinstance(s, str):
        return s
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().strip().lower()

mergers = {
    'jardim praiamar': 'jardim praia mar',
    'meia praia - frente mar': 'meia praia',
    'taboleiro': 'tabuleiro dos oliveiras',
    'tabuleiro': 'tabuleiro dos oliveiras',
}
def canonic(s):
    return mergers.get(norm(s), norm(s))

def bin_tip(nb):
    if nb <= 1:
        return '1qto'
    if nb == 2:
        return '2q'
    if nb == 3:
        return '3q'
    return '4q+'

def filtro_outliers(df, col, q_lo=0.01, q_hi=0.99):
    lo, hi = df[col].quantile([q_lo, q_hi])
    return df[(df[col] >= lo) & (df[col] <= hi)]

def main():
    # ---- Lado Airbnb: bairro + tipologia + R$/noite ----
    D = pd.read_csv('data/Details_Itapema.csv', encoding='utf-8',
                    usecols=['airbnb_listing_id', 'number_of_bedrooms', 'listing_type'])
    M = pd.read_csv('data/Mesh_Ids_Data_Itapema.csv', encoding='utf-8',
                    usecols=['airbnb_listing_id', 'suburb'])
    M = M[M['suburb'].str.lower() != 'none'].dropna(subset=['suburb'])
    M['bairro'] = M['suburb'].map(canonic)
    P = pd.read_csv('data/Price_AV_Itapema.csv', encoding='utf-8',
                    usecols=['airbnb_listing_id', 'price'])
    air = D.merge(M[['airbnb_listing_id', 'bairro']], on='airbnb_listing_id', how='inner')
    air = air.merge(P, on='airbnb_listing_id', how='inner')
    air = air[air['listing_type'] == 'apartamento']
    air['tipo'] = air['number_of_bedrooms'].map(bin_tip)

    contagens = air.groupby(['bairro', 'tipo'])['airbnb_listing_id'].nunique().rename('n_airbnb')
    receita = air.groupby(['bairro', 'tipo'])['price'].median().rename('price_med_noite')

    # ---- Lado VivaReal: bairro + tipologia + preco de compra ----
    v = pd.read_csv('data/VivaReal_Itapema.csv', encoding='utf-8',
                    usecols=['suburb', 'bedrooms', 'listing_type', 'sale_price', 'usable_area'])
    v = v[v['listing_type'] == 'apartamento']
    v = v[v['sale_price'] > 0]
    v = v.dropna(subset=['suburb'])
    v['bairro'] = v['suburb'].map(canonic)
    v['tipo'] = v['bedrooms'].map(bin_tip)
    v = filtro_outliers(v, 'sale_price')

    nviv = v.groupby(['bairro', 'tipo']).size().rename('M_vivareal')
    prec = v.groupby(['bairro', 'tipo'])['sale_price'].median().rename('sale_price_med')

    # ---- junta ----
    tab = pd.DataFrame({'price_med_noite': receita, 'sale_price_med': prec, 'M_vivareal': nviv})
    tab = tab.merge(contagens, on=['bairro', 'tipo'], how='left').reset_index()
    tab = tab[(tab['n_airbnb'] >= 20) & (tab['M_vivareal'] >= 15)]

    # k = receita nominal independente de ocupacao: (R$/noite * 365)/sale_price
    tab['k'] = tab['price_med_noite'] * 365 / tab['sale_price_med']
    for occ in [0.5, 0.6, 0.7]:
        tab[f'cap_{int(occ*100)}'] = tab['k'] * occ

    tab = tab.sort_values('cap_50', ascending=False)
    cols = ['bairro', 'tipo', 'n_airbnb', 'M_vivareal', 'price_med_noite',
            'sale_price_med', 'cap_50', 'cap_60', 'cap_70']
    pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
    print('=== Cap Rate short-stay por bairro x tipo (ocupa 50/60/70%) ===')
    print(tab[cols].to_string(index=False))

if __name__ == '__main__':
    main()