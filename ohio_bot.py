
import os
import uuid
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

logging.basicConfig(level=logging.INFO)

# 🔷 ВСТАВЬ СВОЙ ТОКЕН ОТ BOTFATHER
API_TOKEN = 'your_api_token_here'

# 🔷 Имя таблицы и папки
GOOGLE_SHEET_NAME = 'Ohio Jobs'
GOOGLE_FOLDER_NAME = 'Ohio moving'

# 🔷 Путь к credentials.json
CREDENTIALS_FILE = 'credentials.json'

# 🔷 Области доступа
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# 🔷 Авторизация Google
creds = Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)

gc = gspread.authorize(creds)
drive_service = build('drive', 'v3', credentials=creds)

# 🔷 Получаем таблицу
spreadsheet = gc.open(GOOGLE_SHEET_NAME)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    report_data = {
        'Job number': '12345',  # замените на парсинг из сообщения
        'report': 'example'
    }
    worksheet = spreadsheet.sheet1
    row = [
        report_data.get('Job number', ''),
        report_data.get('report', '')
    ]
    worksheet.append_row(row)

    if message.photo:
        job_number = report_data.get('Job number', 'report')
        unique_id = uuid.uuid4().hex
        unique_photo_name = f"{job_number}_{unique_id}.jpg"

        photo = message.photo[-1]
        file = await photo.download(destination_file=unique_photo_name)
        local_photo_path = file.name

        file_metadata = {
            'name': unique_photo_name,
            'parents': [GOOGLE_FOLDER_NAME]
        }

        media = MediaFileUpload(local_photo_path, mimetype='image/jpeg')
        drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        os.remove(local_photo_path)

    await message.reply("✅ Отчёт успешно сохранён!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
