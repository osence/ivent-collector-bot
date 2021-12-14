import datetime
import re
import telebot
from telebot import types
import configure
from geopandas.tools import geocode

client = telebot.TeleBot(configure.config['token'])


class Event:
    def __init__(self, id, name, description, date, time, place, subject, pay, number_of_seats, who_create):
        self.event_id = id
        self.event_name = name
        self.event_description = description
        self.event_date = date
        self.event_time = time
        self.event_place = place
        self.event_subject = subject
        self.event_pay = pay
        self.event_number_of_seats = number_of_seats
        self.user_who_create = who_create


event_dict = {}
event_list = []
i = 0
user_set = dict()


def add_event_in_database(i, name, description, date, time, place, theme, pay, msg, userId):
    # TODO Запрос на добавление события
    event_list.append(Event(i, name, description, date, time, place, theme, pay, msg, userId))


def id_in_database(userId):
    if userId in user_set.keys():
        # TODO Запрос на проверку регистрации
        return False
    return True

def add_user_in_database(name, birthday, userId):
    # TODO Запрос на регистрацию пользователя
    user_set[userId] = [name, birthday]


def get_events_from_database():
    # TODO Запрос на получение всех мероприятий
    return []


# TODO сделать везде проверку на длину строк (слишком большие)
@client.message_handler(commands=['start', 'reset'])
def welcome_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if id_in_database(message.chat.id):
        # registration
        keyboard.add(*["Регистрация"])
        client.send_message(message.chat.id, 'Чтобы начать работать с ботом, вам необходимо зарегистрироваться.',
                            reply_markup=keyboard)
    else:
        keyboard.add(*["Создать мероприятие", "Посмотреть мероприятия"])
        keyboard.add(*["Мои события", "Мои планы"])
        keyboard.add(*["Поиск по событиям", "Мой аккаунт"])
        client.send_message(message.chat.id, 'Выберите действие',
                            reply_markup=keyboard)
    return


@client.message_handler(content_types=["text"])
def choose_handler(message: types.Message):
    if message.text == "Регистрация":
        registration(message)
    elif id_in_database(message.chat.id):
        welcome_message(message)
    elif message.text == "Посмотреть мероприятия":
        show_events(message, 0)
    elif message.text == "Создать мероприятие":
        create_event(message)
    elif message.text == "Мои события":
        client.send_message(message.chat.id, 'Это вы создали')
    elif message.text == "Мои планы":
        client.send_message(message.chat.id, 'Сюда вы пойдете')
    elif message.text == "Поиск по событиям":
        client.send_message(message.chat.id, 'Фильтры')
    elif message.text == "Мой аккаунт":
        info_account(message)


def registration(message: types.Message):
    client.send_message(message.chat.id, 'Введите ваше ФИО: ')
    client.register_next_step_handler(message, registration_step2)


def isCorrectName(text):
    if re.match(r'^[А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*( [А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*)+$', text) is not None:
        return True
    else:
        return False


def registration_step2(message: types.Message):
    if message.location != None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        client.send_location(message.chat.id, latitude, longitude)
    else:
        loc = message.text
        # finding the location
        location = geocode(loc, provider="nominatim" , user_agent = 'my_request')
        point = location.geometry.iloc[0]
        client.send_location(message.chat.id, point.y, point.x)

    if isCorrectName(message.text) and len(message.text) < 255:
        client.send_message(message.chat.id, 'Введите вашу дату рождения в формате дд.мм.гггг:')
        client.register_next_step_handler(message, registration_step3, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step2)


def registration_step3(message: types.Message, name):
    try:
        datetime.datetime.strptime(message.text, "%d.%m.%Y")
        client.send_message(message.chat.id, 'Вы успешно зарегистрированы')
        add_user_in_database(name, message.text, message.chat.id)
        welcome_message(message)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step3, name)


def info_account(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_edit_info = types.InlineKeyboardButton(text='Редактировать информацию', callback_data='edit_info|')
    markup_inline.add(button_edit_info)
    client.send_message(message.chat.id,
                        'Имя: ' + user_set[message.chat.id][0] + '\nДата рождения: ' + user_set[message.chat.id][1],
                        reply_markup=markup_inline)


def edit_info(message: types.Message):
    client.send_message(message.chat.id, 'Введите ваше ФИО:')
    client.register_next_step_handler(message, edit_info_step2)


def edit_info_step2(message: types.Message):
    if isCorrectName(message.text) and len(message.text) < 255:
        client.send_message(message.chat.id, 'Введите вашу дату рождения в формате дд.мм.гггг:')
        client.register_next_step_handler(message, edit_info_step3, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step2)


def edit_info_step3(message: types.Message, name):
    try:
        datetime.datetime.strptime(message.text, "%d.%m.%Y")
        client.send_message(message.chat.id, 'Данные успешно изменены')
        user_set[message.chat.id] = [name, message.text, message.chat.id]
        welcome_message(message)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step3, name)


