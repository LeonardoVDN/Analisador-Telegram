import streamlit as st
import os
import tempfile
import warnings

from helpers import (
    validate_phone_number,
    validate_api_credentials,
    validate_claude_key,
    run_async_in_thread,
)
from telegram_ops import (
    get_session_name,
    check_auth,
    send_code,
    sign_in,
    sign_in_password,
    fetch_messages,
)
from claude_analysis import CLAUDE_MODELS, analyze_with_claude
from media_processing import extract_video_urls, process_all_media
from data_preparation import prepare_analysis_input, get_media_summary
import dashboard

warnings.filterwarnings("ignore", category=RuntimeWarning)

st.set_page_config(page_title="Telegram Group Analyze MVP", layout="wide")

if "messages_data" not in st.session_state:
    st.session_state.messages_data = []
if "media_files" not in st.session_state:
    st.session_state.media_files = []
if "transcriptions" not in st.session_state:
    st.session_state.transcriptions = []
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "client_state" not in st.session_state:
    st.session_state.client_state = "disconnected"

st.sidebar.header("Configurações")

with st.sidebar.expander("Credenciais Telegram", expanded=True):
    api_id = st.text_input("API ID", value=os.getenv("TG_API_ID", ""))
    api_hash = st.text_input("API Hash", value=os.getenv("TG_API_HASH", ""), type="password")
    phone = st.text_input("Telefone (com DDI, ex: +5511999999999)", value=os.getenv("TG_PHONE", ""))

with st.sidebar.expander("Anthropic Claude AI", expanded=True):
    claude_key = st.text_input(
        "Claude API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Obtenha em: https://console.anthropic.com/settings/keys",
    )
    claude_model = st.selectbox(
        "Modelo",
        CLAUDE_MODELS,
        index=0,
        format_func=lambda x: {
            "claude-sonnet-4-5-20250929": "🔥 Claude Sonnet 4.5 (Recomendado - Melhor qualidade)",
            "claude-opus-4-6": "🧠 Claude Opus 4.6 (Máxima inteligência)",
            "claude-haiku-4-5-20251001": "⚡ Claude Haiku 4.5 (Mais rápido)",
            "claude-3-haiku-20240307": "Claude Haiku 3 (Legacy)",
        }.get(x, x),
        help="IDs oficiais dos modelos Claude 4.5/4.6 da documentação Anthropic!",
    )
    if claude_key:
        st.caption("✅ API Key configurada")

st.title("🕵️ Analisador de Grupos Telegram MVP")

if api_id and api_hash and phone:
    session_name = get_session_name(phone)

    if st.button("Verificar Conexão / Entrar"):
        phone_valid, phone_error = validate_phone_number(phone)
        if not phone_valid:
            st.error(phone_error)
        else:
            api_valid, api_error = validate_api_credentials(api_id, api_hash)
            if not api_valid:
                st.error(api_error)
            else:
                with st.spinner("Conectando ao Telegram..."):
                    try:
                        authorized, err = run_async_in_thread(check_auth, session_name, api_id, api_hash)
                        if err:
                            st.error(f"Erro na conexão: {err}")
                        elif authorized:
                            st.session_state.client_state = "connected"
                            st.success("Conectado com sucesso!")
                            st.rerun()
                        else:
                            st.info("Não autorizado. Enviando código...")
                            try:
                                ph_hash = run_async_in_thread(send_code, session_name, api_id, api_hash, phone)
                                st.session_state.phone_code_hash = ph_hash
                                st.session_state.client_state = "waiting_code"
                                st.success("Código de verificação enviado! Verifique seu app do Telegram.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao enviar código: {e}")
                    except Exception as e:
                        st.error(f"Erro crítico: {e}")

    if st.session_state.client_state == "waiting_code":
        code = st.text_input("Código enviado para o Telegram", key="auth_code")
        if st.button("Confirmar Código"):
            with st.spinner("Verificando código..."):
                try:
                    p_hash = st.session_state.get("phone_code_hash")
                    success, error_msg = run_async_in_thread(
                        sign_in, session_name, api_id, api_hash, phone, code, p_hash
                    )
                    if success:
                        st.session_state.client_state = "connected"
                        st.success("Autenticado!")
                        st.rerun()
                    elif error_msg == "2FA_REQUIRED":
                        st.session_state.client_state = "waiting_password"
                        st.warning("Verificação em duas etapas necessária.")
                        st.rerun()
                    else:
                        st.error(f"Erro na verificação: {error_msg}")
                except Exception as e:
                    st.error(f"Erro: {e}")

    if st.session_state.client_state == "waiting_password":
        password = st.text_input("Senha da Verificação em Duas Etapas", type="password")
        if st.button("Entrar com Senha"):
            with st.spinner("Verificando senha..."):
                success, err = run_async_in_thread(
                    sign_in_password, session_name, api_id, api_hash, password
                )
                if success:
                    st.session_state.client_state = "connected"
                    st.success("Autenticado!")
                    st.rerun()
                else:
                    st.error(f"Erro: {err}")

