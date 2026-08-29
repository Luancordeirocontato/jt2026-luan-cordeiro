# Verificador de coerencia dos Cap Rates entre os entregaveis.
#
# Por que existe: a mesma metrica aparece em cinco lugares (secoes 5b, 7, 9 e os
# mapas do notebook, mais a tabela do relatorio). Cada um foi escrito em momento
# diferente, e ja aconteceu de um deles ficar num cenario de ocupacao e o resto em
# outro -- foi assim que a secao 7 chegou a mostrar Morretes liderando enquanto o
# cartao recomendava Meia Praia.
#
# O script NAO le o codigo do notebook: recalcula tudo do zero a partir dos CSVs
# brutos e compara com o que esta PUBLICADO em cada saida. Se algum numero foi
# editado a mao, ou se uma celula ficou com output velho, a checagem quebra.
#
# Uso:  py scripts/verificar_coerencia.py     (a partir da raiz do repo)
# Saida: uma linha por checagem, e codigo 1 se qualquer uma falhar.
import io
import json
import os
import re
import sys
import unicodedata

import pandas as pd

OCC_ALTA = {'meia praia': 0.65, 'centro': 0.60, 'morretes': 0.55}
OCC_FALLBACK = 0.60
OCC_FAIXA = {'meia praia': (0.60, 0.65), 'centro': (0.55, 0.60), 'morretes': (0.45, 0.55)}

falhas = []


def checa(nome, ok, detalhe=''):
    print(('  OK    ' if ok else '  FALHA ') + nome + (('  ' + detalhe) if detalhe else ''))
    if not ok:
        falhas.append(nome)


# ----------------------------------------------------------- 1. recalculo do zero
def norm(s):
    if not isinstance(s, str):
        return s
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().strip().lower()


MERGERS = {'jardim praiamar': 'jardim praia mar', 'meia praia - frente mar': 'meia praia',
           'taboleiro': 'tabuleiro dos oliveiras', 'tabuleiro': 'tabuleiro dos oliveiras'}
canon = lambda s: MERGERS.get(norm(s), norm(s))
binn = lambda n: '1qto' if n <= 1 else ('2q' if n == 2 else ('3q' if n == 3 else '4q+'))


def base():
    D = pd.read_csv('data/Details_Itapema.csv',
                    usecols=['airbnb_listing_id', 'number_of_bedrooms', 'listing_type'])
    M = pd.read_csv('data/Mesh_Ids_Data_Itapema.csv', usecols=['airbnb_listing_id', 'suburb'])
    M = M[M['suburb'].str.lower() != 'none'].dropna(subset=['suburb'])
    M['bairro'] = M['suburb'].map(canon)
    P = pd.read_csv('data/Price_AV_Itapema.csv', usecols=['airbnb_listing_id', 'price'])
    air = (D.merge(M[['airbnb_listing_id', 'bairro']], on='airbnb_listing_id')
             .merge(P, on='airbnb_listing_id'))
    air = air[air['listing_type'] == 'apartamento']
    air['tipo'] = air['number_of_bedrooms'].map(binn)

    V = pd.read_csv('data/VivaReal_Itapema.csv',
                    usecols=['suburb', 'bedrooms', 'listing_type', 'sale_price'])
    V = V[(V['listing_type'] == 'apartamento') & (V['sale_price'] > 0)].dropna(subset=['suburb'])
    V['bairro'] = V['suburb'].map(canon)
    V['tipo'] = V['bedrooms'].map(binn)
    lo, hi = V['sale_price'].quantile([0.01, 0.99])
    V = V[(V['sale_price'] >= lo) & (V['sale_price'] <= hi)]

    t = pd.concat([
        air.groupby(['bairro', 'tipo'])['airbnb_listing_id'].nunique().rename('n_air'),
        air.groupby(['bairro', 'tipo'])['price'].median().rename('noite'),
        V.groupby(['bairro', 'tipo']).size().rename('n_viv'),
        V.groupby(['bairro', 'tipo'])['sale_price'].median().rename('venda')], axis=1).dropna()
    t = t[(t.n_air >= 20) & (t.n_viv >= 15)]
    t['k'] = t.noite * 365 / t.venda
    t['occ'] = [OCC_ALTA.get(b, OCC_FALLBACK) for b, _ in t.index]
    t['cap_alta'] = t.k * t.occ
    return t


# ----------------------------------------------------------- utilitarios de leitura
def pct(txt):
    """'13,4%' -> 0.134"""
    m = re.search(r'(-?[\d.]+),(\d+)\s*%', txt.replace('−', '-'))
    if not m:
        m2 = re.search(r'(-?[\d.]+)\s*%', txt)
        return float(m2.group(1).replace('.', '')) / 100 if m2 else None
    return float(m.group(1).replace('.', '') + '.' + m.group(2)) / 100


def tabelas_do_notebook(nb):
    """Extrai as tabelas HTML das saidas, como listas de listas de texto."""
    from bs4 import BeautifulSoup
    out = []
    for cel in nb['cells']:
        for o in cel.get('outputs', []):
            html = o.get('data', {}).get('text/html')
            if not html:
                continue
            for t in BeautifulSoup(''.join(html), 'html.parser').find_all('table'):
                linhas = []
                for tr in t.find_all('tr'):
                    linhas.append([c.get_text(' ', strip=True) for c in tr.find_all(['th', 'td'])])
                if linhas:
                    out.append(linhas)
    return out


