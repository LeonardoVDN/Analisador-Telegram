from datetime import datetime
from helpers import priority_sort_key

PRIORITY_COLORS = {
    1: {"bg": "#fee2e2", "border": "#ef4444", "label": "ALTO", "icon": "🔴"},
    2: {"bg": "#fef9c3", "border": "#eab308", "label": "MÉDIO", "icon": "🟡"},
    3: {"bg": "#dcfce7", "border": "#22c55e", "label": "BAIXO", "icon": "🟢"},
}

VIABILITY_COLORS = {
    1: {"bg": "#dcfce7", "border": "#22c55e", "label": "ALTA", "icon": "🟢"},
    2: {"bg": "#fef9c3", "border": "#eab308", "label": "MÉDIA", "icon": "🟡"},
    3: {"bg": "#fee2e2", "border": "#ef4444", "label": "BAIXA", "icon": "🔴"},
}


def generate_html_report(analysis_results):
    problemas = analysis_results.get("problemas_operacionais", [])
    solucoes = analysis_results.get("solucoes_ia_implementadas", [])
    oportunidades = analysis_results.get("oportunidades_ia", [])
    areas = analysis_results.get("areas_impactadas", [])
    links = analysis_results.get("links_ferramentas", [])
    model_used = analysis_results.get("_model_used", "N/A")
    generated_at = datetime.now().strftime("%d/%m/%Y às %H:%M")

    metrics_html = _build_metrics(problemas, solucoes, oportunidades, areas, links)
    problems_html = _build_problems(problemas)
    opportunities_html = _build_opportunities(oportunidades)
    areas_html = _build_areas(areas, problemas)
    recommendations_html = _build_recommendations(problemas, solucoes)
    links_html = _build_links(links)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório Estratégico - Oportunidades de IA</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 24px; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 32px; border-radius: 12px; margin-bottom: 24px; }}
  .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
  .header p {{ opacity: 0.8; font-size: 14px; }}
  .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .metric {{ background: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .metric .number {{ font-size: 32px; font-weight: 700; color: #1e293b; }}
  .metric .label {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
  .section {{ background: white; border-radius: 10px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .section h2 {{ font-size: 18px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; border-left: 4px solid; }}
  .card .title {{ font-weight: 600; margin-bottom: 8px; }}
  .card .details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px; color: #475569; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
  .tag {{ display: inline-block; background: #f1f5f9; padding: 4px 12px; border-radius: 6px; margin: 4px; font-size: 13px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
  th {{ background: #f8fafc; font-weight: 600; color: #475569; }}
  .urgent {{ color: #dc2626; }}
  .medium {{ color: #ca8a04; }}
  a {{ color: #2563eb; }}
  .footer {{ text-align: center; padding: 24px; color: #94a3b8; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🎯 Relatório Estratégico - Oportunidades de IA</h1>
    <p>Gerado em {generated_at} | Modelo: {model_used}</p>
  </div>

  {metrics_html}
  {problems_html}
  {opportunities_html}
  {areas_html}
  {recommendations_html}
  {links_html}

  <div class="footer">
    Relatório gerado automaticamente pelo Analisador de Grupos Telegram
  </div>
</div>
</body>
</html>"""


def _build_metrics(problemas, solucoes, oportunidades, areas, links):
    items = [
        ("🚨", len(problemas), "Problemas Operacionais"),
        ("✅", len(solucoes), "Soluções Implementadas"),
        ("💡", len(oportunidades), "Oportunidades de IA"),
        ("🏢", len(areas), "Áreas Impactadas"),
        ("🔗", len(links), "Ferramentas Mencionadas"),
    ]
    cards = ""
    for icon, count, label in items:
        cards += f'<div class="metric"><div class="number">{icon} {count}</div><div class="label">{label}</div></div>'
    return f'<div class="metrics">{cards}</div>'


def _build_problems(problemas):
    if not problemas:
        return '<div class="section"><h2>🚨 Problemas Operacionais</h2><p>Nenhum problema identificado.</p></div>'

    cards = ""
    problemas_sorted = sorted(problemas, key=lambda x: priority_sort_key(x, "impacto"))
    for i, prob in enumerate(problemas_sorted, 1):
        level = priority_sort_key(prob, "impacto")
        style = PRIORITY_COLORS.get(level, PRIORITY_COLORS[3])
        cards += f"""<div class="card" style="border-left-color: {style['border']}; background: {style['bg']}20;">
  <div class="title">#{i} {prob.get('problema', 'N/A')}</div>
  <div class="details">
    <div>📍 Área: {prob.get('area', 'N/A')}</div>
    <div>⏱️ Frequência: {prob.get('frequencia', 'N/A')}</div>
    <div>🎯 Impacto: <span class="badge" style="background:{style['bg']}; color:{style['border']}">{style['icon']} {style['label']}</span></div>
  </div>
</div>"""
    return f'<div class="section"><h2>🚨 Problemas Operacionais Priorizados</h2>{cards}</div>'


def _build_opportunities(oportunidades):
    if not oportunidades:
        return '<div class="section"><h2>💡 Oportunidades de IA</h2><p>Nenhuma oportunidade identificada.</p></div>'

    cards = ""
    oport_sorted = sorted(oportunidades, key=lambda x: priority_sort_key(x, "viabilidade"))
    for i, oport in enumerate(oport_sorted, 1):
        level = priority_sort_key(oport, "viabilidade")
        style = VIABILITY_COLORS.get(level, VIABILITY_COLORS[3])
        cards += f"""<div class="card" style="border-left-color: {style['border']}; background: {style['bg']}20;">
  <div class="title">💡 Oportunidade {i}: {oport.get('oportunidade', 'N/A')}</div>
  <div class="details">
    <div>🎯 Problema alvo: {oport.get('problema_alvo', 'N/A')}</div>
    <div>📊 Viabilidade: <span class="badge" style="background:{style['bg']}; color:{style['border']}">{style['icon']} {style['label']}</span></div>
  </div>
</div>"""
    return f'<div class="section"><h2>💡 Oportunidades de Automação com IA</h2>{cards}</div>'


def _build_areas(areas, problemas):
    if not areas:
        return ""

    area_count = {}
    for prob in problemas:
        area = prob.get("area", "Não especificado")
        area_count[area] = area_count.get(area, 0) + 1

    if area_count:
        rows = ""
        for area, count in sorted(area_count.items(), key=lambda x: x[1], reverse=True):
            rows += f"<tr><td>{area}</td><td>{count}</td></tr>"
        table = f"<table><thead><tr><th>Área</th><th>Problemas Identificados</th></tr></thead><tbody>{rows}</tbody></table>"
    else:
        tags = "".join(f'<span class="tag">{a}</span>' for a in areas)
        table = tags

    return f'<div class="section"><h2>🏢 Análise por Área/Departamento</h2>{table}</div>'


def _build_recommendations(problemas, solucoes):
    if not problemas:
        return ""

    content = "<h3>Priorização Sugerida:</h3>"

    prob_altos = [p for p in problemas if priority_sort_key(p, "impacto") == 1]
    prob_medios = [p for p in problemas if priority_sort_key(p, "impacto") == 2]

    if prob_altos:
        items = "".join(
            f"<li>{p.get('problema', 'N/A')} ({p.get('area', 'N/A')})</li>"
            for p in prob_altos[:3]
        )
        content += f'<p class="urgent"><strong>🔴 URGENTE ({len(prob_altos)} problemas):</strong></p><ul>{items}</ul>'

    if prob_medios:
        items = "".join(
            f"<li>{p.get('problema', 'N/A')} ({p.get('area', 'N/A')})</li>"
            for p in prob_medios[:3]
        )
        content += f'<p class="medium"><strong>🟡 MÉDIO PRAZO ({len(prob_medios)} problemas):</strong></p><ul>{items}</ul>'

    if solucoes:
        content += (
            f"<p><strong>💡 APROVEITAR SUCESSOS:</strong> "
            f"Você já tem {len(solucoes)} solução(ões) implementada(s). "
            f"Considere replicar esses padrões para problemas similares.</p>"
        )

    return f'<div class="section"><h2>🎯 Recomendações</h2>{content}</div>'


def _build_links(links):
    if not links:
        return ""
    items = "".join(f'<li><a href="{link}" target="_blank">{link}</a></li>' for link in links)
    return f'<div class="section"><h2>🔗 Ferramentas e Recursos</h2><ul>{items}</ul></div>'