# TODO сделать ожидание, как везде, но учитывая callback
def create_event(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='Выставка', callback_data='create_event_step2|Выставка')
    button_2 = types.InlineKeyboardButton(text='Концерт', callback_data='create_event_step2|Концерт')
    button_3 = types.InlineKeyboardButton(text='Спектакль', callback_data='create_event_step2|Спектакль')
    button_4 = types.InlineKeyboardButton(text='Обучение', callback_data='create_event_step2|Обучение')
    button_5 = types.InlineKeyboardButton(text='Встреча', callback_data='create_event_step2|Встреча')
    button_6 = types.InlineKeyboardButton(text='Экскурсия', callback_data='create_event_step2|Экскурсия')
    button_7 = types.InlineKeyboardButton(text='Праздник', callback_data='create_event_step2|Праздник')
    button_8 = types.InlineKeyboardButton(text='Другое', callback_data='create_event_step2|Другое')
    button_9 = types.InlineKeyboardButton(text='Без категории', callback_data='create_event_step2|Без категории')
    markup_inline.add(button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8, button_9,
                      row_width=2)
    client.send_message(message.chat.id, 'Выберите тематику вашего мероприятия:', reply_markup=markup_inline)


def create_event_step2(message: types.Message, theme):
    client.send_message(message.chat.id, 'Введите название вашего мероприятия:')
    client.register_next_step_handler(message, create_event_step3, theme)


def isCorrectText(text):
    if re.search(r'[А-ЯЁа-яёa-zA-Z]{3,}', text) is not None:
        return True
    else:
        return False


