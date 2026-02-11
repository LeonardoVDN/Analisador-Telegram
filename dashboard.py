import streamlit as st
import pandas as pd
from helpers import priority_sort_key, priority_color


def render(res):
    st.divider()
    st.header("🎯 Dashboard Estratégico - Oportunidades de IA")

    model_used = res.get("_model_used")
    if model_used:
        st.caption(f"🤖 Análise realizada com: **{model_used}**")

    problemas = res.get("problemas_operacionais", [])
    solucoes = res.get("solucoes_ia_implementadas", [])
    oportunidades = res.get("oportunidades_ia", [])
    areas = res.get("areas_impactadas", [])
    links = res.get("links_ferramentas", [])

    _render_metrics(problemas, solucoes, oportunidades, areas, links)
    st.divider()
    _render_problems(problemas)
    st.divider()
    _render_solutions(solucoes)
    st.divider()
    _render_opportunities(oportunidades)
    st.divider()
    _render_areas(areas, problemas)
    st.divider()
    _render_recommendations(problemas, solucoes)
    st.divider()
    _render_links(links)
    _render_raw_data()
    _render_debug(res)


def _render_metrics(problemas, solucoes, oportunidades, areas, links):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("🚨 Problemas Operacionais", len(problemas))
    with c2:
        st.metric("✅ Soluções Implementadas", len(solucoes))
    with c3:
        st.metric("💡 Oportunidades de IA", len(oportunidades))
    with c4:
        st.metric("🏢 Áreas Impactadas", len(areas))
    with c5:
        st.metric("🔗 Ferramentas Mencionadas", len(links))


def _render_problems(problemas):
    st.subheader("🚨 Problemas Operacionais Priorizados")
    if not problemas:
        st.info("Nenhum problema operacional identificado nas mensagens.")
        return

    problemas_sorted = sorted(problemas, key=lambda x: priority_sort_key(x, "impacto"))
    for i, prob in enumerate(problemas_sorted, 1):
        impacto = prob.get("impacto", "baixo")
        cor = priority_color(impacto)

        with st.expander(f"{cor} #{i} - {prob.get('problema', 'N/A')[:80]}...", expanded=(i <= 3)):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📍 Área:** {prob.get('area', 'Não especificado')}")
                st.markdown(f"**⏱️ Frequência:** {prob.get('frequencia', 'Não especificado')}")
            with col2:
                st.markdown(f"**🎯 Impacto:** {cor} {impacto.upper()}")
            st.markdown(f"**📝 Descrição:** {prob.get('problema', 'N/A')}")


def _render_solutions(solucoes):
    st.subheader("✅ Soluções com IA Já Implementadas")
    if not solucoes:
        st.info("Nenhuma solução com IA mencionada nas mensagens.")
        return

    for i, sol in enumerate(solucoes, 1):
        with st.expander(f"✅ Solução {i}: {sol.get('solucao', 'N/A')}", expanded=True):
            st.markdown(f"**🎯 Problema resolvido:** {sol.get('problema_resolvido', 'N/A')}")
            st.markdown(f"**📊 Resultado:** {sol.get('resultado', 'N/A')}")
            st.markdown(f"**🛠️ Ferramenta:** {sol.get('ferramenta', 'N/A')}")


def _render_opportunities(oportunidades):
    st.subheader("💡 Oportunidades de Automação com IA")
    if not oportunidades:
        st.info("Nenhuma oportunidade de IA identificada nas mensagens.")
        return

    oport_sorted = sorted(oportunidades, key=lambda x: priority_sort_key(x, "viabilidade"))
    for i, oport in enumerate(oport_sorted, 1):
        viab = oport.get("viabilidade", "baixa")
        cor = priority_color(viab, invert=True)

        with st.container():
            st.markdown(f"### {cor} Oportunidade {i}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**💡 Oportunidade:** {oport.get('oportunidade', 'N/A')}")
                st.markdown(f"**🎯 Problema alvo:** {oport.get('problema_alvo', 'N/A')}")
            with col2:
                st.markdown(f"**📊 Viabilidade:** {cor} {viab.upper()}")
            st.divider()


def _render_areas(areas, problemas):
    st.subheader("🏢 Análise por Área/Departamento")
    if not areas:
        st.info("Nenhuma área específica identificada.")
        return

    area_count = {}
    for prob in problemas:
        area = prob.get("area", "Não especificado")
        area_count[area] = area_count.get(area, 0) + 1

    if area_count:
        df_areas = pd.DataFrame([
            {"Área": area, "Problemas Identificados": count}
            for area, count in sorted(area_count.items(), key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(df_areas, use_container_width=True)
    else:
        st.write(", ".join(areas))


def _render_recommendations(problemas, solucoes):
    st.subheader("🎯 Recomendações - O que Desenvolver Primeiro")
    if not problemas:
        st.info("Sem dados suficientes para recomendações.")
        return

    st.markdown("### Priorização Sugerida:")

    prob_altos = [p for p in problemas if priority_sort_key(p, "impacto") == 1]
    prob_medios = [p for p in problemas if priority_sort_key(p, "impacto") == 2]

    if prob_altos:
        st.markdown(f"**🔴 URGENTE ({len(prob_altos)} problemas):**")
        for p in prob_altos[:3]:
            st.markdown(f"- {p.get('problema', 'N/A')} ({p.get('area', 'N/A')})")

    if prob_medios:
        st.markdown(f"\n**🟡 MÉDIO PRAZO ({len(prob_medios)} problemas):**")
        for p in prob_medios[:3]:
            st.markdown(f"- {p.get('problema', 'N/A')} ({p.get('area', 'N/A')})")

    if solucoes:
        st.markdown(f"\n**💡 APROVEITAR SUCESSOS:**")
        st.markdown(
            f"Você já tem {len(solucoes)} solução(ões) implementada(s). "
            "Considere replicar esses padrões para problemas similares."
        )


def _render_links(links):
    st.subheader("🔗 Ferramentas e Recursos Mencionados")
    if links:
        for link in links:
            st.markdown(f"- {link}")
    else:
        st.info("Nenhum link de ferramenta compartilhado.")


def _render_raw_data():
    with st.expander("📄 Ver dados brutos (Mensagens originais)"):
        df = pd.DataFrame(st.session_state.get("messages_data", []))
        st.dataframe(df, use_container_width=True)


def _render_debug(res):
    raw_response = res.get("_raw_response")
    if raw_response:
        with st.expander("🔍 Debug: Resposta bruta do modelo (JSON)"):
            st.code(raw_response, language="json")
