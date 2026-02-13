MAX_TOTAL_CHARS = 12000
TEXT_PRIORITY_RATIO = 0.6


def prepare_analysis_input(messages, transcriptions=None):
    if transcriptions is None:
        transcriptions = []

    text_section = _build_text_section(messages)
    video_section = _build_video_section(transcriptions)

    if not video_section:
        return text_section[:MAX_TOTAL_CHARS]

    text_limit = int(MAX_TOTAL_CHARS * TEXT_PRIORITY_RATIO)
    video_limit = MAX_TOTAL_CHARS - min(len(text_section), text_limit)

    truncated_text = text_section[:text_limit]
    truncated_video = video_section[:video_limit]

    return f"{truncated_text}\n\n{truncated_video}"


def _build_text_section(messages):
    if not messages:
        return ""

    lines = ["MENSAGENS DE TEXTO DO GRUPO:", ""]
    for msg in messages:
        date = msg.get("date", "")
        text = msg.get("text", "")
        lines.append(f"[{date}] {text}")

    return "\n".join(lines)


def _build_video_section(transcriptions):
    if not transcriptions:
        return ""

    lines = [
        "TRANSCRIÇÕES DE VÍDEOS COMPARTILHADOS NO GRUPO:",
        "(Conteúdo extraído automaticamente dos vídeos enviados nas mensagens)",
        "",
    ]
    for t in transcriptions:
        source = t.get("origin", "desconhecido")
        date = t.get("date", "")
        text = t.get("transcription", "")
        if text:
            lines.append(f"[{date}] Vídeo ({source}):")
            lines.append(f"  {text}")
            lines.append("")

    return "\n".join(lines)


def get_media_summary(transcriptions):
    if not transcriptions:
        return None

    total = len(transcriptions)
    from_links = sum(1 for t in transcriptions if t.get("source") == "link")
    from_telegram = sum(1 for t in transcriptions if t.get("source") == "telegram")

    return {
        "total_transcribed": total,
        "from_links": from_links,
        "from_telegram": from_telegram,
    }
