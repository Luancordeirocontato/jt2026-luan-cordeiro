# Deep-dive (corrigido): o que separa imóveis que rendem mais vs menos DENTRO de cada célula compacta.
# Nível de análise: LISTING (1 imóvel = 1 linha). R$/noite = mediana por listing (jan-abr, viés verão).
# Foco (beira-mar, alvo Seazone): Centro 1q, Centro 2q, Meia Praia 1q, Meia Praia 2q.
# Saída: para cada característica, R$/noite mediano tem-vs-não e diferença (R$ e %).

import pandas as pd
import numpy as np
import unicodedata

def norm(s):
    if not isinstance(s, str):
        return s
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().strip().lower()

MERGERS = {
    'jardim praiamar': 'jardim praia mar',
    'meia praia - frente mar': 'meia praia',
    'taboleiro': 'tabuleiro dos oliveiras',
    'tabuleiro': 'tabuleiro dos oliveiras',
}
def bairro_canonic(s):
    n = norm(s)
    return MERGERS.get(n, n)

def bin_tipo(nb):
    if nb <= 1:
        return '1qto'
    if nb == 2:
        return '2q'
    if nb == 3:
        return '3q'
    return '4q+'

BASE = 'data/'

D = pd.read_csv(f'{BASE}Details_Itapema.csv', encoding='utf-8')
M = pd.read_csv(f'{BASE}Mesh_Ids_Data_Itapema.csv', encoding='utf-8',
                usecols=['airbnb_listing_id', 'suburb'])
M = M[M['suburb'].str.lower() != 'none'].dropna(subset=['suburb'])
M['bairro'] = M['suburb'].map(bairro_canonic)
P = pd.read_csv(f'{BASE}Price_AV_Itapema.csv', encoding='utf-8',
                usecols=['airbnb_listing_id', 'price'])
H = pd.read_csv(f'{BASE}Hosts_ids_Itapema.csv', encoding='utf-8')

# R$/noite mediano por listing (agrega Price no nível do imóvel)
prec_listing = P.groupby('airbnb_listing_id')['price'].median().rename('price_med_noite')

# Construção no nível listing: Details é 1 linha/imóvel
df = (D.merge(M[['airbnb_listing_id', 'bairro']], on='airbnb_listing_id', how='inner')
       .merge(prec_listing, on='airbnb_listing_id', how='inner')
       .merge(H, on='owner_id', how='left'))
df = df[df['listing_type'] == 'apartamento']
df['tipo'] = df['number_of_bedrooms'].map(bin_tipo)
df = df.drop_duplicates('airbnb_listing_id')  # garante nível listing

FOCAL = [('centro', '1qto'), ('centro', '2q'),
         ('meia praia', '1qto'), ('meia praia', '2q')]

BIN = {
    'is_superhost': True,
    'is_professional': True,
    'can_instant_book': True,
    'is_guest_favorite': True,
    'is_verified': True,
}
# limiares numéricos: rótulo e função de "tem"
THRESH = {
    'star_rating': ('>= 4.8', lambda s: s >= 4.8),
    'number_of_reviews': ('>= 20', lambda s: s >= 20),
    'picture_count': ('>= 30', lambda s: s >= 30),
    'min_nights': ('>= 3', lambda s: s >= 3),
    'response_rate_shown': ('>= 90%', lambda s: s >= 90),
    'years_host': ('>= 3', lambda s: s >= 3),
}

TAB_ROWS = []
for (bairo, t) in FOCAL:
    sub = df[(df['bairro'] == bairo) & (df['tipo'] == t)].copy()
    label = f'{bairo} {t} (n={len(sub)})'
    print(f'\n===== {label} =====')
    rows = []
    feats = []
    for col, pos in BIN.items():
        if col not in sub.columns:
            continue
        grp = sub[sub[col] == pos]['price_med_noite'].dropna()
        grp_no = sub[sub[col] != pos]['price_med_noite'].dropna()
        trim_null = sub[col].isna().sum()
        if len(grp) == 0 or len(grp_no) == 0:
            continue
        med_tem, med_nao = grp.median(), grp_no.median()
        feats.append((f'{col}' + (f' [{trim_null}NaN]' if trim_null else ''), len(grp), len(grp_no), med_tem, med_nao))
    for col, (labl, fn) in THRESH.items():
        val = sub[col]
        if val.isna().all():
            continue
        mask = val.apply(lambda x: fn(x) if pd.notna(x) else False)
        grp = sub[mask]['price_med_noite'].dropna()
        grp_no = sub[~mask]['price_med_noite'].dropna()
        trim_null = val.isna().sum()
        if len(grp) == 0 or len(grp_no) == 0:
            continue
        med_tem, med_nao = grp.median(), grp_no.median()
        feats.append((f'{col} {labl}' + (f' [{trim_null}NaN]' if trim_null else ''), len(grp), len(grp_no), med_tem, med_nao))

    for (fn, n_tem, n_nao, med_tem, med_nao) in feats:
        dif = med_tem - med_nao
        pct = (med_tem / med_nao - 1) * 100 if med_nao else np.nan
        print(f'  {fn:<28} tem={n_tem:>4} não={n_nao:>4} | R$ {med_tem:>6.0f} vs {med_nao:>6.0f} | dif {dif:>+6.0f} ({pct:>+5.0f}%)')
        TAB_ROWS.append({'celula': label, 'carac': fn, 'tem_n': n_tem, 'nao_n': n_nao,
                         'tem_med': med_tem, 'nao_med': med_nao, 'dif': dif, 'pct': pct})

all_rows = pd.DataFrame(TAB_ROWS)
all_rows['|pct|'] = all_rows['pct'].abs()
solid = all_rows[(all_rows['tem_n'] >= 5) & (all_rows['nao_n'] >= 5)].dropna(subset=['pct'])

print('\n===== TOP 5 características por |% dif| médio (só grupos sólidos, n>=5) =====')
if not solid.empty:
    agg = (solid.groupby('carac')['pct']
                 .agg(mean_pct='mean', n_celulas='count')
                 .sort_values('mean_pct', key=lambda s: s.abs(), ascending=False))
    print(agg.round(0).to_string())

print('\n===== TOP 3 RECOMENDÁVEIS (que DEVEM elevar receita: % dif > 0) =====')
pos = solid[solid['pct'] > 0]
if not pos.empty:
    agg_pos = (pos.groupby('carac')['pct'].mean()
                   .sort_values(ascending=False))
    print(agg_pos.round(0).head(3).to_string())