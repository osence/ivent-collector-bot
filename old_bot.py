from logging import exception

import telebot
from telebot import types

import configure

client = telebot.TeleBot(configure.config['token'])


class Ivent:
    def __init__(self) -> None:
        name = ''
        date = ''
        cost_check = False
        cost = 0


ivent_dict = {}


# add_ivent, edit_ivent, view_ivent, search_ivent
@client.message_handler(commands=['start', 'reset'])
def welcome_message(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_add_ivent = types.InlineKeyboardButton(text='Добавить событие', callback_data='add_ivent')
    item_edit_ivent = types.InlineKeyboardButton(text='Изменить событие', callback_data='edit_ivent')
    item_view_ivent = types.InlineKeyboardButton(text='Посмотреть событие', callback_data='view_ivent')
    item_search_ivent = types.InlineKeyboardButton(text='Поиск события', callback_data='search_ivent')
    markup_inline.add(item_add_ivent, item_edit_ivent, item_view_ivent, item_search_ivent)
    if message.text == '/start':
        client.send_message(message.chat.id, 'Привет я бот - обработчик событий')
    elif message.text == '/reset':
        client.send_message(message.chat.id, 'Давай попробуем снова')
    client.send_message(message.chat.id, 'Что ты хочешь сделать?',
                        reply_markup=markup_inline
                        )


@client.message_handler(content_types=['add'])
def input_ivent_name(message):
    try:
        ivent_dict[message.chat.id] = Ivent
        mesg = client.send_message(message.chat.id, 'Название события: ')
        client.register_next_step_handler(mesg, input_ivent_date)
    except exception as e:
        client.reply_to(message, 'Что то пошло не так. Попробуй снова')


def input_ivent_date(message):
    try:
        ivent_dict[message.chat.id].name = message.text

        mesg = client.send_message(message.chat.id, 'Дата события (YY.MM.DD.HH.MM.SS): ')
        client.register_next_step_handler(mesg, ivent_cost_question)
    except exception as e:
        client.reply_to(message, 'Что то пошло не так. Попробуй снова')


def ivent_cost_question(message):
    try:
        ivent_dict[message.chat.id].date = message.text
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='ДА', callback_data='cost_check_yes')
        item_no = types.InlineKeyboardButton(text='НЕТ', callback_data='cost_check_no')
        markup_inline.add(item_yes, item_no)
        client.send_message(message.chat.id, 'Событие будет платным?',
                            reply_markup=markup_inline
                            )
    except exception as e:
        client.reply_to(message, 'Что то пошло не так. Попробуй снова')


def ivent_cost_value(message):
    try:
        mesg = client.send_message(message.chat.id, 'Стоимость билета в рублях: ')
        client.register_next_step_handler(mesg, add_ivent_end)
    except exception as e:
        client.reply_to(message, 'Что то пошло не так. Попробуй снова')


def add_ivent_end(message):
    try:
        ivent_dict[message.chat.id].cost = message.text
        client.send_message(message.chat.id, 'Событие сформировано: ')
        if ivent_dict[message.chat.id].cost_check:
            client.send_message(message.chat.id,
                                'Название: ' + ivent_dict[message.chat.id].name + '\nДата: ' + ivent_dict[
                                    message.chat.id].date + '\nСтоимость: ' + ivent_dict[message.chat.id].cost)
        else:
            client.send_message(message.chat.id,
                                'Название: ' + ivent_dict[message.chat.id].name + '\nДата: ' + ivent_dict[
                                    message.chat.id].date + '\nСтоимость: бесплатно')
        client.send_message(message.chat.id, 'Если ты хочешь продолжить /reset')
    except exception as e:
        client.reply_to(message, 'Что то пошло не так. Попробуй снова')

    # Обработка нажатий на кнопки


@client.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'add_ivent':
        input_ivent_name(call.message)
    elif call.data == 'edit_ivent':
        pass
    elif call.data == 'view_ivent':
        pass
    elif call.data == 'search_ivent':
        pass
    elif call.data == 'cost_check_yes':
        ivent_dict[call.message.chat.id].cost_check = True
        ivent_cost_value(call.message)
    elif call.data == 'cost_check_no':
        ivent_dict[call.message.chat.id].cost_check = False
        add_ivent_end(call.message)


@client.message_handler(content_types=["text"])
def send_help(message):
    client.send_message(message.chat.id, 'Попробуйте /reset')


client.polling(none_stop=True, interval=0)