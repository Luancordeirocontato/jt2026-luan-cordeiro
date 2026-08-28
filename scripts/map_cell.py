# Célula do mapa interativo — AUTOCONTIDA (não depende de variáveis do notebook).
# Se 'air'/'tab'/'BASE' não existirem no escopo do chamador, reconstrói do zero.
# Gera folium.Map com UM marcador por célula (bairro x tipo), colorido pelo Cap Rate
# (cenário diferencial, faixa alta por perfil), tamanho proporcional ao nº de imóveis.
import pandas as pd
import folium

# ---------- autonomia: reconstrói air/tab/BASE se não estiverem no contexto ----------
_faltam = any(v not in globals() for v in ('BASE', 'air', 'tab'))
if _faltam:
    import numpy as np
    import unicodedata

    def _norm(s):
        if not isinstance(s, str):
            return s
        return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().strip().lower()

    _MERGERS = {
        'jardim praiamar': 'jardim praia mar',
        'meia praia - frente mar': 'meia praia',
        'taboleiro': 'tabuleiro dos oliveiras',
        'tabuleiro': 'tabuleiro dos oliveiras',
    }
    def _bairro_canonic(s):
        n = _norm(s)
        return _MERGERS.get(n, n)

    def _bin_tipo(nb):
        if nb <= 1:
            return '1qto'
        if nb == 2:
            return '2q'
        if nb == 3:
            return '3q'
        return '4q+'

    _BASE = '../data/'
    _D = pd.read_csv(f'{_BASE}Details_Itapema.csv', encoding='utf-8',
                     usecols=['airbnb_listing_id', 'number_of_bedrooms', 'listing_type'])
    _M = pd.read_csv(f'{_BASE}Mesh_Ids_Data_Itapema.csv', encoding='utf-8',
                     usecols=['airbnb_listing_id', 'suburb'])
    _M = _M[_M['suburb'].str.lower() != 'none'].dropna(subset=['suburb'])
    _M['bairro'] = _M['suburb'].map(_bairro_canonic)
    _P = pd.read_csv(f'{_BASE}Price_AV_Itapema.csv', encoding='utf-8',
                     usecols=['airbnb_listing_id', 'price'])
    _air = (_D.merge(_M[['airbnb_listing_id', 'bairro']], on='airbnb_listing_id', how='inner')
              .merge(_P, on='airbnb_listing_id', how='inner'))
    _air = _air[_air['listing_type'] == 'apartamento']
    _air['tipo'] = _air['number_of_bedrooms'].map(_bin_tipo)

    _cnt = _air.groupby(['bairro', 'tipo'])['airbnb_listing_id'].nunique().rename('n_airbnb')
    _rec = _air.groupby(['bairro', 'tipo'])['price'].median().rename('price_med_noite')

    _V = pd.read_csv(f'{_BASE}VivaReal_Itapema.csv', encoding='utf-8',
                     usecols=['suburb', 'bedrooms', 'listing_type', 'sale_price', 'usable_area'])
    _V = _V[(_V['listing_type'] == 'apartamento') & (_V['sale_price'] > 0)]
    _V = _V.dropna(subset=['suburb'])
    _V['bairro'] = _V['suburb'].map(_bairro_canonic)
    _V['tipo'] = _V['bedrooms'].map(_bin_tipo)
    _lo, _hi = _V['sale_price'].quantile([0.01, 0.99])
    _V = _V[(_V['sale_price'] >= _lo) & (_V['sale_price'] <= _hi)]

    _nviv = _V.groupby(['bairro', 'tipo']).size().rename('n_vivareal')
    _prec = _V.groupby(['bairro', 'tipo'])['sale_price'].median().rename('sale_price_med')

    _t = (pd.DataFrame({'price_med_noite': _rec, 'sale_price_med': _prec, 'n_vivareal': _nviv})
              .merge(_cnt, on=['bairro', 'tipo'], how='left').reset_index())
    _t = _t[(_t['n_airbnb'] >= 20) & (_t['n_vivareal'] >= 15)].copy()
    _t['k'] = _t['price_med_noite'] * 365 / _t['sale_price_med']

    BASE, air, tab = _BASE, _air, _t

