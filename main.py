import os
import logging
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


BOT_TOKEN = ''

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def download_tiktok_video(url):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return None



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ссылку , сучка 😈")



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "tiktok.com" in text:
        status_msg = await update.message.reply_text("Качау")
        loop = asyncio.get_running_loop()
        video_path = await loop.run_in_executor(None, download_tiktok_video, text)

        if video_path and os.path.exists(video_path):
            try:
                await update.message.reply_video(
                    video=open(video_path, 'rb'),
                    caption="Скачау",
                    write_timeout=60
                )
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit_text(f"Ошибка: {e}")
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
        else:
            await status_msg.edit_text("Не получилось")


if __name__ == '__main__':

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    tiktok_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(start_handler)
    application.add_handler(tiktok_handler)
    print("Бот запущен...")
    application.run_polling()