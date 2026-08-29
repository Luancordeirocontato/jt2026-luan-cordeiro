# Gera a versão HTML de APRESENTAÇÃO do notebook: sem código, só markdown + outputs,
# com estética de dashboard de consultoria (não de notebook Jupyter).
# Fluxo:
#   1. executa o notebook (atualiza outputs: matrizes/tabelas)
#   2. nbconvert --to html (template lab, converte markdown e embute imagens/folium)
#   3. remove blocos de input de código e containers que ficaram vazios
#   4. reestrutura: capa + uma <section class="card"> por seção (h2)
#   5. marca colunas numéricas e a linha da recomendação principal
#   6. injeta fontes do Google + CSS customizado
# NENHUM passo altera texto, número, seção ou tabela — só embrulha e classifica.
# Uso:  py scripts/apresentacao.py   (a partir da raiz do repo)
# Obs.: depende de mistune<=2.0.5 (compatível com nbconvert 7.14) e beautifulsoup4.
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

# Tipografia: duas famílias só.
#   Archivo  -> texto (sem serifa moderna, boa em peso alto para títulos)
#   IBM Plex Mono -> números e termos entre crases (algarismos de largura fixa,
#                    que é o que alinha coluna de tabela)
FONTS_HREF = ('https://fonts.googleapis.com/css2'
              '?family=Archivo:wght@400;500;600;700;800'
              '&family=IBM+Plex+Mono:wght@400;500;600'
              '&display=swap')

NB = 'analise/01_analise_principal.ipynb'
OUT = 'analise/apresentacao.html'
# O notebook completo (nbconvert cru, COM as celulas de codigo) e um entregavel,
# nao um temporario: e a partir dele que a versao de apresentacao e montada. Antes
# era gravado num arquivo temporario e apagado no fim, o que deixava a copia do
# repo orfa e congelada numa versao antiga do notebook. Agora as duas saidas sao
# regravadas no mesmo passo, sempre em sincronia.
BRUTA = 'analise/notebook_completo.html'

