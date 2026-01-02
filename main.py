import os
import logging
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден в .env файле!")
    print("Создайте файл .env и добавьте строку: BOT_TOKEN=ваш_токен")
    input("Нажмите Enter для выхода...")
    exit(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def download_tiktok_video(url):
    """Скачивает видео с TikTok"""
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'downloads/%(id)s_video.%(ext)s',
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
        print(f"Ошибка скачивания видео: {e}")
        return None


def download_tiktok_audio(url):
    """Скачивает только аудио с TikTok"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s_audio.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Получаем путь к аудио файлу (с расширением .mp3)
            base_path = ydl.prepare_filename(info)
            audio_path = os.path.splitext(base_path)[0] + '.mp3'
            return audio_path
    except Exception as e:
        print(f"Ошибка скачивания аудио: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ссылку , сучка 😈")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "tiktok.com" in text:
        status_msg = await update.message.reply_text("Качаю...")
        loop = asyncio.get_running_loop()

        # Скачиваем видео и аудио параллельно
        video_task = loop.run_in_executor(None, download_tiktok_video, text)
        audio_task = loop.run_in_executor(None, download_tiktok_audio, text)

        video_path, audio_path = await asyncio.gather(video_task, audio_task)


        if video_path and os.path.exists(video_path):
            try:
                await status_msg.edit_text("Отправляю видео...")
                await update.message.reply_video(
                    video=open(video_path, 'rb'),
                    caption="🎥 Видео",
                    write_timeout=60
                )
            except Exception as e:
                await update.message.reply_text(f"Ошибка отправки видео: {e}")
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
        else:
            await update.message.reply_text("Не получилось скачать видео")

        # Отправляем аудио
        if audio_path and os.path.exists(audio_path):
            try:
                await status_msg.edit_text("Отправляю аудио...")
                await update.message.reply_audio(
                    audio=open(audio_path, 'rb'),
                    caption="🎵 Аудио",
                    write_timeout=60
                )
            except Exception as e:
                await update.message.reply_text(f"Ошибка отправки аудио: {e}")
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
        else:
            await update.message.reply_text("Не получилось скачать аудио")


        try:
            await status_msg.delete()
        except:
            pass


if __name__ == '__main__':
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        start_handler = CommandHandler('start', start)
        tiktok_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
        application.add_handler(start_handler)
        application.add_handler(tiktok_handler)
        print("Бот запущен...")
        application.run_polling()
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        input("Нажмите Enter для выхода...")