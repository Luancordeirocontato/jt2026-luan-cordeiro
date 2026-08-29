# Exporta a sessao do Claude Code para ai-log/, a partir do arquivo de sessao que
# o proprio Claude Code grava em ~/.claude/projects/<projeto>/<sessao>.jsonl
#
# Mesma logica do exportar_ailog_opencode.py: o criterio do desafio pede a conversa
# "exportada", a "sessao inteira, nao um trecho escolhido". Nada aqui e redigido --
# o conteudo sai do arquivo de sessao na ordem em que foi gravado.
#
# Gera:
#   ai-log/claude-code-sessao-completa.jsonl  copia integral do arquivo de sessao
#   ai-log/ailogclaude.md                     a mesma conversa, legivel
#
# No .md, entradas e saidas de ferramenta muito longas sao cortadas com marca
# explicita; o .jsonl ao lado guarda tudo. Imagens coladas na conversa viram uma
# nota (o base64 fica so no .jsonl) -- print nao e transcript, o texto e que conta.
#
# Uso:  py scripts/exportar_ailog_claude.py
import glob
import io
import json
import os
import shutil
import sys

RAIZ_SESSOES = os.path.expanduser('~/.claude/projects')
SAIDA_JSONL = 'ai-log/claude-code-sessao-completa.jsonl'
SAIDA_MD = 'ai-log/ailogclaude.md'
LIMITE = 1800          # chars por entrada/saida de ferramenta no .md


def acha_sessao(repo):
    """O .jsonl mais recente da pasta de projeto correspondente a este repo."""
    slug = repo.replace(':', '').replace('\\', '-').replace('/', '-')
    candidatos = []
    for pasta in glob.glob(os.path.join(RAIZ_SESSOES, '*')):
        base = os.path.basename(pasta).lower()
        if os.path.basename(repo).lower() in base or base in slug.lower():
            candidatos += glob.glob(os.path.join(pasta, '*.jsonl'))
    if not candidatos:
        sys.exit('nenhuma sessao do Claude Code encontrada para este projeto')
    return max(candidatos, key=os.path.getsize)


def corta(txt, limite=LIMITE):
    txt = str(txt)
    if len(txt) <= limite:
        return txt
    return txt[:limite] + f'\n[... cortado aqui; {len(txt)} chars no .jsonl]'


def renderiza(bloco):
    """Um bloco de conteudo -> markdown."""
    if isinstance(bloco, str):
        return bloco
    t = bloco.get('type')
    if t == 'text':
        return bloco.get('text', '')
    if t == 'thinking':
        corpo = (bloco.get('thinking') or '').strip()
        if not corpo:
            return ''
        return '<details><summary>raciocínio interno</summary>\n\n' + corta(corpo) + '\n\n</details>'
    if t == 'tool_use':
        entrada = json.dumps(bloco.get('input', {}), ensure_ascii=False)
        return f"**ferramenta `{bloco.get('name', '?')}`**\n\n```json\n{corta(entrada)}\n```"
    if t == 'tool_result':
        conteudo = bloco.get('content')
        if isinstance(conteudo, list):
            conteudo = '\n'.join(
                c.get('text', '[imagem]') if isinstance(c, dict) else str(c) for c in conteudo)
        erro = ' (erro)' if str(bloco.get('is_error')).lower() == 'true' else ''
        return f'*resultado{erro}:*\n\n```\n{corta(conteudo)}\n```'
    if t == 'image':
        return '*[imagem colada na conversa — o binário fica no `.jsonl`]*'
    return ''


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    origem = acha_sessao(repo)
    print('sessao:', origem)

    os.makedirs(os.path.join(repo, 'ai-log'), exist_ok=True)
    shutil.copy(origem, os.path.join(repo, SAIDA_JSONL))

    linhas = []
    for ln in io.open(origem, encoding='utf-8'):
        ln = ln.strip()
        if ln:
            try:
                linhas.append(json.loads(ln))
            except ValueError:
                pass

    conversa = [d for d in linhas if d.get('type') in ('user', 'assistant')]
    n_user = sum(1 for d in conversa if d.get('type') == 'user')
    modelo = next((d.get('message', {}).get('model') for d in conversa
                   if d.get('type') == 'assistant' and d.get('message', {}).get('model')), '')

    out = ['# Sessão Claude Code — transcript exportado do arquivo de sessão',
           '',
           '**Projeto:** Jovens Talentos AI Builder 2026 — Seazone · Itapema-SC  ',
           f'**Sessão:** `{os.path.basename(origem).replace(".jsonl", "")}`  ',
           f'**Modelo:** `{modelo}`  ',
           f'**Registros na conversa:** {len(conversa)} '
           f'({n_user} do usuário, {len(conversa) - n_user} da IA)  ',
           '',
           'Exportado por `scripts/exportar_ailog_claude.py` a partir do arquivo que o '
           'próprio Claude Code grava em `~/.claude/projects/`. Nada foi reescrito: o '
           'conteúdo sai do arquivo na ordem em que foi gravado, incluindo chamadas de '
           'ferramenta, resultados e raciocínio interno. Entradas e saídas longas '
           'aparecem cortadas aqui por legibilidade — `claude-code-sessao-completa.jsonl`, '
           'ao lado, é a cópia integral.',
           '',
           '> O arquivo de sessão é gravado à medida que a conversa acontece, então a '
           'última resposta da IA (a que gerou este export) não aparece no registro: ela '
           'é justamente o commit que trouxe este arquivo para o repositório.',
           '', '---', '']

    i_user = 0
    for i, d in enumerate(conversa, 1):
        papel = d['type']
        if papel == 'user':
            i_user += 1
        etiqueta = f'você (#{i_user})' if papel == 'user' else 'IA'
        corpo = d.get('message', {}).get('content')
        blocos = corpo if isinstance(corpo, list) else [corpo]
        partes = [renderiza(b) for b in blocos if b is not None]
        partes = [p for p in partes if p and p.strip()]
        if not partes:
            continue
        out.append(f'## {i}. {etiqueta}')
        out.append('')
        out.append('\n\n'.join(partes))
        out.append('')

    io.open(os.path.join(repo, SAIDA_MD), 'w', encoding='utf-8').write('\n'.join(out))

    kb = lambda p: os.path.getsize(os.path.join(repo, p)) // 1024
    print(f'OK -> {SAIDA_JSONL} ({kb(SAIDA_JSONL)} KB)')
    print(f'OK -> {SAIDA_MD} ({kb(SAIDA_MD)} KB)')


if __name__ == '__main__':
    main()
