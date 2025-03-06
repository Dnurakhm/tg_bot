import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Токен бота
TELEGRAM_BOT_TOKEN = "7532015526:AAH6onVHZ7cBL6r13cyA95W0hgY1R4oECrI"
API_TOKEN = "4aba690793e7bfe87064b5f0474b9943ab429d77"

# Настроим логирование
logging.basicConfig(level=logging.INFO)


# Функция для получения данных о качестве воздуха по гео-координатам
def get_raw_air_quality_data_by_geo(latitude, longitude):
    url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Вернет JSON с информацией о качестве воздуха
    else:
        return {"error": "Не удалось получить данные"}


# Форматирование данных о качестве воздуха
def format_air_quality_data(air_quality_data, city_name):
    if "error" in air_quality_data:
        return air_quality_data["error"]

    air_quality = air_quality_data["data"]

    # Извлекаем данные
    aqi = air_quality["aqi"]
    temperature = air_quality["iaqi"].get("t", {}).get("v", "неизвестно")  # Температура
    humidity = air_quality["iaqi"].get("h", {}).get("v", "неизвестно")  # Влажность
    wind_speed = air_quality["iaqi"].get("w", {}).get("v", "неизвестно")  # Скорость ветра
    wind_gust = air_quality["iaqi"].get("wg", {}).get("v", "неизвестно")  # Порывы ветра
    pressure = air_quality["iaqi"].get("p", {}).get("v", "неизвестно")  # Давление

    # Загрязняющие вещества
    pm25 = air_quality["iaqi"].get("pm25", {}).get("v", "неизвестно")  # PM2.5
    co = air_quality["iaqi"].get("co", {}).get("v", "неизвестно")  # CO
    no2 = air_quality["iaqi"].get("no2", {}).get("v", "неизвестно")  # NO2
    so2 = air_quality["iaqi"].get("so2", {}).get("v", "неизвестно")  # SO2

    # Формируем строку отчета
    return f"🌍 Качество воздуха в {city_name}\n" \
           f"📆 Последнее обновление: {air_quality.get('time', {}).get('s', 'неизвестно')}\n\n" \
           f"💨 Общий индекс загрязнения (AQI): {aqi}\n" \
           f"🌡 Температура: {temperature}°C\n" \
           f"💧 Влажность: {humidity}%\n" \
           f"🌬 Скорость ветра: {wind_speed} м/с (порывы до {wind_gust} м/с)\n" \
           f"🛑 Давление: {pressure} hPa\n\n" \
           f"🦠 Основные загрязняющие вещества:\n" \
           f"- PM2.5 (опасная пыль): {pm25}\n" \
           f"- CO (угарный газ): {co}\n" \
           f"- NO₂ (диоксид азота): {no2}\n" \
           f"- SO₂ (диоксид серы): {so2}"


# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    print("Команда /start получена.")
    keyboard = [[KeyboardButton("Отправить местоположение", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Отправь свое местоположение, чтобы узнать качество воздуха.",
        reply_markup=reply_markup
    )


# Обработчик получения геолокации
async def location_handler(update: Update, context: CallbackContext):
    location = update.message.location
    if location:
        latitude = location.latitude
        longitude = location.longitude

        print(f"Получены координаты: Широта: {latitude}, Долгота: {longitude}")

        # Получаем данные о качестве воздуха
        raw_data = get_raw_air_quality_data_by_geo(latitude, longitude)
        air_quality_report = format_air_quality_data(raw_data, city_name="Almaty")  # Замените на имя города, если нужно

        # Отправка отчета о качестве воздуха
        await update.message.reply_text(air_quality_report)
    else:
        await update.message.reply_text("Не удалось получить местоположение.")


# Запуск бота
def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Логируем, когда бот запущен
    print("Бот запущен, ожидаю сообщений...")

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, location_handler))

# Запуск бота в режиме polling
    application.run_polling()

# Запуск основной функции
if __name__ == "__main__":
    main()  # Запуск бота без использования asyncio