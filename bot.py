import requests
import time
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "-1004475315451"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

users = {}
offset = 0


def send_message(chat_id, text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text
        }
    )


def send_to_channel(text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        data={
            "chat_id": CHANNEL_ID,
            "text": text
        }
    )


def copy_message_to_channel(from_chat_id, message_id):
    response = requests.post(
        f"{BASE_URL}/copyMessage",
        data={
            "chat_id": CHANNEL_ID,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
    )

    return response.json()


print("ربات روشن شد.")
print("منتظر پیام کاربران هستیم...")


while True:

    try:

        response = requests.get(
            f"{BASE_URL}/getUpdates",
            params={
                "offset": offset,
                "timeout": 30
            },
            timeout=40
        )

        data = response.json()

        if not data.get("ok"):
            print("Telegram Error:", data)
            time.sleep(3)
            continue

        for update in data["result"]:

            offset = update["update_id"] + 1

            message = update.get("message")

            if not message:
                continue

            chat = message.get("chat")

            if chat.get("type") != "private":
                continue

            chat_id = chat["id"]

            user = message.get("from", {})
            username = user.get("username", "")

            text = message.get("text", "")

            # شروع
            if text == "/start":

                users[chat_id] = {
                    "step": "name",
                    "name": None
                }

                send_message(
                    chat_id,
                    "سلام 👋\n\n"
                    "برای ثبت پرداخت، لطفاً نام و نام خانوادگی خود را وارد کنید:"
                )

                continue

            # اگر کاربر هنوز شروع نکرده
            if chat_id not in users:

                send_message(
                    chat_id,
                    "لطفاً ابتدا روی /start بزنید."
                )

                continue

            state = users[chat_id]

            # دریافت نام
            if state["step"] == "name":

                if not text:

                    send_message(
                        chat_id,
                        "لطفاً نام و نام خانوادگی را به صورت متنی ارسال کنید."
                    )

                    continue

                state["name"] = text
                state["step"] = "receipt"

                send_message(
                    chat_id,
                    "ممنون 🌹\n\n"
                    "حالا لطفاً تصویر یا فایل PDF رسید واریز را ارسال کنید 📎"
                )

                continue

            # دریافت رسید
            if state["step"] == "receipt":

                # عکس
                if "photo" in message:

                    info = (
                        "🧾 رسید پرداخت جدید\n\n"
                        f"👤 نام: {state['name']}"
                    )

                    if username:
                        info += f"\n📱 Username: @{username}"

                    send_to_channel(info)

                    result = copy_message_to_channel(
                        chat_id,
                        message["message_id"]
                    )

                    if result.get("ok"):

                        send_message(
                            chat_id,
                            "✅ رسید شما با موفقیت ثبت شد.\n\n"
                            "رسید برای بررسی ارسال شد."
                        )

                    else:

                        send_message(
                            chat_id,
                            "⚠️ اطلاعات شما ثبت شد، "
                            "اما ارسال فایل رسید با مشکل مواجه شد."
                        )

                    del users[chat_id]

                    continue

                # PDF
                if "document" in message:

                    document = message["document"]

                    file_name = document.get("file_name", "")

                    if not file_name.lower().endswith(".pdf"):

                        send_message(
                            chat_id,
                            "لطفاً رسید را به صورت تصویر یا فایل PDF ارسال کنید."
                        )

                        continue

                    info = (
                        "🧾 رسید پرداخت جدید\n\n"
                        f"👤 نام: {state['name']}\n"
                        f"📄 فایل: {file_name}"
                    )

                    if username:
                        info += f"\n📱 Username: @{username}"

                    send_to_channel(info)

                    result = copy_message_to_channel(
                        chat_id,
                        message["message_id"]
                    )

                    if result.get("ok"):

                        send_message(
                            chat_id,
                            "✅ رسید شما با موفقیت ثبت شد.\n\n"
                            "رسید برای بررسی ارسال شد."
                        )

                    else:

                        send_message(
                            chat_id,
                            "⚠️ اطلاعات شما ثبت شد، "
                            "اما ارسال فایل رسید با مشکل مواجه شد."
                        )

                    del users[chat_id]

                    continue

                send_message(
                    chat_id,
                    "لطفاً فقط تصویر رسید یا فایل PDF رسید را ارسال کنید 📎"
                )

    except Exception as e:

        print("خطا:", e)

        time.sleep(3)
