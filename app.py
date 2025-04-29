import asyncio
import logging
import sys
import requests
from urllib.parse import quote_plus
from json import dumps
from aiogram import types, Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from json import JSONDecodeError
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Token va adminlar ro‘yxati
# TOKEN = config('BOT_TOKEN')
# ADMINS = config('ADMINS').split(" ")

TOKEN='8102263265:AAEaCVYBJ8zi8dJiNKx8y9fc1bTp9stba3Y'
ADMINS=['816660001']
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class GetData(StatesGroup):
    start = State()
    final = State()

@dp.message(Command('start'))
async def get_message(msg: types.Message):
    btn = ReplyKeyboardBuilder()
    btn.button(text="Username Kiriting")
    await msg.answer("Assalamu Aleykum! Botga xush kelibsiz! 👋", reply_markup=btn.as_markup(resize_keyboard=True, one_time_keyboard=True))

@dp.message(F.text == 'Username Kiriting')
async def get_start(message: types.Message,  state: FSMContext):
    await message.answer("Iltimos, Instagram username kiriting:")
    await state.set_state(GetData.start)





@dp.message(GetData.start)
async def get_state1(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username:
        await message.answer("⚠️ Iltimos, Instagram username to'g'ri kiriting!")
        return
    await state.update_data(username=username)
    await message.answer("Session ID kiriting:")
    await state.set_state(GetData.final)


def advanced_lookup(username):
    """
    Post to get obfuscated login information from Instagram.
    Args:
        username (str): The Instagram username for the search.
    Returns:
        dict: Contains 'user' data or error message.
    """
    data = "signed_body=SIGNATURE." + quote_plus(dumps(
        {"q": username, "skip_recovery": "1"},
        separators=(",", ":")
    ))

    try:
        api = requests.post(
            'https://i.instagram.com/api/v1/users/lookup/',
            headers={
                "Accept-Language": "en-US",
                "User-Agent": "Instagram 101.0.0.15.120",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-IG-App-ID": "124024574287414",
                "Accept-Encoding": "gzip, deflate",
                "Host": "i.instagram.com",
                "Connection": "keep-alive",
                "Content-Length": str(len(data))
            },
            data=data
        )
        api.raise_for_status()
        return {"user": api.json(), "error": None}

    except requests.exceptions.RequestException as e:
        return {"user": None, "error": str(e)}

def display_user_info(infos):
    result = []
    result.append(f"👤 *Informations about* : {infos.get('username', 'N/A')}")
    result.append(f"🆔 *UserID* : {infos.get('id', 'N/A')}")
    result.append(f"📛 *Full Name* : {infos.get('full_name', 'N/A')}")
    result.append(f"✅ *Verified* : {infos.get('is_verified', 'N/A')} | 🏢 *Business* : {infos.get('is_business', 'N/A')}")
    result.append(f"🔒 *Private* : {infos.get('is_private', 'N/A')}")
    result.append(f"👥 *Followers* : {infos.get('follower_count', 'N/A')} | 🏃 *Following* : {infos.get('following_count', 'N/A')}")
    result.append(f"📸 *Posts* : {infos.get('media_count', 'N/A')}")
    result.append(f"🔗 *External URL* : {infos.get('external_url', 'None')}")
    result.append(f"📺 *IGTV Posts* : {infos.get('total_igtv_videos', 'N/A')}")
    result.append(f"📝 *Biography* : {infos.get('biography', 'None')}")

    if infos.get("public_email"):
        result.append(f"📧 *Public Email* : {infos['public_email']}")
    else:
        result.append("📧 *Public Email* : None")

    if infos.get("public_phone_number"):
        phonenr = f"+{infos.get('public_phone_country_code', '')} {infos['public_phone_number']}"
        result.append(f"📞 *Public Phone* : {phonenr}")
    else:
        result.append("📞 *Public Phone* : None")

    # Advanced lookup
    other_infos = advanced_lookup(infos.get("username", ""))

    if other_infos["error"] == "rate limit":
        result.append("⚠️ *Rate limit!* Please wait a few minutes and try again.")
    elif other_infos["user"] and "message" in other_infos["user"]:
        if other_infos["user"]["message"] == "No users found":
            result.append("❌ *Lookup failed!* No users found.")
        else:
            result.append(other_infos["user"]["message"])
    else:
        if other_infos["user"] and other_infos["user"].get("obfuscated_email"):
            result.append(f"🔒 *Obfuscated Email* : {other_infos['user']['obfuscated_email']}")
        else:
            result.append("🔒 *Obfuscated Email* : None")

        if other_infos["user"] and other_infos["user"].get("obfuscated_phone"):
            result.append(f"📵 *Obfuscated Phone* : {other_infos['user']['obfuscated_phone']}")
        else:
            result.append("📵 *Obfuscated Phone* : None")


    if infos.get("hd_profile_pic_url_info", {}).get("url"):
        result.append(f"🖼 *Profile Picture* : {infos['hd_profile_pic_url_info']['url']}")
    else:
        result.append("🖼 *Profile Picture* : None")

    return "\n".join(result)



@dp.message(GetData.final)
async def get_instagram_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    session_id = message.text.strip()
    await message.answer(text="Malumotlar yuklanmooqda kuting ⏰")
    user_data = get_user_id(username, session_id)
    if user_data["error"]:
        await message.answer(f"Xatolik: {user_data['error']}")
        return

    user_id = user_data["id"]
    print("User ID:", user_id)

    user_info = get_user_info(user_id, session_id)
    if user_info["error"]:
        await message.answer(f"Xatolik: {user_info['error']}")
        return

    infos = user_info["user"]
    user_text = display_user_info(infos)
    await message.answer(user_text)
    await state.clear()

def get_user_id(username, session_id):
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 Android",
        "x-ig-app-id": "936619743392459"
    }
    cookies = {"sessionid": session_id}
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        user_data = response.json()
        user_id = user_data["data"]["user"]["id"]
        return {"id": user_id, "error": None}
    except requests.exceptions.RequestException as e:
        return {"id": None, "error": str(e)}

def get_user_info(user_id, session_id):
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 Android",
        "x-ig-app-id": "936619743392459"
    }
    cookies = {"sessionid": session_id}
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        user_data = response.json()

        if "user" in user_data:
            return {"user": user_data["user"], "error": None}
        else:
            return {"user": None, "error": "To'liq ma'lumot topilmadi"}

    except requests.exceptions.RequestException as e:
        return {"user": None, "error": str(e)}

async def start():
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text="Bot faollashdi! ✅")
        except Exception:
            pass

async def shutdown():
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text="Bot to'xtadi! ❌")
        except Exception:
            pass

async def main():
    dp.startup.register(start)
    dp.shutdown.register(shutdown)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[logging.FileHandler("bot.log"),
                                  logging.StreamHandler(sys.stdout)])
    asyncio.run(main())
