{%- extends 'null.j2' -%}

{% block header %}
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Análise Itapema — Seazone (sem código)</title>
<style>
  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 960px;
         margin: 40px auto; padding: 0 24px; color: #222; line-height: 1.6; }
  h1 { font-size: 1.8em; border-bottom: 2px solid #eee; padding-bottom: .3em; }
  h2 { font-size: 1.35em; margin-top: 1.6em; color: #0a4d8c; }
  h3 { font-size: 1.1em; }
  table { border-collapse: collapse; margin: 1em 0; width: 100%; font-size: .92em; }
  th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: right; }
  th { background: #f4f4f4; }
  tr:nth-child(even) { background: #fafafa; }
  img { max-width: 100%; height: auto; }
  pre, code { background:#f6f6f6; border-radius:4px; padding:2px 6px; font-size:.9em; }
  blockquote { border-left: 4px solid #ccc; margin-left:0; padding-left:14px; color:#555; }
  hr { border:none; border-top:1px solid #eee; margin:2em 0; }
  .cell-output { margin: .6em 0; }
  .n { color:#888; font-size:.8em; }
</style>
</head>
<body>
{% endblock header %}

{% block body %}
{{ super() }}
{% endblock body %}

{% block any_cell scoped %}
{% if cell.cell_type == 'markdown' or cell.cell_type == 'raw' %}
  {{ super() }}
{% elif cell.cell_type == 'code' %}
  {# mostra apenas outputs (sem o source) #}
  {% if cell.outputs %}
  <div class="cell-output">
  {% for output in cell.outputs %}
    {% if output.output_type == 'stream' %}
      <pre>{{ output.text }}</pre>
    {% elif output.output_type in ['execute_result', 'display_data'] %}
      {% for mime, data in output.data.items() %}
        {% if mime == 'text/html' %}
          <div>{{ data }}</div>
        {% elif mime == 'image/png' %}
          <img src="data:image/png;base64,{{ data }}">
        {% elif mime == 'text/plain' %}
          <pre>{{ data }}</pre>
        {% endif %}
      {% endfor %}
    {% elif output.output_type == 'error' %}
      <pre style="color:#b00">ERRO: {{ output.ename }}: {{ output.evalue }}</pre>
    {% endif %}
  {% endfor %}
  </div>
  {% endif %}
{% endif %}
{% endblock any_cell %}

{% block footer %}
</body>
</html>
{% endblock footer %}