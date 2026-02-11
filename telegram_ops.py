from contextlib import asynccontextmanager
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


def get_session_name(phone_number):
    clean_phone = "".join(filter(str.isdigit, phone_number))
    return f"session_{clean_phone}"


@asynccontextmanager
async def telegram_client(session_name, api_id, api_hash):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


async def check_auth(session_name, api_id, api_hash):
    async with telegram_client(session_name, api_id, api_hash) as client:
        try:
            authorized = await client.is_user_authorized()
            return authorized, None
        except Exception as e:
            return False, str(e)


async def send_code(session_name, api_id, api_hash, phone):
    async with telegram_client(session_name, api_id, api_hash) as client:
        req = await client.send_code_request(phone)
        return req.phone_code_hash


async def sign_in(session_name, api_id, api_hash, phone, code, phone_code_hash):
    async with telegram_client(session_name, api_id, api_hash) as client:
        try:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            return True, None
        except SessionPasswordNeededError:
            return False, "2FA_REQUIRED"
        except Exception as e:
            return False, str(e)


async def sign_in_password(session_name, api_id, api_hash, password):
    async with telegram_client(session_name, api_id, api_hash) as client:
        try:
            await client.sign_in(password=password)
            return True, None
        except Exception as e:
            return False, str(e)


async def fetch_messages(session_name, api_id, api_hash, entity, limit):
    async with telegram_client(session_name, api_id, api_hash) as client:
        msgs = []
        try:
            try:
                chat = await client.get_entity(entity)
            except ValueError:
                raise Exception(f"Não foi possível encontrar o grupo/canal: {entity}")

            async for message in client.iter_messages(chat, limit=limit):
                if message.text:
                    msgs.append({
                        "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "sender_id": message.sender_id,
                        "text": message.text,
                    })
            return msgs, None
        except Exception as e:
            return [], str(e)
