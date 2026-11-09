import asyncio
import logging
import random
import datetime
import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# --- НАСТРОЙКИ ---
BOT_TOKEN = "9038484067:AAGeh0gSzOC29C6APWoD08j9o8zbpYAtr9I"
GROUP_CHAT_ID = -1003976779667  # ВСТАВЬ СЮДА ID ГРУППЫ
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def generate_detailed_weather():
    """Генерирует подробный почасовой прогноз."""
    
    # 1. Задаем базовые условия дня (погода меняется, но не хаотично)
    # Например: утро прохладное, день теплый, вечер прохладный
    base_temp = random.randint(12, 28)  # Базовая дневная температура
    weather_types = [
        ("ясно", "☀️"), 
        ("переменная облачность", "⛅"), 
        ("облачно", "☁️"), 
        ("небольшой дождь", "🌦️"),
        ("гроза", "⛈️")
    ]
    
    # Определяем "настроение" дня (один тип погоды на весь день, чтобы не было абсурда)
    day_weather, day_emoji = random.choice(weather_types)
    
    # 2. Формируем шапку
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    text = (
        f"<b>🌤️ Подробный прогноз погоды — округа Кордова</b>\n"
        f"<i>{tomorrow.strftime('%d %B %Y')}</i>\n\n"
    )
    
    # 3. Генерируем 24 часа
    for hour in range(24):
        # Красивое форматирование времени (12-часовой формат)
        ampm = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0: display_hour = 12
        
        # Логика температуры: ночью холоднее, днем жарче (синусоида)
        # Пик температуры приходится на 14:00
        temp_offset = -10 if hour < 6 or hour > 22 else (10 if 12 <= hour <= 16 else 0)
        current_temp = base_temp + temp_offset + random.randint(-2, 2)
        
        # Логика погоды для конкретного часа
        if hour < 6 or hour > 20:
            # Ночью без солнца
            condition = "ясно" if day_weather in ["ясно", "переменная облачность"] else day_weather
            emoji = "🌙" if condition == "ясно" else "☁️"
        else:
            condition = day_weather
            emoji = day_emoji

        # Красивое описание
        if condition == "ясно":
            desc = "Ясно" if 6 < hour < 20 else "Звездное небо"
        elif condition == "переменная облачность":
            desc = "Переменная облачность"
        elif condition == "облачно":
            desc = "Пасмурно"
        elif condition == "небольшой дождь":
            desc = "Дождь"
        elif condition == "гроза":
            desc = "Гроза и молнии"

        # Собираем строку
        text += f"• <b>{display_hour:02d}:00 {ampm}</b> — +{current_temp} °C, {desc} {emoji}\n"

    # 4. Итог дня
    text += f"\n<b>Итог:</b> {day_weather.capitalize()}, температура воздуха днем +{base_temp} °C.\n"
    text += f"<a href='https://t.me/your_channel'>Метеоцентр Университета Кордовы</a>"
    
    return text

async def send_daily_weather():
    try:
        weather_text = generate_detailed_weather()
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=weather_text)
        logging.info("Подробный прогноз отправлен!")
    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")

async def main():
    logging.info("Бот запущен и ждет 23:00 по Москве...")
    while True:
        now = datetime.datetime.now(MOSCOW_TZ)
        target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        logging.info(f"Следующая отправка в {target_time.strftime('%Y-%m-%d %H:%M:%S')} (через {wait_seconds:.0f} сек).")
        
        await asyncio.sleep(wait_seconds)
        await send_daily_weather()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())