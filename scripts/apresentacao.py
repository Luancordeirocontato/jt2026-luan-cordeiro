# Gera a versão HTML de APRESENTAÇÃO do notebook: sem código, só markdown + outputs,
# com estilo de "material de consultoria".
# Fluxo:
#   1. executa o notebook (atualiza outputs: matrizes/tabelas)
#   2. nbconvert --to html (template lab, converte markdown e embute imagens/folium)
#   3. remove blocos de input de código (.jp-Cell-inputWrapper) e labels "In [n]"
#   4. injeta CSS customizado (fundo creme, tabelas, destaques...)
# Uso:  py scripts/apresentacao.py   (a partir da raiz do repo)
# Obs.: depende de mistune<=2.0.5 (compatível com nbconvert 7.14) e beautifulsoup4.
import os
import subprocess
import sys

from bs4 import BeautifulSoup

# Tipografia: Playfair Display (titulos) + Bebas Neue (destaques de impacto)
# + Inter/Lato (corpo). Carregada do Google Fonts; os stacks de fallback no CSS
# garantem leitura offline (Georgia p/ titulo, Arial Narrow p/ destaque, Segoe p/ corpo).
FONTS_HREF = ('https://fonts.googleapis.com/css2'
              '?family=Playfair+Display:wght@600;700;800;900'
              '&family=Bebas+Neue'
              '&family=Inter:wght@400;500;600;700'
              '&family=Lato:wght@400;700&display=swap')

NB = 'analise/01_analise_principal.ipynb'
OUT = 'analise/apresentacao_sem_codigo.html'
# A versao "bruta" (nbconvert cru, COM as celulas de codigo) e um entregavel, nao
# um temporario: e a partir dela que a versao sem codigo e montada. Antes ela era
# gravada como '_apresentacao_bruta.html' e apagada no fim, o que deixava o
# 'apresentacao_bruta.html' do repo orfao e congelado numa versao antiga do
# notebook. Agora as duas saidas sao regravadas no mesmo passo, sempre em sincronia.
BRUTA = 'analise/apresentacao_bruta.html'