def create_event_step3(message: types.Message, theme):
    if isCorrectText(message.text) and len(message.text) < 255:
        client.send_message(message.chat.id, 'Введите описание вашего мероприятия:')
        client.register_next_step_handler(message, create_event_step4, theme, message.text)
    else:
        client.send_message(message.chat.id,
                            'В названии мероприятия должно быть хотя бы одно слово. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step3, theme)


def create_event_step4(message: types.Message, theme, name):
    if isCorrectText(message.text) and len(message.text) < 255:
        client.send_message(message.chat.id, 'Введите дату вашего мероприятия в формате дд.мм.гггг:')
        client.register_next_step_handler(message, create_event_step5, theme, name, message.text)
    else:
        client.send_message(message.chat.id,
                            'В описании мероприятия должно быть хотя бы одно слово. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step4, theme, name)


def create_event_step5(message: types.Message, theme, name, description):
    try:
        user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
        user_date = datetime.date(user_datetime.year, user_datetime.month, user_datetime.day)
        now_date = datetime.date.today()
        if user_date < now_date:
            client.send_message(message.chat.id, 'Невозможная дата. Попробуйте еще раз.')
            client.register_next_step_handler(message, create_event_step5, theme, name, description)
        else:
            client.send_message(message.chat.id, 'Введите время вашего мероприятия (в формате чч:мм):')
            client.register_next_step_handler(message, create_event_step6, theme, name, description, message.text)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step5, theme, name, description)


def isCorrectTime(text):
    if re.match(r'([0-1][0-9]|2[0-3]):([0-5][0-9])$', text) is not None:
        return True
    else:
        return False


def create_event_step6(message: types.Message, theme, name, description, date):
    if isCorrectTime(message.text):
        now_date = datetime.datetime.now()
        now_date_str = now_date.strftime("%d.%m.%Y")
        if now_date_str == date and int(message.text.split(':')[0]) * 100 + int(
                message.text.split(':')[1]) <= now_date.hour * 100 + now_date.minute:
            client.send_message(message.chat.id, 'Невозможное время. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step6, theme, name, description, date)
        else:
            client.send_message(message.chat.id, 'Введите место проведения:')
            client.register_next_step_handler(message, create_event_step7, theme, name, description, date, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step6, theme, name, description, date)


# TODO Координаты!?
def create_event_step7(message: types.Message, theme, name, description, date, time):
    latitude = message.location.latitude
    longitude = message.location.longitude

    client.send_message(message.chat.id, 'Введите стоимость посещения (целое число):')
    client.register_next_step_handler(message, create_event_step8, theme, name, description, date, time, message.text)


def isCorrectDigit(text):
    if re.match(r'([1-9][0-9]+)|[0-9]$', text) is not None:
        return True
    else:
        return False


def create_event_step8(message: types.Message, theme, name, description, date, time, place):
    if isCorrectDigit(message.text):
        client.send_message(message.chat.id, 'Введите количество мест (0 - не ограничено):')
        client.register_next_step_handler(message, create_event_step9, theme, name, description, date, time, place,
                                          message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step8, theme, name, description, date, time, place)


def create_event_step9(message: types.Message, theme, name, description, date, time, place, pay):
    if isCorrectDigit(message.text):
        client.send_message(message.chat.id, 'Ваше мероприятие успешно добавлено.')
        global i  # pylint: disable=global-statement
        add_event_in_database(i, name, description, date, time, place, theme, pay, message.text, message.chat.id)
        i += 1
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step9, theme, name, description, date, time, place, pay)


def show_events(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    # TODO тут должно быть получение списка из бд
    get_events_from_database()
    number = 0
    for event in event_list:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page != 0 and page != (len(event_list) - 1) // 5:
        button1 = types.InlineKeyboardButton(text='<', callback_data='prev_page|' + str(page))
        button2 = types.InlineKeyboardButton(text='>', callback_data='next_page|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<', callback_data='prev_page|' + str(page))
        markup_inline.add(button)
    elif page != (len(event_list) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>', callback_data='next_page|' + str(page))
        markup_inline.add(button)
    else:
        client.send_message(message.chat.id, 'Мероприятий нет')
        return
    client.send_message(message.chat.id, 'Предстоящие мероприятия:', reply_markup=markup_inline)


def show_events_next(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    # TODO тут должно быть получение списка из бд
    get_events_from_database()
    number = 0
    for event in event_list:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page != 0 and page != (len(event_list) - 1) // 5:
        button1 = types.InlineKeyboardButton(text='<', callback_data='prev_page|' + str(page))
        button2 = types.InlineKeyboardButton(text='>', callback_data='next_page|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<', callback_data='prev_page|' + str(page))
        markup_inline.add(button)
    elif page != (len(event_list) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>', callback_data='next_page|' + str(page))
        markup_inline.add(button)
    else:
        client.send_message(message.chat.id, 'Мероприятий нет')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.id, reply_markup=markup_inline)


def show_event(message: types.Message, id):
    # TODO Здесь запрос к БД по id вместо того, что ниже
    cur_event = None
    for event in event_list:
        if event.event_id == id:
            cur_event = event
            break
    seats = ''
    if cur_event.event_number_of_seats == 0:
        seats = 'Не ограничено'
    else:
        seats = cur_event.event_number_of_seats
    text = ('Название: ' + cur_event.event_name +
            '\nДата: ' + cur_event.event_date +
            '\nВремя: ' + cur_event.event_time +
            '\nОписание: ' + cur_event.event_description +
            '\nМесто: ' + cur_event.event_place +
            '\nКатегория: ' + cur_event.event_subject +
            '\nСтоимость: ' + cur_event.event_pay +
            '\nКоличество мест: ' + seats
            )
    if cur_event.user_who_create == message.chat.id:
        markup_inline = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Редактировать', callback_data='edit_event|' + str(id))
        button2 = types.InlineKeyboardButton(text='Удалить', callback_data='delete_event|' + str(id))
        markup_inline.add(button1, button2)
        client.send_message(message.chat.id, text, reply_markup=markup_inline)
    else:
        # TODO Регистрация
        client.send_message(message.chat.id, text)


# TODO Редактирование мероприятия
def edit_event(message: types.Message, id):
    client.send_message(message.chat.id, 'Тут можно будет редактировать')


# TODO Удаление мероприятия
def delete_event(message: types.Message, id):
    client.send_message(message.chat.id, 'Тут можно будет удалять')


# Обработка нажатий на кнопки
@client.callback_query_handler(func=lambda call: True)
def answer(call):
    func = call.data.split('|')[0]
    if func == 'edit_info':
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                         inline_message_id=None)
        edit_info(call.message)
    elif func == 'create_event_step2':
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                         inline_message_id=None)
        theme = call.data.split('|')[1]
        create_event_step2(call.message, theme)
    # TODO изменить, чтоб сообщение заново не отправлялось
    elif func == 'next_page':
        page = int(call.data.split('|')[1])
        show_events_next(call.message, page + 1)
    elif func == 'prev_page':
        page = int(call.data.split('|')[1])
        show_events_next(call.message, page - 1)
    elif func == 'show_event':
        event_id = int(call.data.split('|')[1])
        show_event(call.message, event_id)
    elif func == 'edit_event':
        event_id = int(call.data.split('|')[1])
        edit_event(call.message, event_id)
    elif func == 'delete_event':
        event_id = int(call.data.split('|')[1])
        delete_event(call.message, event_id)


client.infinity_polling()