CSS = '''
/* ============================================================ tokens
   Claro por padrão; o bloco prefers-color-scheme troca só as variáveis. */
:root {
  /* Paleta Seazone. Os tokens vem do design system do proprio site
     (seazone.com.br): navy --colors-primary-theme #011337, coral do logo
     #F1605D / #FC6058, azul de realce #3758A6, fundo lavanda #EBEBF5. */
  --bg:        #f9f8f5;   /* quase branco com um toque de creme */
  --surface:   #fffffd;   /* card, um tom acima do fundo */
  --surface-2: #f2f3f7;   /* blocos de apoio (tags, saída de terminal) */
  --line:      #e4e5ea;   /* borda Seazone (#E1E2E5), levemente fria */
  --line-soft: #eeeff3;
  --ink:       #19191a;   /* --colors-text-theme */
  --ink-2:     #62656f;   /* --content-theme-secondary */
  --accent:    #011337;   /* navy Seazone: títulos de seção */
  --accent-2:  #3758a6;   /* azul de realce: h3, links, callout */
  --coral:     #f1605d;   /* coral do logo: título da capa */
  --wash:      #f0f2fa;   /* --secondary: fundo do callout */
  --destaque:  #ebebf5;   /* --colors-background-theme: linha vencedora */
  --sombra:    0 1px 2px rgba(1,19,55,.04), 0 8px 24px rgba(1,19,55,.07);
  --sombra-img: 0 2px 6px rgba(1,19,55,.07), 0 12px 28px rgba(1,19,55,.11);

  --sans: 'Archivo', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --mono: 'IBM Plex Mono', 'Cascadia Code', Consolas, 'Courier New', monospace;

  /* o CSS do nbconvert aplica var(--jp-content-font-family) em p/li/td e venceria
     a regra do body; sobrescrever a propria variavel propaga a fonte de corpo */
  --jp-content-font-family: var(--sans) !important;
  --jp-ui-font-family: var(--sans) !important;
}
@media (prefers-color-scheme: dark) {
  :root {
    /* no escuro o navy vira o fundo e o azul claro assume os titulos */
    --bg:        #0b1020;
    --surface:   #121a2e;
    --surface-2: #1a2338;
    --line:      #253048;
    --line-soft: #1e2840;
    --ink:       #e8eaf2;
    --ink-2:     #9aa3ba;
    --accent:    #a8c2f0;
    --accent-2:  #8fb0e8;
    --coral:     #ff8a87;
    --wash:      #17203a;
    --destaque:  #1b2440;
    --sombra:    0 1px 2px rgba(0,0,0,.34), 0 8px 24px rgba(0,0,0,.40);
    --sombra-img: 0 2px 6px rgba(0,0,0,.38), 0 12px 28px rgba(0,0,0,.48);
  }
}

/* ============================================================ base */
html, body {
  background: var(--bg) !important;
  color: var(--ink);
  font-family: var(--sans) !important;
  font-size: 16.5px;
  line-height: 1.72;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'kern' 1, 'liga' 1;
}
.jp-RenderedMarkdown, .jp-RenderedHTML,
.jp-RenderedMarkdown p, .jp-RenderedMarkdown li, .jp-RenderedMarkdown blockquote,
.jp-RenderedMarkdown strong, .jp-RenderedMarkdown em, .jp-RenderedHTML p {
  font-family: var(--sans) !important;
  color: var(--ink);
}
.jp-Notebook, main, .jp-Notebook-cell {
  max-width: 1100px !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
.jp-Notebook { padding: 40px 24px 72px !important; background: transparent !important; }

/* zera a moldura de célula do Jupyter: quem desenha caixa agora é o .card */
.jp-Cell {
  box-shadow: none !important; border: none !important;
  background: transparent !important; margin: 0 !important; padding: 0 !important;
}
.jp-Cell-inputWrapper, .jp-InputArea, .jp-Cell-inputArea {
  background: transparent !important; border: none !important;
  box-shadow: none !important; padding: 0 !important;
}
.jp-InputCollapser, .jp-OutputCollapser, .jp-Collapser,
.jp-InputArea-prompt, .jp-OutputArea-prompt, .jp-OutputPrompt, .jp-Prompt,
.jp-Metadata, .jp-Cell-outputCollapser, .jp-Cell-inputCollapser,
.jp-InputPlaceholder, .jp-OutputPlaceholder {
  display: none !important;
}
.jp-RenderedMarkdown, .jp-RenderedHTML { padding: 0 !important; }
.jp-OutputArea { margin: 0 !important; background: transparent !important; }
.jp-OutputArea-child { background: transparent !important; }
/* caixas cinzas que sobram do Jupyter quando a célula não tem saída visível */
.jp-Cell.jp-mod-noOutputs, .jp-OutputArea:empty, .jp-OutputArea-child:empty,
.jp-Cell-outputWrapper:empty, .jp-RenderedText:empty, .vazio {
  display: none !important;
}

/* ============================================================ capa */
.capa {
  max-width: 1100px; margin: 0 auto; padding: 64px 34px 34px;
}
.capa .jp-RenderedMarkdown h1 {
  font-family: var(--sans);
  font-size: 2.6rem; font-weight: 800; letter-spacing: -.025em;
  /* coral da marca. Em 2.6rem/800 conta como texto grande, e o contraste de
     3.19:1 sobre o fundo do card fica acima do minimo AA para esse porte. */
  line-height: 1.14; color: var(--coral); margin: 0 0 .35em;
  border: none; padding: 0;
}
.capa .jp-RenderedMarkdown h2 {
  font-size: 1.12rem; font-weight: 500; letter-spacing: .005em;
  color: var(--ink-2); text-transform: none;
  margin: 0 0 1.3em; padding: 0; border: none;
}
.capa .jp-RenderedMarkdown h2::before { display: none; }
.capa .jp-RenderedMarkdown p { color: var(--ink-2); font-size: .95rem; max-width: 76ch; }
.capa::after {
  content: ''; display: block; height: 3px; width: 72px;
  background: var(--coral); border-radius: 2px; margin-top: 30px;
}

/* ============================================================ cards */
.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 34px 38px 38px;
  margin: 0 0 26px;
  box-shadow: var(--sombra);
}
.card > .jp-Cell + .jp-Cell { margin-top: 4px !important; }

/* ============================================================ títulos */
.card .jp-RenderedMarkdown h2 {
  font-family: var(--sans) !important;
  font-size: 1.42rem; font-weight: 700; letter-spacing: -.012em;
  color: var(--accent);
  margin: 0 0 1.1rem; padding: 0 0 .7rem;
  border: none; border-bottom: 1px solid var(--line-soft);
  line-height: 1.3;
}
.card .jp-Cell:not(:first-child) .jp-RenderedMarkdown h2 { margin-top: 1.6rem; }
.jp-RenderedMarkdown h3 {
  font-family: var(--sans) !important;
  font-size: 1.03rem; font-weight: 700; letter-spacing: .01em;
  color: var(--accent-2); margin: 2rem 0 .6rem;
}
.jp-RenderedMarkdown h4 {
  font-size: .95rem; font-weight: 600; color: var(--ink-2); margin: 1.5rem 0 .5rem;
}
/* âncora "¶" que o nbconvert pendura nos títulos */
.anchor-link { display: none !important; }

/* ============================================================ texto */
.jp-RenderedMarkdown p { margin: .75em 0; max-width: 82ch; }
.jp-RenderedMarkdown li { margin: .38em 0; max-width: 82ch; }
.jp-RenderedMarkdown ul, .jp-RenderedMarkdown ol { padding-left: 1.25em; margin: .75em 0; }
.jp-RenderedMarkdown ul li::marker { color: var(--accent-2); }
.jp-RenderedMarkdown strong { color: var(--ink); font-weight: 700; }
.jp-RenderedMarkdown em { color: var(--ink-2); }
.jp-RenderedMarkdown hr {
  border: none; border-top: 1px solid var(--line); margin: 2.2em 0;
}
.jp-RenderedMarkdown a:not(.anchor-link) {
  color: var(--accent-2); font-weight: 600;
  text-decoration: underline; text-underline-offset: 3px;
  text-decoration-color: color-mix(in srgb, var(--accent-2) 35%, transparent);
}

/* callout (blockquote do markdown) */
.jp-RenderedMarkdown blockquote {
  background: var(--wash) !important;
  border: 1px solid var(--line-soft) !important;
  border-left: 3px solid var(--accent-2) !important;
  border-radius: 4px 12px 12px 4px;
  color: var(--ink);
  /* !important: o CSS do nbconvert zera o padding vertical do blockquote */
  padding: 20px 26px !important; margin: 1.5em 0 !important;
  font-size: .96rem; box-shadow: none;
}
.jp-RenderedMarkdown blockquote p { margin: .3em 0; }
.jp-RenderedMarkdown blockquote p:first-child { margin-top: 0; }
.jp-RenderedMarkdown blockquote p:last-child { margin-bottom: 0; }

/* termo entre crases vira tag pequena */
.jp-RenderedMarkdown code, .jp-RenderedHTML code {
  background: var(--surface-2) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line-soft);
  font-family: var(--mono) !important;
  font-size: .82em !important; font-weight: 500;
  padding: .12em .45em !important; border-radius: 5px;
  white-space: nowrap;
}

/* saída de texto do notebook (print) */
.jp-OutputArea-output pre, .jp-RenderedText pre, .jp-RenderedMarkdown pre {
  background: var(--surface-2) !important;
  border: 1px solid var(--line-soft);
  border-radius: 10px;
  color: var(--ink) !important;
  font-family: var(--mono) !important;
  font-size: .8rem; line-height: 1.65;
  padding: 14px 18px !important; margin: 1em 0 !important;
  overflow-x: auto;
}
.jp-OutputArea-output pre code { background: none !important; border: none; padding: 0; }

/* ============================================================ tabelas
   Sem bordas verticais e sem zebra: só filetes horizontais bem sutis. */
.jp-RenderedHTML table, .jp-RenderedMarkdown table {
  border-collapse: collapse !important;
  /* width:100% + celulas nowrap fazia a tabela larga ESMAGAR as colunas umas
     sobre as outras em vez de rolar. Com width auto + min-width 100% ela ocupa
     a largura toda quando cabe e transborda para o scroll horizontal quando nao. */
  width: auto !important;
  min-width: 100%;
  margin: 1.5em 0;
  background: transparent !important;
  box-shadow: none !important; border-radius: 0;
  font-size: .875rem;
}
/* a area de saida e quem rola, com um respiro para a barra nao colar na tabela */
.jp-OutputArea-output { overflow-x: auto; padding-bottom: 2px; }
.jp-RenderedHTML thead th, .jp-RenderedMarkdown thead th {
  background: transparent !important;
  color: var(--ink-2) !important;
  font-family: var(--sans) !important;
  font-size: .68rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: .09em !important;
  text-align: left !important;
  padding: 0 14px 10px !important;
  border: none !important;
  border-bottom: 1.5px solid var(--line) !important;
  white-space: nowrap; line-height: 1.4;
}
.jp-RenderedHTML tbody td, .jp-RenderedMarkdown tbody td,
.jp-RenderedHTML tbody th, .jp-RenderedMarkdown tbody th {
  /* SEM !important no fundo: as cores do Styler (matriz do deep-dive, tarjas de
     prioridade do cartao) vem de regras com id (#T_xxx_row0_col0) e precisam
     vencer aqui. Com !important elas eram apagadas e sobrava so a cor do texto. */
  background: transparent;
  color: var(--ink);
  font-family: var(--sans);
  padding: 12px 14px !important;
  border: none !important;
  border-bottom: 1px solid var(--line-soft) !important;
  /* o CSS do nbconvert alinha td a direita por padrao (heranca de planilha);
     categoria vai para a esquerda e so a coluna .num volta para a direita */
  text-align: left !important;
  white-space: nowrap;
}
/* sem zebra: a separacao e o filete horizontal */
.jp-RenderedHTML tbody tr:nth-child(even),
.jp-RenderedMarkdown tbody tr:nth-child(even),
.jp-RenderedHTML tbody tr, .jp-RenderedMarkdown tbody tr {
  background: transparent !important;
}
.jp-RenderedHTML tbody tr:last-child td, .jp-RenderedMarkdown tbody tr:last-child td {
  border-bottom: none !important;
}
/* números: monoespaçado, tabular, à direita */
.jp-RenderedHTML td.num, .jp-RenderedMarkdown td.num {
  font-family: var(--mono) !important;
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum' 1;
  font-size: .82rem; font-weight: 500;
  text-align: right !important;
}
.jp-RenderedHTML th.num, .jp-RenderedMarkdown th.num { text-align: right !important; }
/* linha da recomendação principal */
/* linha da recomendacao principal: tinta de fundo + filete no inicio da linha.
   Sem !important, para a tarja de prioridade da 1a coluna continuar aparecendo. */
.jp-RenderedHTML tbody tr.linha-vencedora { background: var(--destaque) !important; }
.jp-RenderedHTML tr.linha-vencedora td, .jp-RenderedHTML tr.linha-vencedora th {
  font-weight: 600;
}
.jp-RenderedHTML tr.linha-vencedora td:first-child {
  box-shadow: inset 2px 0 0 var(--coral);
}
/* rótulo de prioridade do cartão (ex.: "1ª — aposta principal") */
.jp-RenderedHTML td.rotulo, .jp-RenderedMarkdown td.rotulo {
  font-weight: 600; color: var(--ink); letter-spacing: -.005em;
}
tr.linha-vencedora td.rotulo { color: var(--accent); }
table.no-index { table-layout: auto; }
.jp-OutputArea, .jp-RenderedHTML, .jp-RenderedMarkdown { overflow-x: auto; }

/* ============================================================ imagens */
.jp-RenderedMarkdown img, .jp-RenderedHTML img, .jp-RenderedImage img, .jp-OutputArea img {
  border-radius: 12px;
  box-shadow: var(--sombra-img);
  border: 1px solid var(--line-soft);
  margin: 1.4em 0; max-width: 100%; height: auto;
  background: #fff;
}
/* mapa folium embutido */
.jp-OutputArea iframe {
  border-radius: 12px !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--sombra-img);
  max-width: 100%;
}
.leaflet-container, .leaflet-popup-content { font-family: var(--sans) !important; }

/* ============================================================ matriz do deep-dive
   As cores das células vêm do Styler (inline) e continuam mandando; aqui só o
   cabeçalho e o espaçamento seguem a linguagem do resto do documento. */
table.deep-dive { border-collapse: separate !important; border-spacing: 0 4px !important; }
table.deep-dive th, table.deep-dive td {
  font-family: var(--sans) !important;
  text-transform: none !important; letter-spacing: 0 !important;
  white-space: nowrap;
}
table.deep-dive thead th {
  background: transparent !important;
  color: var(--ink-2) !important;
  font-size: .68rem !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: .09em !important;
  text-align: center !important;
  padding: 0 14px 10px !important;
  border-bottom: 1.5px solid var(--line) !important;
}
table.deep-dive thead th.blank { border: none !important; }
table.deep-dive tbody th {
  background: transparent !important;
  color: var(--ink) !important;
  font-family: var(--mono) !important;
  font-size: .78rem !important; font-weight: 500 !important;
  text-align: left !important; padding: 14px 16px !important;
  border-bottom: none !important;
}
table.deep-dive tbody td {
  font-family: var(--mono) !important;
  font-variant-numeric: tabular-nums;
  font-size: .82rem; font-weight: 600;
  text-align: center !important;
  padding: 14px 18px; border-bottom: none !important;
  border-radius: 4px;
}

/* ============================================================ responsivo */
@media (max-width: 720px) {
  html, body { font-size: 15.5px; }
  .card { padding: 24px 20px 26px; border-radius: 12px; }
  .capa { padding: 40px 20px 24px; }
  .capa .jp-RenderedMarkdown h1 { font-size: 1.95rem; }
}
'''

