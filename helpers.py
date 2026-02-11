import asyncio
import threading
import queue

PRIORITY_ORDER = {
    "alto": 1, "alta": 1,
    "médio": 2, "medio": 2, "média": 2, "media": 2,
    "baixo": 3, "baixa": 3,
}


def priority_sort_key(item, field):
    return PRIORITY_ORDER.get(item.get(field, "").lower(), 3)


def priority_color(level, invert=False):
    l = level.lower()
    high = l in ("alto", "alta")
    mid = l in ("médio", "medio", "média", "media")
    if invert:
        return "🟢" if high else ("🟡" if mid else "🔴")
    return "🔴" if high else ("🟡" if mid else "🟢")


def validate_phone_number(phone):
    if not phone:
        return False, "Número de telefone não informado"
    if not phone.startswith("+"):
        return False, "Número deve começar com + (ex: +5511999999999)"
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 10:
        return False, "Número deve ter pelo menos 10 dígitos"
    return True, None


def validate_api_credentials(api_id, api_hash):
    if not api_id or not api_id.strip():
        return False, "API ID não informado"
    if not api_hash or not api_hash.strip():
        return False, "API Hash não informado"
    return True, None


def validate_claude_key(key):
    if not key or not key.strip():
        return False, "Claude API Key não informada"
    if not key.startswith("sk-ant-"):
        return False, "API Key inválida. Deve começar com 'sk-ant-'"
    if len(key) < 40:
        return False, "API Key parece inválida (muito curta)"
    return True, None


def run_async_in_thread(async_func, *args):
    result_queue = queue.Queue()

    def target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_func(*args))
            result_queue.put(("success", result))
        except Exception as e:
            result_queue.put(("error", e))
        finally:
            loop.close()

    t = threading.Thread(target=target)
    t.start()
    t.join()

    status, value = result_queue.get()
    if status == "error":
        raise value
    return value