# ---------- Cap rate por célula (cenário diferencial, faixa alta por perfil) ----------
_occ_diff = {'centro': (0.55, 0.60), 'meia praia': (0.60, 0.65), 'morretes': (0.45, 0.55)}
_tab_map = tab.copy()
_tab_map['cap_cell'] = _tab_map.apply(
    lambda r: _occ_diff.get(r['bairro'], (0.55, 0.60))[1] * r['k'], axis=1)
_tab_map['chave'] = _tab_map['bairro'] + ' ' + _tab_map['tipo']

_MESH = pd.read_csv(f'{BASE}Mesh_Ids_Data_Itapema.csv', encoding='utf-8',
                    usecols=['airbnb_listing_id', 'latitude', 'longitude'])
_air_map = air[['airbnb_listing_id', 'bairro', 'tipo']].merge(_MESH, on='airbnb_listing_id', how='inner')

# centroide + n por célula
_centro = (_air_map.groupby(['bairro', 'tipo'])
                 .agg(lat=('latitude', 'mean'), lon=('longitude', 'mean'),
                      n=('airbnb_listing_id', 'count'))
                 .reset_index())
_centro['chave'] = _centro['bairro'] + ' ' + _centro['tipo']
_map_df = _centro.merge(_tab_map[['chave', 'cap_cell']], on='chave', how='left')
_map_df = _map_df.dropna(subset=['lat', 'lon'])

m = folium.Map(location=[-27.10, -48.606], zoom_start=14, tiles='OpenStreetMap')

val_min = _map_df['cap_cell'].min() if _map_df['cap_cell'].notna().any() else 0
val_max = _map_df['cap_cell'].max() if _map_df['cap_cell'].notna().any() else 1

def cor_cap(v):
    """Vermelho -> amarelo -> verde (2 segmentos); passa por amarelo no meio,
    nunca por cinza."""
    if pd.isna(v):
        return 'gray'
    t = (v - val_min) / (val_max - val_min) if val_max > val_min else 0
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        # vermelho (255,0,0) -> amarelo (255,255,0)
        s = t * 2
        r, g, b = 255, int(255 * s), 0
    else:
        # amarelo (255,255,0) -> verde (0,255,0)
        s = (t - 0.5) * 2
        r, g, b = int(255 * (1 - s)), 255, 0
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

for _, row in _map_df.iterrows():
    if pd.notna(row['cap_cell']):
        popup = '{} - Cap {:.1%}<br>{} imóveis'.format(row['chave'], row['cap_cell'], int(row['n']))
    else:
        popup = '{} (fora do ranking)<br>{} imóveis'.format(row['chave'], int(row['n']))
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=8 + 4 * min(row['n'], 60) / 60,
        color=cor_cap(row['cap_cell']),
        fill=True,
        fill_opacity=0.8,
        popup=popup,
    ).add_to(m)

legend_html = '''<div style="position:fixed; bottom:30px; left:30px; z-index:9999;
  background:white; padding:8px 12px; border:1px solid #ccc; font:12px sans-serif;">
  <b>Cap Rate (diferencial, faixa alta)</b><br>
  <span style="color:#ff0000">&#9608;</span> baixo ({:.0%})
  <span style="color:#ffff00">&#9608;</span> medio
  <span style="color:#00ff00">&#9608;</span> alto ({:.0%})<br>
  <span style="color:#808080">&#9679;</span> fora do ranking<br>
  <i>tamanho do marcador = nº de imóveis</i></div>'''.format(val_min, val_max)
m.get_root().html.add_child(folium.Element(legend_html))

# salva o mapa como HTML na pasta analise/ (cwd do kernel quando notebook aberto
# de analise/; se rodando da raiz, usa analise/ explicitamente se existir).
import os as _os
_nb_dir = 'analise' if _os.path.isdir('analise') else '.'
_salva_em = _os.path.join(_nb_dir, 'mapa_interativo.html')
m.save(_salva_em)
print('Mapa salvo em {} ({:.1f} KB)'.format(_salva_em, _os.path.getsize(_salva_em) / 1024))

print('Mapa com centroides por célula ({} células) — role o notebook e veja inline.'.format(len(_map_df)))
print('Autocontido: construiu air/tab do zero.' if _faltam else 'Usou contexto do notebook.')
m