# Uma célula é "numérica" quando tem dígito e nada além de dígitos, separadores e
# unidades (R$, %, m², anos, "a" de faixa). Assim '12,4% a 13,4%' e 'R$ 877.500'
# contam, mas 'meia praia', '2q' e 'baixa-fina' continuam alinhados à esquerda.
RE_NUM = re.compile(r'^[\s+\-–—]*[\d][\d\s.,%+\-–—/aRs$m²²anoº]*$', re.IGNORECASE)
RE_TEM_DIGITO = re.compile(r'\d')


def _texto(el):
    return el.get_text(' ', strip=True)


def eh_numero(txt):
    t = txt.strip()
    if not t or not RE_TEM_DIGITO.search(t):
        return False
    return bool(RE_NUM.match(t))


def limpar_vazios(soup):
    """Remove containers do Jupyter que ficaram sem conteúdo visível.

    Roda algumas vezes: ao esvaziar um filho, o pai pode passar a ser vazio.
    """
    seletores = ('.jp-OutputArea-output', '.jp-OutputArea-child', '.jp-OutputArea',
                 '.jp-Cell-outputWrapper', '.jp-Cell-inputWrapper', '.jp-Cell')
    for _ in range(4):
        removidos = 0
        for sel in seletores:
            for el in soup.select(sel):
                if _texto(el):
                    continue
                if el.find(['img', 'table', 'svg', 'iframe', 'canvas', 'video']):
                    continue
                el.decompose()
                removidos += 1
        if not removidos:
            break


