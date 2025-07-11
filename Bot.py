import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from collections import defaultdict
import emoji

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("🌐 Variable API_TOKEN is not set")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_stats = defaultdict(lambda: {
    'messages': 0,
    'replies': 0,
    'emojis': 0,
    'total_length': 0,
    'replied_by_others': 0
})

def count_emojis(text):
    return sum(1 for char in text if char in emoji.EMOJI_DATA)

@dp.message_handler(content_types=types.ContentType.TEXT)
async def on_text(message: types.Message):
    uid = message.from_user.id
    stats = user_stats[uid]
    text = message.text or ""
    stats['messages'] += 1
    stats['total_length'] += len(text)
    stats['emojis'] += count_emojis(text)
    if message.reply_to_message:
        stats['replies'] += 1
        replied = message.reply_to_message.from_user
        if replied:
            user_stats[replied.id]['replied_by_others'] += 1

@dp.message_handler(commands=['dashboard'])
async def cmd_dashboard(message: types.Message):
    lines = ["📊 *گزارش فعالیت اعضا:*"]
    for uid, s in user_stats.items():
        name = f"[{uid}](tg://user?id={uid})"
        avg_len = s['total_length'] // max(s['messages'], 1)
        lines.append(f"{name} • پیام‌ها: {s['messages']} • ریپلای: {s['replies']} • "
                     f"رسبشن: {s['replied_by_others']} • ایموجی: {s['emojis']} • م‌متن: {avg_len}")
    await message.reply("\n".join(lines), parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
