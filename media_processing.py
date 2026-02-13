import re
import os
import logging
import subprocess
import tempfile
import shlex

logger = logging.getLogger(__name__)

MAX_VIDEO_SIZE_MB = 100
DOWNLOAD_TIMEOUT = 60

VIDEO_URL_PATTERNS = [
    r'https?://(?:www\.)?instagram\.com/reel/[\w-]+',
    r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
    r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
    r'https?://youtu\.be/[\w-]+',
    r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
    r'https?://(?:vm\.)?tiktok\.com/[\w-]+',
    r'https?://(?:www\.)?x\.com/\w+/status/\d+',
    r'https?://(?:www\.)?twitter\.com/\w+/status/\d+',
]

COMBINED_PATTERN = re.compile('|'.join(VIDEO_URL_PATTERNS), re.IGNORECASE)

_whisper_model = None


def _get_whisper_model(model_size="base"):
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _whisper_model


def extract_video_urls(messages):
    results = []
    seen_urls = set()
    for msg in messages:
        text = msg.get("text", "")
        urls = COMBINED_PATTERN.findall(text)
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                results.append({
                    "url": url,
                    "date": msg.get("date", ""),
                    "text": text,
                })
    return results


def _is_safe_url(url):
    if not url.startswith(("http://", "https://")):
        return False
    dangerous = [";", "|", "&", "$", "`", "(", ")", "{", "}", "<", ">"]
    return not any(c in url for c in dangerous)


def download_video(url, output_dir):
    if not _is_safe_url(url):
        logger.warning("URL rejeitada por segurança: %s", url)
        return None

    try:
        output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--max-filesize", f"{MAX_VIDEO_SIZE_MB}M",
            "--socket-timeout", str(DOWNLOAD_TIMEOUT),
            "--output", output_template,
            "--quiet",
            "--no-warnings",
            url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOWNLOAD_TIMEOUT + 30,
        )
        if result.returncode != 0:
            logger.warning("yt-dlp falhou para %s: %s", url, result.stderr[:200])
            return None

        files = os.listdir(output_dir)
        video_files = [f for f in files if not f.endswith((".wav", ".mp3", ".part"))]
        if video_files:
            return os.path.join(output_dir, video_files[-1])
        return None

    except subprocess.TimeoutExpired:
        logger.warning("Timeout ao baixar: %s", url)
        return None
    except Exception as e:
        logger.warning("Erro ao baixar %s: %s", url, e)
        return None


def extract_audio(video_path, output_dir):
    try:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(output_dir, f"{base_name}.wav")
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            audio_path,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            logger.warning("ffmpeg falhou para %s: %s", video_path, result.stderr[:200])
            return None

        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            return audio_path
        return None

    except subprocess.TimeoutExpired:
        logger.warning("Timeout ao extrair áudio: %s", video_path)
        return None
    except Exception as e:
        logger.warning("Erro ao extrair áudio de %s: %s", video_path, e)
        return None


def transcribe_audio(audio_path, model_size="base"):
    try:
        model = _get_whisper_model(model_size)
        segments, info = model.transcribe(audio_path, language="pt")
        text = " ".join(segment.text.strip() for segment in segments)
        return text if text.strip() else ""
    except Exception as e:
        logger.warning("Erro ao transcrever %s: %s", audio_path, e)
        return ""


def process_all_media(messages, telegram_media_files=None, progress_callback=None):
    if telegram_media_files is None:
        telegram_media_files = []

    video_urls = extract_video_urls(messages)
    total_items = len(video_urls) + len(telegram_media_files)

    if total_items == 0:
        return []

    transcriptions = []
    processed = 0

    with tempfile.TemporaryDirectory(prefix="tg_media_") as tmp_dir:
        # Processar links de vídeo externos
        for item in video_urls:
            processed += 1
            if progress_callback:
                progress_callback(processed, total_items, f"Baixando: {item['url'][:50]}...")

            video_dir = os.path.join(tmp_dir, f"video_{processed}")
            os.makedirs(video_dir, exist_ok=True)

            video_path = download_video(item["url"], video_dir)
            if not video_path:
                logger.info("Pulando vídeo (download falhou): %s", item["url"])
                continue

            audio_path = extract_audio(video_path, video_dir)
            if not audio_path:
                logger.info("Pulando vídeo (extração de áudio falhou): %s", item["url"])
                continue

            if progress_callback:
                progress_callback(processed, total_items, f"Transcrevendo: {item['url'][:50]}...")

            text = transcribe_audio(audio_path)
            if text:
                transcriptions.append({
                    "source": "link",
                    "origin": item["url"],
                    "transcription": text,
                    "date": item["date"],
                })

        # Processar vídeos baixados diretamente do Telegram
        for media in telegram_media_files:
            processed += 1
            if progress_callback:
                progress_callback(processed, total_items, "Processando vídeo do Telegram...")

            video_path = media.get("path")
            if not video_path or not os.path.exists(video_path):
                continue

            audio_dir = os.path.join(tmp_dir, f"tg_audio_{processed}")
            os.makedirs(audio_dir, exist_ok=True)

            audio_path = extract_audio(video_path, audio_dir)
            if not audio_path:
                continue

            if progress_callback:
                progress_callback(processed, total_items, "Transcrevendo vídeo do Telegram...")

            text = transcribe_audio(audio_path)
            if text:
                transcriptions.append({
                    "source": "telegram",
                    "origin": media.get("filename", "vídeo do chat"),
                    "transcription": text,
                    "date": media.get("date", ""),
                })

    return transcriptions