else:
    st.warning("Preencha as credenciais na barra lateral para começar.")

if st.session_state.client_state == "connected":
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        target_chat = st.text_input(
            "Link ou Username do Grupo/Canal", placeholder="ex: https://t.me/pythonbrasil"
        )
    with col2:
        msg_limit = st.number_input("Qtd. Mensagens", min_value=10, max_value=2000, value=100)

    # --- ETAPA 1: Baixar Mensagens ---
    if st.button("📥 Baixar Mensagens"):
        if not target_chat:
            st.error("Informe o grupo alvo!")
        else:
            with st.spinner("Baixando mensagens e mídias do Telegram..."):
                try:
                    media_tmp = tempfile.mkdtemp(prefix="tg_downloads_")
                    msgs, media_files, err = run_async_in_thread(
                        fetch_messages, session_name, api_id, api_hash,
                        target_chat, msg_limit, media_tmp
                    )
                    if err:
                        st.error(f"Erro ao baixar mensagens: {err}")
                    else:
                        st.session_state.messages_data = msgs
                        st.session_state.media_files = media_files
                        st.session_state.transcriptions = []

                        video_urls = extract_video_urls(msgs)
                        st.success(
                            f"{len(msgs)} mensagens baixadas! "
                            f"{len(media_files)} vídeos do chat + "
                            f"{len(video_urls)} links de vídeo encontrados."
                        )
                except Exception as e:
                    st.error(f"Erro crítico: {e}")

    if st.session_state.get("messages_data"):
        msgs_count = len(st.session_state.messages_data)
        media_count = len(st.session_state.media_files)
        video_urls = extract_video_urls(st.session_state.messages_data)
        total_videos = media_count + len(video_urls)

        st.write(f"Mensagens carregadas: {msgs_count}")

        # --- ETAPA 2: Processar Mídias (opcional) ---
        if total_videos > 0:
            st.divider()
            st.subheader("🎬 Processamento de Mídias")
            st.caption(
                f"{len(video_urls)} links de vídeo + {media_count} vídeos do chat = "
                f"{total_videos} vídeos para processar"
            )

            if st.button("🎙️ Processar Vídeos (Baixar + Transcrever)"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(current, total, message):
                    progress_bar.progress(current / total)
                    status_text.text(f"[{current}/{total}] {message}")

                with st.spinner("Processando vídeos..."):
                    try:
                        transcriptions = process_all_media(
                            st.session_state.messages_data,
                            st.session_state.media_files,
                            progress_callback=update_progress,
                        )
                        st.session_state.transcriptions = transcriptions
                        progress_bar.progress(1.0)

                        summary = get_media_summary(transcriptions)
                        if summary:
                            status_text.empty()
                            st.success(
                                f"Transcrição concluída! "
                                f"{summary['total_transcribed']} vídeos transcritos "
                                f"({summary['from_links']} de links, "
                                f"{summary['from_telegram']} do Telegram)."
                            )
                        else:
                            status_text.empty()
                            st.warning("Nenhum vídeo pôde ser transcrito.")
                    except Exception as e:
                        st.error(f"Erro no processamento de mídias: {e}")

            if st.session_state.get("transcriptions"):
                with st.expander("Ver transcrições", expanded=False):
                    for t in st.session_state.transcriptions:
                        st.markdown(f"**{t['origin']}** ({t['date']})")
                        st.text(t["transcription"][:500])
                        st.divider()

        # --- ETAPA 3: Analisar com IA ---
        st.divider()
        if st.button("🤖 Analisar com IA"):
            claude_valid, claude_error = validate_claude_key(claude_key)
            if not claude_valid:
                st.error(claude_error)
            else:
                prepared_text = prepare_analysis_input(
                    st.session_state.messages_data,
                    st.session_state.get("transcriptions", []),
                )
                with st.spinner(f"Analisando com {claude_model}..."):
                    status_box = st.empty()
                    analysis = analyze_with_claude(
                        st.session_state.messages_data,
                        claude_key,
                        claude_model,
                        status_box,
                        prepared_text=prepared_text,
                    )
                    if "error" in analysis:
                        st.error(f"Erro na análise: {analysis['error']}")
                    else:
                        st.session_state.analysis_results = analysis
                        status_box.empty()
                        model_used = analysis.get("_model_used", "desconhecido")
                        has_videos = len(st.session_state.get("transcriptions", [])) > 0
                        extra = " (com transcrições de vídeos)" if has_videos else ""
                        st.success(
                            f"✅ Análise concluída com sucesso usando o modelo "
                            f"**{model_used}**!{extra}"
                        )

if st.session_state.get("analysis_results"):
    dashboard.render(st.session_state.analysis_results)
