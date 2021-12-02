from logging import exception
import telebot
from telebot import types
import configure

client = telebot.TeleBot(configure.config['token'])


class Ivent:
    def __init__(self, id, name, description, date, time, place, subject, pay, number_of_seats, who_create) -> None:
        event_id = id
        event_name = name
        event_description = description
        event_date = date
        event_time = time
        event_place = place
        event_subject = subject
        event_pay = pay
        event_number_of_seats = number_of_seats
        user_who_create = who_create


ivent_dict = {}
user_set = dict()


# add_ivent, edit_ivent, view_ivent, search_ivent
@client.message_handler(commands=['start', 'reset'])
def welcome_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id not in user_set.keys():
        # registration
        keyboard.add(*["Регистрация"])
    else:
        keyboard.add(*["Создать мероприятие", "Посмотреть мероприятия"])
        keyboard.add(*["Мои события", "Мои планы"])
        keyboard.add(*["Поиск по событиям", "Мой аккаунт"])
    client.send_message(message.chat.id, 'Что ты хочешь сделать?',
                        reply_markup=keyboard
                        )
    return


# TODO Не обрабатывать если юзер не зареган!
@client.message_handler(content_types=["text"])
def choose_handler(message: types.Message):
    if message.text == "Регистрация":
        registration(message)
    if message.text == "Посмотреть мероприятия":
        client.send_message(message.chat.id, 'Это мероприятия')
    elif message.text == "Создать мероприятие":
        client.send_message(message.chat.id, 'Вы молодец')
    elif message.text == "Мои события":
        client.send_message(message.chat.id, 'Это вы создали')
    elif message.text == "Мои планы":
        client.send_message(message.chat.id, 'Сюда вы пойдете')
    elif message.text == "Поиск по событиям":
        client.send_message(message.chat.id, 'Фильтры')
    elif message.text == "Мой аккаунт":
        client.send_message(message.chat.id, 'Ваше имя: ' + user_set[message.chat.id])


def registration(message: types.Message):
    client.send_message(message.chat.id, 'Введите свое имя: ')
    client.register_next_step_handler(message, registration_step2)


def registration_step2(message: types.Message):
    client.send_message(message.chat.id, 'Ваше имя: ' + message.text)
    client.send_message(message.chat.id, 'Вы успешно зарегестрированы')
    user_set[message.chat.id] = message.text
    welcome_message(message)


client.infinity_polling()
