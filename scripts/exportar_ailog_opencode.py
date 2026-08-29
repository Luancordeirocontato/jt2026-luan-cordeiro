# Exporta a sessão do opencode para ai-log/ a partir do banco local do próprio
# opencode (~/.local/share/opencode/opencode.db).
#
# Por que existe: o critério do desafio pede a conversa "exportada", a "sessão
# inteira, não um trecho escolhido". Um resumo escrito depois — por mais fiel que
# seja — é justamente o que o critério exclui. Aqui nada é redigido: o conteúdo
# sai do banco como foi gravado, na ordem em que aconteceu.
#
# Gera um arquivo:
#   ai-log/opencode-sessao-completa.md    a conversa inteira, legível e SEM cortes
#
# Antes havia tambem um dump .json ao lado, e o .md cortava as saidas de ferramenta
# longas apontando para ele. Como o .json era o mesmo conteudo em outro formato, foi
# removido -- e o .md passou a sair integral, para nao depender de arquivo nenhum.
#
# Uso:  py scripts/exportar_ailog_opencode.py
import json
import os
import shutil
import sqlite3
import sys
import tempfile

DB = os.path.expanduser('~/.local/share/opencode/opencode.db')
SAIDA_MD = 'ai-log/opencode-sessao-completa.md'
LIMITE_TOOL = None       # None = sem corte: o .md e a unica copia da conversa


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
        try:
            entrada = json.dumps(estado.get('input', {}), ensure_ascii=False)
        except Exception:
            entrada = str(estado.get('input', ''))
        saida = str(estado.get('output', '') or '')
        if LIMITE_TOOL:
            entrada, saida = entrada[:LIMITE_TOOL], saida[:LIMITE_TOOL]
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

    os.makedirs(os.path.join(repo, 'ai-log'), exist_ok=True)

    # ---------------- versao legivel
    out = [f'# Sessão opencode — transcript exportado do banco local',
           '',
           f'**Projeto:** Jovens Talentos AI Builder 2026 — Seazone · Itapema-SC  ',
           f'**Sessão:** `{sid}` — {titulo}  ',
           f'**Mensagens:** {n}  ',
           '',
           'Exportado de `~/.local/share/opencode/opencode.db` por '
           '`scripts/exportar_ailog_opencode.py`. Nada foi reescrito: o conteúdo sai do '
           'banco na ordem gravada, sem cortes, com a prosa da IA, as chamadas de '
           'ferramenta (entrada e saída) e os arquivos alterados a cada passo.',
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
    print(f'OK -> {SAIDA_MD} ({kb(SAIDA_MD)} KB)')


if __name__ == '__main__':
    main()