def montar_cards(soup):
    """Capa + uma <section class="card"> por seção (h2).

    Só embrulha as células que o nbconvert já gerou, na mesma ordem — nenhuma
    seção é criada, removida ou renomeada.
    """
    # A classe .jp-Notebook fica no proprio <body> no template lab; o container
    # real das celulas e o pai dos .jp-Cell (um <main>/<div> mais abaixo).
    todas = soup.select('.jp-Cell')
    if not todas:
        return
    nb = todas[0].parent
    celulas = [c for c in nb.find_all(True, recursive=False)
               if c.has_attr('class') and 'jp-Cell' in c['class']]
    if not celulas:
        return

    grupos = []          # lista de (tipo, [células])
    atual = None
    for i, cel in enumerate(celulas):
        if i == 0 and cel.find('h1') is not None:
            grupos.append(('capa', [cel]))
            atual = None
            continue
        if cel.find('h2') is not None:
            atual = ('card', [cel])
            grupos.append(atual)
        elif atual is not None:
            atual[1].append(cel)
        else:
            atual = ('card', [cel])
            grupos.append(atual)

    for cel in celulas:
        cel.extract()
    for tipo, itens in grupos:
        if tipo == 'capa':
            caixa = soup.new_tag('header')
            caixa['class'] = 'capa'
        else:
            caixa = soup.new_tag('section')
            caixa['class'] = 'card'
        for it in itens:
            caixa.append(it)
        nb.append(caixa)