CSS = '''
:root {
  --creme: #f6f2e9;
  --tinta: #26221c;
  --accent: #0f6b5c;
  --accent-2: #d97706;
  --creme-card: #fcfaf4;
  --borda: #e5dfd1;
  --fonte-titulo: 'Playfair Display', Georgia, 'Times New Roman', serif;
  --fonte-impacto: 'Bebas Neue', 'Arial Narrow', 'Haettenschweiler', Impact, sans-serif;
  --fonte-corpo: 'Inter', 'Lato', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  /* o CSS do nbconvert aplica var(--jp-content-font-family) em p/li/td e venceria
     a regra do body; sobrescrever a propria variavel propaga a fonte de corpo */
  --jp-content-font-family: var(--fonte-corpo) !important;
  --jp-ui-font-family: var(--fonte-corpo) !important;
}
.jp-RenderedMarkdown, .jp-RenderedHTML,
.jp-RenderedMarkdown p, .jp-RenderedMarkdown li, .jp-RenderedMarkdown blockquote,
.jp-RenderedMarkdown strong, .jp-RenderedMarkdown em, .jp-RenderedHTML p {
  font-family: var(--fonte-corpo) !important;
}
html, body {
  background: var(--creme) !important;
  color: var(--tinta);
  font-family: var(--fonte-corpo) !important;
  font-size: 17px;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'kern' 1, 'liga' 1;
  line-height: 1.75;
}
.jp-Notebook, main, .jp-Notebook-cell {
  max-width: 860px !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
.jp-Notebook { padding: 56px 28px !important; }
.jp-Cell {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
  margin: 0 0 8px !important;
  padding: 0 !important;
}
.jp-Cell-inputWrapper {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.jp-InputCollapser, .jp-OutputCollapser, .jp-Collapser,
.jp-InputArea-prompt, .jp-OutputArea-prompt, .jp-Prompt, .jp-Metadata,
.jp-Cell-outputCollapser, .jp-Cell-inputCollapser, .jp-InputPlaceholder {
  display: none !important;
}
.jp-InputArea, .jp-Cell-inputArea { padding: 0 !important; }
.jp-RenderedMarkdown, .jp-RenderedHTML { padding: 0 !important; }
.jp-OutputArea { margin: 8px 0 !important; }
.jp-RenderedMarkdown h1 {
  font-family: var(--fonte-titulo) !important;
  font-size: 2.35em; font-weight: 800; color: var(--tinta);
  letter-spacing: -0.015em;
  border-bottom: 3px solid var(--accent);
  padding-bottom: 0.25em; margin: 0 0 0.6em; line-height: 1.25;
}
.jp-RenderedMarkdown h2 {
  font-family: var(--fonte-titulo) !important;
  font-size: 1.6em; font-weight: 700; color: var(--accent);
  letter-spacing: -0.005em; margin: 1.9em 0 0.5em; padding-top: 0.4em;
  border-top: 1px solid var(--borda);
}
.jp-RenderedMarkdown h2:first-child { border-top: none; margin-top: 0.5em; }
.jp-RenderedMarkdown h3 {
  font-family: var(--fonte-titulo) !important;
  font-size: 1.22em; font-weight: 700; color: var(--accent); margin: 1.5em 0 0.4em;
}
.jp-RenderedMarkdown { color: var(--tinta); }
.jp-RenderedMarkdown p { margin: 0.7em 0; }
.jp-RenderedMarkdown li { margin: 0.5em 0; }
.jp-RenderedMarkdown ul, .jp-RenderedMarkdown ol { padding-left: 1.4em; margin: 0.7em 0; }
.jp-RenderedMarkdown strong { color: var(--accent); font-weight: 700; }
.jp-RenderedMarkdown hr { border: none; border-top: 1px solid var(--borda); margin: 2em 0; }
.jp-RenderedMarkdown a:not(.anchor-link) { color: var(--accent-2); font-weight: 600; }
.jp-RenderedMarkdown blockquote {
  background: #eef4f1 !important;
  border-left: 5px solid var(--accent) !important;
  border-radius: 0 10px 10px 0;
  color: #1f3d34;
  padding: 14px 20px; margin: 1.2em 0; font-size: 0.98em;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.jp-RenderedMarkdown blockquote p { margin: 0.3em 0; }
.jp-RenderedMarkdown code {
  background: #ffe9d1 !important;
  color: #7a3d02 !important;
  font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
  font-size: 0.86em; padding: 2px 6px; border-radius: 6px;
}
.jp-RenderedMarkdown pre {
  background: #efead9; border-radius: 10px; padding: 14px 18px;
  overflow-x: auto; line-height: 1.5;
}
/* --- tabelas: collapse elimina bordas duplas / sobreposicao de cabecalho --- */
.jp-RenderedHTML table, .jp-RenderedMarkdown table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  font-size: 13.5px;
  box-sizing: border-box;
}
/* cabecalho em UMA linha: nunca quebra. Se faltar espaco, scroll horizontal. */
.jp-RenderedHTML th, .jp-RenderedMarkdown th {
  background: var(--accent) !important;
  color: #fff !important;
  /* Bebas Neue tem so o peso 400 e caixa alta: sem bold sintetico, com tracking.
     Texto claro sobre fundo escuro fica fino/borrado se antialiasado como corpo;
     'subpixel-antialiased' + optimizeLegibility devolvem a nitidez, e o corpo
     maior (17px) engrossa o traco sem precisar de bold falso. */
  font-family: var(--fonte-impacto) !important;
  font-weight: 400;
  font-synthesis: none;
  font-size: 17px;
  text-transform: uppercase;
  letter-spacing: 0.045em;
  -webkit-font-smoothing: subpixel-antialiased;
  -moz-osx-font-smoothing: auto;
  text-rendering: optimizeLegibility;
  text-shadow: none;
  padding: 11px 14px;
  text-align: left;
  white-space: nowrap;
  line-height: 1.25;
}
.jp-RenderedHTML td, .jp-RenderedMarkdown td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--borda);
  background: var(--creme-card);
  white-space: nowrap;
}
/* permite scroll horizontal em vez de quebrar/sobrepor */
.jp-OutputArea, .jp-RenderedHTML, .jp-RenderedMarkdown {
  overflow-x: auto;
}
/* NAO esconder a 1a coluna: todos os display() do notebook ja usam
   Styler.hide(axis='index'), que remove o indice do pandas no proprio HTML
   (nenhuma tabela sai com <th> vazio a esquerda). A regra antiga
   'table.no-index th:first-child { display:none }' estava, por isso,
   engolindo a primeira coluna de DADOS: o '#' do ranking e a coluna
   'Recomendacao' (colorida) do cartao do investimento. */
table.no-index { table-layout: auto; }
/* header mais fino e elegante */
.jp-RenderedHTML th, .jp-RenderedMarkdown th {
  padding: 9px 12px;
}
.jp-RenderedMarkdown tr:nth-child(even) td, .jp-RenderedHTML tr:nth-child(even) td {
  background: #f8f5ed;
}
.jp-RenderedMarkdown tr:last-child td, .jp-RenderedHTML tr:last-child td {
  border-bottom: none;
}
.jp-RenderedMarkdown img, .jp-RenderedHTML img, .jp-RenderedImage img, .jp-OutputArea img {
  border-radius: 14px;
  box-shadow: 0 4px 18px rgba(0,0,0,0.14);
  margin: 1em 0;
}
.jp-OutputArea-output .jp-RenderedText pre {
  background: transparent; padding: 4px 8px; margin: 2px 0;
}
/* numeros alinhados em coluna (Inter com algarismos tabulares) */
.jp-RenderedHTML td, .jp-RenderedMarkdown td {
  font-family: var(--fonte-corpo);
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum' 1;
}
/* destaque de impacto reutilizavel: <span class="impacto">13,4%</span> */
.impacto, .jp-RenderedMarkdown .impacto {
  font-family: var(--fonte-impacto) !important;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 1.35em;
  line-height: 1.1;
  color: var(--accent);
}
/* --- matriz do deep-dive (secao 8) ---------------------------------------
   As regras globais de <th> (Bebas Neue em caixa alta, fundo verde escuro)
   valem para tabela de ranking, mas nesta matriz elas gritam: os rotulos de
   caracteristica e de celula viram IS_PROFESSIONAL / MEIA PRAIA 1QTO. Aqui a
   tipografia volta ao corpo, em caixa normal, e o cabecalho de linha fica
   claro para nao competir com as cores das celulas. */
table.deep-dive th, table.deep-dive td {
  font-family: var(--fonte-corpo) !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  white-space: nowrap;
}
table.deep-dive thead th {
  background-color: var(--accent) !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-size: 13.5px !important;
  text-align: center !important;
  padding: 13px 16px !important;
}
table.deep-dive thead th.blank {
  background-color: transparent !important;
  border: none !important;
}
table.deep-dive tbody th {
  background-color: #eef4f1 !important;
  color: var(--tinta) !important;
  font-weight: 500 !important;
  font-size: 13.5px !important;
  text-align: left !important;
  padding: 15px 16px !important;
}
/* respiro entre as linhas: a separacao vem de um vao na cor do fundo, nao de
   uma regra, para nao cortar as faixas pastel */
table.deep-dive { border-collapse: separate !important; border-spacing: 0 3px !important; }
table.deep-dive tbody td {
  font-size: 15px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  text-align: center;
  padding: 15px 18px;
  border-bottom: none !important;
}
/* a faixa zebrada do CSS geral nao se aplica: cada celula tem cor de sinal */
table.deep-dive tbody tr:nth-child(even) td { background: inherit; }

/* legenda do mapa folium embutido segue a mesma tipografia */
.leaflet-container, .leaflet-popup-content {
  font-family: var(--fonte-corpo) !important;
}
'''


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nb_path = os.path.join(repo, NB)
    bruta_path = os.path.join(repo, BRUTA)
    out_path = os.path.join(repo, OUT)
    nb_dir = os.path.dirname(nb_path)

    print('1) executando notebook...')
    r = subprocess.run(
        [sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook',
         '--execute', '--inplace', NB],
        cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:])
        sys.exit(1)

    print('2) nbconvert para HTML (versao bruta, com codigo)...')
    r = subprocess.run(
        [sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'html',
         nb_path, '--output', os.path.basename(BRUTA)],
        cwd=nb_dir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        sys.exit(1)

    print('3) removendo código...')
    with open(bruta_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for c in soup.select('.jp-CodeCell'):
        for iw in c.select('.jp-Cell-inputWrapper'):
            iw.decompose()
    for p in soup.select('.jp-InputArea-prompt'):
        p.decompose()
    for cell in soup.select('.jp-CodeCell.jp-mod-noOutputs'):
        cell.decompose()

    print('4) injetando fontes + CSS customizado...')
    title = soup.find('title')
    style = soup.new_tag('style')
    style.string = CSS
    title.insert_after(style)
    # preconnect + folha do Google Fonts (inseridos ANTES do <style>)
    for attrs in ({'rel': 'preconnect', 'href': 'https://fonts.googleapis.com'},
                  {'rel': 'preconnect', 'href': 'https://fonts.gstatic.com',
                   'crossorigin': 'anonymous'},
                  {'rel': 'stylesheet', 'href': FONTS_HREF}):
        title.insert_after(soup.new_tag('link', **attrs))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f'OK -> {BRUTA} ({os.path.getsize(bruta_path)//1024} KB)')
    print(f'OK -> {OUT} ({os.path.getsize(out_path)//1024} KB)')


if __name__ == '__main__':
    main()