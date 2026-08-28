# Exporta a sessão do opencode para ai-log/ a partir do banco local do próprio
# opencode (~/.local/share/opencode/opencode.db).
#
# Por que existe: o critério do desafio pede a conversa "exportada", a "sessão
# inteira, não um trecho escolhido". Um resumo escrito depois — por mais fiel que
# seja — é justamente o que o critério exclui. Aqui nada é redigido: o conteúdo
# sai do banco como foi gravado, na ordem em que aconteceu.
#
# Gera dois arquivos:
#   ai-log/opencode-sessao-completa.json  dump integral, sem nenhum corte
#   ai-log/opencode-sessao-completa.md    a mesma conversa, legível
#
# No .md as saídas de ferramenta muito longas (leitura de CSV, dumps) são cortadas
# com marca explícita, e o .json ao lado guarda tudo — o corte é de leitura, nunca
# de conteúdo.
#
# Uso:  py scripts/exportar_ailog_opencode.py
import json
import os
import shutil
import sqlite3
import sys
import tempfile

DB = os.path.expanduser('~/.local/share/opencode/opencode.db')
SAIDA_JSON = 'ai-log/opencode-sessao-completa.json'
SAIDA_MD = 'ai-log/opencode-sessao-completa.md'
LIMITE_TOOL = 2000       # chars por saída de ferramenta no .md


def abrir_copia(db):
    """Copia o banco (com -wal/-shm) para ler sem disputar lock com o opencode."""
    if not os.path.exists(db):
        sys.exit(f'banco do opencode nao encontrado em {db}')
    tmp = os.path.join(tempfile.gettempdir(), 'opencode_export.db')
    for ext in ('', '-wal', '-shm'):
        if os.path.exists(db + ext):
            shutil.copy(db + ext, tmp + ext)
    return sqlite3.connect(tmp)


def maior_sessao(cur, diretorio):
    """A sessão com mais mensagens dentro do diretório do projeto."""
    linhas = cur.execute('select id, title, directory from session').fetchall()
    alvo = os.path.basename(diretorio).lower()
    melhor, melhor_n = None, -1
    for sid, titulo, d in linhas:
        if d and alvo not in str(d).lower():
            continue
        n = cur.execute('select count(*) from message where session_id=?', (sid,)).fetchone()[0]
        if n > melhor_n:
            melhor, melhor_n = (sid, titulo, d), n
    if melhor is None:
        sys.exit('nenhuma sessao do opencode encontrada para este projeto')
    return melhor, melhor_n


def texto_da_parte(d):
    """Renderiza uma parte da mensagem em markdown."""
    tipo = d.get('type')
    if tipo == 'text':
        return d.get('text', '')
    if tipo == 'reasoning':
        corpo = d.get('text', '').strip()
        return f'<details><summary>raciocínio interno</summary>\n\n{corpo}\n\n</details>' if corpo else ''
    if tipo == 'tool':
        estado = d.get('state') or {}
        nome = d.get('tool') or estado.get('title') or 'ferramenta'
        entrada = estada = ''
        try:
            entrada = json.dumps(estado.get('input', {}), ensure_ascii=False)[:LIMITE_TOOL]
        except Exception:
            entrada = str(estado.get('input', ''))[:LIMITE_TOOL]
        saida = str(estado.get('output', '') or '')
        cortada = len(saida) > LIMITE_TOOL
        if cortada:
            saida = saida[:LIMITE_TOOL] + f'\n[... saída cortada aqui; {len(str(estado.get("output","")))} chars no .json]'
        bloco = [f'**ferramenta `{nome}`**']
        if entrada:
            bloco.append(f'```json\n{entrada}\n```')
        if saida.strip():
            bloco.append(f'```\n{saida}\n```')
        return '\n\n'.join(bloco)
    if tipo == 'patch':
        arqs = d.get('files') or []
        return f'*alterou:* `{"`, `".join(map(str, arqs))}`' if arqs else '*aplicou patch*'
    if tipo == 'file':
        return f'*anexou arquivo:* `{d.get("filename", "")}`'
    return ''


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    con = abrir_copia(DB)
    cur = con.cursor()
    (sid, titulo, diretorio), n = maior_sessao(cur, repo)
    print(f'sessao: {sid}\ntitulo: {titulo}\nmensagens: {n}')

    msgs = cur.execute(
        'select id, data, time_created from message where session_id=? order by time_created, id',
        (sid,)).fetchall()
    partes = {}
    for mid, pdata, tc in cur.execute(
            'select message_id, data, time_created from part where session_id=? order by time_created, id',
            (sid,)):
        partes.setdefault(mid, []).append(json.loads(pdata))

    # ---------------- dump integral
    bruto = {'session_id': sid, 'title': titulo, 'directory': diretorio,
             'mensagens': [{'id': mid, 'time_created': tc,
                            'data': json.loads(md),
                            'parts': partes.get(mid, [])}
                           for mid, md, tc in msgs]}
    os.makedirs(os.path.join(repo, 'ai-log'), exist_ok=True)
    with open(os.path.join(repo, SAIDA_JSON), 'w', encoding='utf-8') as f:
        # compacto: o .md e a versao de leitura; aqui o que importa e ser integral
        json.dump(bruto, f, ensure_ascii=False, separators=(',', ':'))

    # ---------------- versao legivel
    out = [f'# Sessão opencode — transcript exportado do banco local',
           '',
           f'**Projeto:** Jovens Talentos AI Builder 2026 — Seazone · Itapema-SC  ',
           f'**Sessão:** `{sid}` — {titulo}  ',
           f'**Mensagens:** {n}  ',
           '',
           'Exportado de `~/.local/share/opencode/opencode.db` por '
           '`scripts/exportar_ailog_opencode.py`. Nada foi reescrito: o conteúdo sai do '
           'banco na ordem gravada. Saídas de ferramenta muito longas aparecem cortadas '
           'aqui por legibilidade — `opencode-sessao-completa.json`, ao lado, tem tudo.',
           '', '---', '']
    n_user = 0
    for i, (mid, md, tc) in enumerate(msgs, 1):
        d = json.loads(md)
        papel = d.get('role', '?')
        if papel == 'user':
            n_user += 1
        etiqueta = f'você (#{n_user})' if papel == 'user' else 'IA'
        modelo = d.get('model') or ''
        cab = f'## {i}. {etiqueta}' + (f' · `{modelo}`' if modelo and papel != 'user' else '')
        corpo = [texto_da_parte(p) for p in partes.get(mid, [])]
        corpo = [c for c in corpo if c and c.strip()]
        if not corpo:
            continue
        out.append(cab)
        out.append('')
        out.extend(['\n'.join(corpo), ''])
    with open(os.path.join(repo, SAIDA_MD), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))

    kb = lambda p: os.path.getsize(os.path.join(repo, p)) // 1024
    print(f'OK -> {SAIDA_JSON} ({kb(SAIDA_JSON)} KB)')
    print(f'OK -> {SAIDA_MD} ({kb(SAIDA_MD)} KB)')


if __name__ == '__main__':
    main()