def marcar_tabelas(soup):
    """Classifica colunas numéricas e a linha da recomendação principal.

    Só adiciona atributos class — nenhum texto, número ou célula muda.
    """
    for tabela in soup.find_all('table'):
        linhas = tabela.select('tbody tr')
        if not linhas:
            continue
        # coluna é numérica quando a maioria das células de dados é numérica
        largura = max(len(l.find_all(['td', 'th'])) for l in linhas)
        for col in range(largura):
            valores, alvos = [], []
            for linha in linhas:
                celulas = linha.find_all(['td', 'th'])
                if col < len(celulas) and celulas[col].name == 'td':
                    valores.append(eh_numero(_texto(celulas[col])))
                    alvos.append(celulas[col])
            if not valores or sum(valores) <= len(valores) / 2:
                continue
            for td in alvos:
                td['class'] = td.get('class', []) + ['num']
            cabecalhos = tabela.select('thead tr')
            if cabecalhos:
                ths = cabecalhos[-1].find_all('th')
                if col < len(ths):
                    ths[col]['class'] = ths[col].get('class', []) + ['num']

        # linha vencedora: a que carrega o rótulo da 1ª recomendação do cartão
        for linha in linhas:
            if '1ª' in _texto(linha) and 'aposta principal' in _texto(linha):
                linha['class'] = linha.get('class', []) + ['linha-vencedora']


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

    print('2) nbconvert para HTML (notebook completo, com codigo)...')
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
    limpar_vazios(soup)

    print('4) reestruturando em cards + marcando tabelas...')
    montar_cards(soup)
    marcar_tabelas(soup)

    print('5) injetando fontes + CSS customizado...')
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
