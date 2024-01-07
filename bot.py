import requests
import telebot
from datetime import datetime, timedelta

API_KEY = 'api-key was hidden'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

bot = telebot.TeleBot("bot-key was hidden")

user_preferences = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_preferences[user_id] = {'unit': 'metric'}  # По умолчанию используем метрическую систему

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    item_celsius = telebot.types.KeyboardButton('Цельсий')
    item_fahrenheit = telebot.types.KeyboardButton('Фаренгейт')
    markup.add(item_celsius, item_fahrenheit)

    bot.send_message(message.chat.id, "Привет! Я бот прогноза погоды. Выберите формат температуры:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Цельсий', 'Фаренгейт'])
def set_temperature_unit(message):
    user_id = message.from_user.id
    user_preferences[user_id]['unit'] = 'imperial' if message.text == 'Фаренгейт' else 'metric'

    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Теперь формат температуры установлен в {message.text}.", reply_markup=markup)

@bot.message_handler(commands=['now'])
def now(message):
    if len(message.text.split()) == 1:
        bot.send_message(message.chat.id, "Пожалуйста, укажите город.\n\nПример: /now Москва")
        return

    user_id = message.from_user.id
    unit = user_preferences.get(user_id, {'unit': 'metric'})['unit']

    city = ' '.join(message.text.split()[1:])
    params = {'q': city, 'appid': API_KEY, 'units': unit, 'lang': 'ru'}
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if 'main' not in data:
        bot.send_message(message.chat.id, "Город не найден. Пожалуйста, уточните запрос.")
        return

    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    description = data['weather'][0]['description']
    temperature_unit = '°C' if unit == 'metric' else '°F'
    wind_speed_unit = "м/c" if unit == 'metric' else 'mph'
    message_text = f"Текущая погода в ✨{city}✨: {description}.\n" \
                   f"<b><i>Температура:</i></b> {temperature}{temperature_unit}.\n" \
                   f"<b><i>Влажность:</i></b> {humidity}%.\n" \
                   f"<b><i>Скорость ветра:</i></b> {wind_speed}{wind_speed_unit}.\n"
    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    if len(message.text.split()) == 1:
        bot.send_message(message.chat.id, "Пожалуйста, укажите город.\n\nПример: /tomorrow Москва")
        return

    user_id = message.from_user.id
    unit = user_preferences.get(user_id, {'unit': 'metric'})['unit']

    city = ' '.join(message.text.split()[1:])
    params = {'q': city, 'appid': API_KEY, 'units': unit, 'lang': 'ru'}
    response = requests.get(FORECAST_URL, params=params)
    data = response.json()

    if 'list' not in data:
        bot.send_message(message.chat.id, "Город не найден. Пожалуйста, уточните запрос.")
        return

    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    forecast_list = data['list']
    forecast_text = f"Прогноз погоды в ✨{city}✨ на завтра:\n"

    for forecast in forecast_list:
        date = forecast['dt_txt']
        if date.startswith(tomorrow_date):
            temperature = forecast['main']['temp']
            humidity = forecast['main']['humidity']
            wind_speed = forecast['wind']['speed']
            description = forecast['weather'][0]['description']
            temperature_unit = '°C' if unit == 'metric' else '°F'
            wind_speed_unit = "м/c" if unit == 'metric' else 'mph'
            forecast_text += f"\n{date}: {description}.\n" \
                             f"<b><i>Температура:</i></b> {temperature}{temperature_unit}.\n" \
                             f"<b><i>Влажность:</i></b> {humidity}%.\n" \
                             f"<b><i>Скорость ветра:</i></b> {wind_speed}{wind_speed_unit}.\n"

    bot.send_message(message.chat.id, forecast_text, parse_mode='HTML')

@bot.message_handler(commands=['week'])
def week(message):
    if len(message.text.split()) == 1:
        bot.send_message(message.chat.id, "Пожалуйста, укажите город.\n\nПример: /week Москва")
        return

    user_id = message.from_user.id
    unit = user_preferences.get(user_id, {'unit': 'metric'})['unit']

    city = ' '.join(message.text.split()[1:])
    params = {'q': city, 'appid': API_KEY, 'units': unit, 'lang': 'ru'}
    response = requests.get(FORECAST_URL, params=params)
    data = response.json()

    if 'list' not in data:
        bot.send_message(message.chat.id, "Город не найден. Пожалуйста, уточните запрос.")
        return

    forecast_list = data['list']
    forecast_text = f"Прогноз погоды в ✨{city}✨ на неделю:\n"

    for forecast in forecast_list:
        date = forecast['dt_txt']
        temperature = forecast['main']['temp']
        humidity = forecast['main']['humidity']
        wind_speed = forecast['wind']['speed']
        description = forecast['weather'][0]['description']
        temperature_unit = '°C' if unit == 'metric' else '°F'
        wind_speed_unit = "м/c" if unit == 'metric' else 'mph'
        forecast_text += f"\n{date}: {description}.\n" \
                         f"<b><i>Температура:</i></b> {temperature}{temperature_unit}.\n" \
                         f"<b><i>Влажность:</i></b> {humidity}%.\n" \
                         f"<b><i>Скорость ветра:</i></b> {wind_speed}{wind_speed_unit}.\n"

    bot.send_message(message.chat.id, forecast_text, parse_mode='HTML')

@bot.message_handler(commands=['clear'])
def clear(message):
    user_id = message.from_user.id
    if user_id in user_preferences:
        del user_preferences[user_id]
        bot.send_message(message.chat.id, "Данные пользователя удалены.")
    else:
        bot.send_message(message.chat.id, "Данные пользователя не найдены.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