def acha_tabela(tabelas, *cabecalhos):
    for t in tabelas:
        cab = ' '.join(t[0])
        if all(h in cab for h in cabecalhos):
            return t
    return None


# ----------------------------------------------------------- checagens
def main():
    if not os.path.exists('data/Details_Itapema.csv'):
        sys.exit('rode a partir da raiz do repositorio')
    t = base()
    esperado = {f'{b} {tp}': r.cap_alta for (b, tp), r in t.iterrows()}
    print('Cap Rate recalculado do zero (ocupacao diferencial, faixa alta):')
    for k, v in sorted(esperado.items(), key=lambda x: -x[1]):
        print(f'    {k:22} {v:6.1%}')
    print()

    nb = json.load(io.open('analise/01_analise_principal.ipynb', encoding='utf-8'))
    tabelas = tabelas_do_notebook(nb)

    # --- secao 7: ranking com confianca
    t7 = acha_tabela(tabelas, 'Cap Rate (diferencial)', 'Confiança')
    if t7 is None:
        checa('secao 7 encontrada', False)
    else:
        ordem = [f'{l[1]} {l[2]}' for l in t7[1:]]
        caps = {f'{l[1]} {l[2]}': pct(l[4]) for l in t7[1:]}
        ok = all(abs(caps[c] - esperado[c]) < 0.0006 for c in caps if c in esperado)
        checa('secao 7: Cap Rate bate com o recalculo', ok)
        checa('secao 7: ordenada por Cap decrescente',
              ordem == sorted(ordem, key=lambda c: -esperado.get(c, 0)))
        checa('secao 7: lider e Meia Praia 1qto', ordem[0] == 'meia praia 1qto', ordem[0])

    # --- secao 5b: mesma premissa, faixa baixa e alta
    t5b = acha_tabela(tabelas, 'Cap diferencial (alta)')
    if t5b is None:
        checa('secao 5b encontrada', False)
    else:
        caps5b = {f'{l[1]} {l[2]}': pct(l[6]) for l in t5b[1:]}
        ok = all(abs(caps5b[c] - esperado[c]) < 0.0006 for c in caps5b if c in esperado)
        checa('secao 5b: faixa alta bate com o recalculo', ok)
        if t7 is not None:
            checa('secao 5b e secao 7 concordam no lider',
                  list(caps5b)[0] == ordem[0], f'{list(caps5b)[0]} vs {ordem[0]}')

    # --- secao 9: cartao do investimento
    t9 = acha_tabela(tabelas, 'Cap Rate', 'Payback')
    if t9 is None:
        checa('secao 9 encontrada', False)
    else:
        mapa = {'Meia Praia 1q': 'meia praia 1qto', 'Morretes 2q': 'morretes 2q',
                'Centro 2q': 'centro 2q', 'Centro 1q': 'centro 1qto'}
        ok = True
        for l in t9[1:]:
            cel = l[1]
            if cel not in mapa:
                continue
            alta = pct(l[5].split(' a ')[-1])
            if abs(alta - esperado[mapa[cel]]) > 0.0006:
                ok = False
                print(f'      {cel}: cartao {alta:.1%} vs recalculo {esperado[mapa[cel]]:.1%}')
        checa('secao 9: cartao bate com o recalculo (ponta alta)', ok)

    # --- mapa interativo
    if os.path.exists('analise/mapa_interativo.html'):
        raw = io.open('analise/mapa_interativo.html', encoding='utf-8').read()
        # o popup do folium usa ponto decimal ('Cap 11.5%'), nao a virgula do pt-BR
        achados = re.findall(
            r'>([a-zà-ú ]+ (?:1qto|2q|3q|4q\+))<br><span class="cap">Cap ([\d.,]+)\s*%', raw)
        ok = bool(achados)
        for chave, val in achados:
            v = float(val.replace(',', '.')) / 100
            if chave in esperado and abs(v - esperado[chave]) > 0.0006:
                ok = False
                print(f'      mapa {chave}: {v:.1%} vs {esperado[chave]:.1%}')
        checa('mapa interativo: popups batem com o recalculo', ok, f'({len(achados)} celulas)')

    # --- relatorio, tabela da secao 1
    rel = io.open('reports/recomendacao_executiva.md', encoding='utf-8').read()
    mapa_rel = {'Meia Praia 1q': 'meia praia 1qto', 'Morretes 2q': 'morretes 2q',
                'Centro 2q': 'centro 2q', 'Centro 1q': 'centro 1qto'}
    ok = True
    for linha in rel[rel.index('| Prioridade'):rel.index('\\* Receita')].split('\n')[2:]:
        col = [c.strip().replace('**', '') for c in linha.split('|')[1:-1]]
        if len(col) < 6 or col[1] not in mapa_rel:
            continue
        alta = pct(col[5].split('–')[-1])
        alvo = esperado[mapa_rel[col[1]]] * (OCC_FAIXA[col[1].rsplit(' ', 1)[0].lower()][1] / OCC_ALTA[col[1].rsplit(' ', 1)[0].lower()])
        if abs(alta - alvo) > 0.0006:
            ok = False
            print(f'      relatorio {col[1]}: {alta:.1%} vs {alvo:.1%}')
    checa('relatorio secao 1: tabela bate com o recalculo', ok)

    print()
    if falhas:
        print(f'{len(falhas)} checagem(ns) FALHARAM:', ', '.join(falhas))
        sys.exit(1)
    print('Todas as checagens passaram — os Cap Rates estao coerentes entre os entregaveis.')


if __name__ == '__main__':
    main()
