import datetime
import re
import telebot
from telebot import types
from geopandas.tools import geocode
import configure
import bd

client = telebot.TeleBot(configure.config['token'])


def is_correct_name(text):
    return re.match(r'^[А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*( [А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*)+$',
                text) is not None


def is_correct_text(text):
    return re.search(r'[А-ЯЁа-яёa-zA-Z]{3,}', text) is not None


def is_correct_time(text):
    return re.match(r'([0-1][0-9]|2[0-3]):([0-5][0-9])$', text) is not None


def is_correct_digit(text):
    return re.match(r'([1-9][0-9]+)|[0-9]$', text) is not None


@client.message_handler(commands=['start', 'reset'])
def welcome_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    flag_is_registered = bd.id_in_database(message.chat.id)
    if flag_is_registered is False:
        keyboard.add(*["Регистрация"])
        client.send_message(message.chat.id,
                            'Чтобы начать работать с ботом, вам необходимо зарегистрироваться.',
                            reply_markup=keyboard)
    elif flag_is_registered is True:
        keyboard.add(*["Создать мероприятие", "Посмотреть мероприятия"])
        keyboard.add(*["Мои события", "Мои планы"])
        keyboard.add(*["Поиск по событиям", "Мой аккаунт"])
        client.send_message(message.chat.id, 'Выберите действие',
                            reply_markup=keyboard)
    else:
        client.send_message(message.chat.id, flag_is_registered)

@client.message_handler(content_types=["text"])
def choose_handler(message: types.Message):
    flag_is_registered = bd.id_in_database(message.chat.id)
    if flag_is_registered not in [True, False]:
        client.send_message(message.chat.id, flag_is_registered)

    if message.text == "Регистрация" and flag_is_registered is False:
        registration(message)
    elif flag_is_registered is False:
        welcome_message(message)
    elif message.text == "Посмотреть мероприятия":
        show_events(message)
    elif message.text == "Создать мероприятие":
        create_event(message)
    elif message.text == "Мои события":
        events_of_user(message)
    elif message.text == "Мои планы":
        events_in_user_plans(message)
    elif message.text == "Поиск по событиям":
        search(message)
    elif message.text == "Мой аккаунт":
        info_account(message)
    else:
        unknown(message)


def registration(message: types.Message):
    client.send_message(message.chat.id, 'Введите ваше ФИО: ')
    client.register_next_step_handler(message, registration_step2)


def registration_step2(message: types.Message):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_name(message.text):
                client.send_message(message.chat.id,
                                    'Введите вашу дату рождения в формате дд.мм.гггг:')
                client.register_next_step_handler(message, registration_step3, message.text)
            else:
                client.send_message(message.chat.id,
                                    'Некорректный ввод. Попробуйте ещё раз.')
                client.register_next_step_handler(message, registration_step2)
        else:
            client.send_message(message.chat.id,
                                'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, registration_step2)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step2)


def registration_step3(message: types.Message, name):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            user_date = datetime.date(user_datetime.year,
                                      user_datetime.month,
                                      user_datetime.day)
            now_date = datetime.date.today()
            if user_date > now_date:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, registration_step3, name)
            else:
                if bd.add_user_in_database(name, message.text, message.chat.id):
                    client.send_message(message.chat.id,
                                    'Вы успешно зарегистрированы.')
                else:
                    client.send_message(message.chat.id,
                                    'Не удалось выполнить запрос.')
                welcome_message(message)
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, registration_step3, name)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step3, name)


def info_account(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_edit_info = types.InlineKeyboardButton(text='Редактировать информацию',
                                                  callback_data='edit_info|')
    markup_inline.add(button_edit_info)
    user_info = bd.get_user_info_from_database(message.chat.id)
    if user_info not in (False, None):
        client.send_message(message.chat.id,
                            'Имя: ' + user_info[0] + '\nДата рождения: ' + user_info[1],
                            reply_markup=markup_inline)
    elif user_info is None:
        client.send_message(message.chat.id,
                            'Пользователя не существует.')
    else:
        client.send_message(message.chat.id,
                            'Не удалось выполнить запрос.')


def edit_info(message: types.Message):
    client.send_message(message.chat.id, 'Введите ваше ФИО:')
    client.register_next_step_handler(message, edit_info_step2)


def edit_info_step2(message: types.Message):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_name(message.text):
                client.send_message(message.chat.id,
                                    'Введите вашу дату рождения в формате дд.мм.гггг:')
                client.register_next_step_handler(message, edit_info_step3, message.text)
            else:
                client.send_message(message.chat.id,
                                    'Некорректный ввод. Попробуйте ещё раз.')
                client.register_next_step_handler(message, edit_info_step2)
        else:
            client.send_message(message.chat.id,
                                'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_info_step2)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step2)


def edit_info_step3(message: types.Message, name):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            user_date = datetime.date(user_datetime.year,
                                      user_datetime.month,
                                      user_datetime.day)
            now_date = datetime.date.today()
            if user_date > now_date:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, edit_info_step3, name)
            else:
                if bd.edit_user_in_database(name, message.text, message.chat.id):
                    client.send_message(message.chat.id,
                                    'Данные успешно изменены')
                else:
                    client.send_message(message.chat.id,
                                    'Не удалось выполнить запрос.')
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_info_step3, name)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step3, name)


def create_event(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='Выставка',
                                          callback_data='create_event_step2|Выставка')
    button_2 = types.InlineKeyboardButton(text='Концерт',
                                          callback_data='create_event_step2|Концерт')
    button_3 = types.InlineKeyboardButton(text='Спектакль',
                                          callback_data='create_event_step2|Спектакль')
    button_4 = types.InlineKeyboardButton(text='Обучение',
                                          callback_data='create_event_step2|Обучение')
    button_5 = types.InlineKeyboardButton(text='Встреча',
                                          callback_data='create_event_step2|Встреча')
    button_6 = types.InlineKeyboardButton(text='Экскурсия',
                                          callback_data='create_event_step2|Экскурсия')
    button_7 = types.InlineKeyboardButton(text='Праздник',
                                          callback_data='create_event_step2|Праздник')
    button_8 = types.InlineKeyboardButton(text='Другое',
                                          callback_data='create_event_step2|Другое')
    button_9 = types.InlineKeyboardButton(text='Без категории',
                                          callback_data='create_event_step2|Без категории')
    markup_inline.add(button_1, button_2, button_3, button_4, button_5, button_6,
                      button_7, button_8, button_9, row_width=2)
    client.send_message(message.chat.id, 'Выберите тематику вашего мероприятия:',
                        reply_markup=markup_inline)


def create_event_step2(message: types.Message, theme):
    client.send_message(message.chat.id, 'Введите название вашего мероприятия:')
    client.register_next_step_handler(message, create_event_step3, theme)


def create_event_step3(message: types.Message, theme):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_text(message.text):
                client.send_message(message.chat.id, 'Введите описание вашего мероприятия:')
                client.register_next_step_handler(message, create_event_step4,
                                                  theme, message.text)
            else:
                client.send_message(message.chat.id,
                                    'В названии мероприятия должно быть хотя бы одно слово. \
                                    Попробуйте ещё раз.')
                client.register_next_step_handler(message, create_event_step3, theme)
        else:
            client.send_message(message.chat.id, 'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step3, theme)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step3, theme)


def create_event_step4(message: types.Message, theme, name):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_text(message.text):
                client.send_message(message.chat.id,
                                    'Введите дату вашего мероприятия в формате дд.мм.гггг:')
                client.register_next_step_handler(message, create_event_step5,
                                                  theme, name, message.text)
            else:
                client.send_message(message.chat.id,
                                    'В описании мероприятия должно быть хотя бы одно слово. \
                                    Попробуйте ещё раз.')
                client.register_next_step_handler(message, create_event_step4, theme, name)
        else:
            client.send_message(message.chat.id, 'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step4, theme, name)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step4, theme, name)


def create_event_step5(message: types.Message, theme, name, description):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            user_date = datetime.date(user_datetime.year,
                                      user_datetime.month,
                                      user_datetime.day)
            now_date = datetime.date.today()
            if user_date < now_date:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, create_event_step5,
                                                  theme, name, description)
            else:
                client.send_message(message.chat.id,
                                    'Введите время вашего мероприятия (в формате чч:мм):')
                client.register_next_step_handler(message, create_event_step6,
                                                  theme, name, description, message.text)
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step5,
                                              theme, name, description)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step5,
                                          theme, name, description)


def create_event_step6(message: types.Message, theme, name, description, date):
    if message.text is not None and is_correct_time(message.text):
        now_date = datetime.datetime.now()
        now_date_str = now_date.strftime("%d.%m.%Y")
        if now_date_str == date and int(message.text.split(':')[0]) * 100 + int(
                message.text.split(':')[1]) <= now_date.hour * 100 + now_date.minute:
            client.send_message(message.chat.id,
                                'Невозможное время. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step6,
                                              theme, name, description, date)
        else:
            client.send_message(message.chat.id,
                                'Введите место проведения или прикрепите геолокацию:')
            client.register_next_step_handler(message, create_event_step7,
                                              theme, name, description, date, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step6,
                                          theme, name, description, date)


def create_event_step7(message: types.Message, theme, name, description, date, time):
    latitude = None
    longitude = None

    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.text is not None:
        loc = message.text
        try:
            location = geocode(loc, provider="nominatim", user_agent='my_request')
            point = location.geometry.iloc[0]
            latitude = point.y
            longitude = point.x
        except Exception:
            client.send_message(message.chat.id,
                                'Некорректный адрес. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_event_step7,
                                              theme, name, description, date, time)
            return

    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step7,
                                          theme, name, description, date, time)
        return

    place = str(latitude) + '|' + str(longitude)
    print(place)
    client.send_message(message.chat.id,
                        'Введите стоимость посещения (целое число):')
    client.register_next_step_handler(message, create_event_step8,
                                      theme, name, description, date, time, place)


def create_event_step8(message: types.Message, theme, name, description, date, time, place):
    if message.text is not None and is_correct_digit(message.text):
        client.send_message(message.chat.id,
                            'Введите количество мест (0 - не ограничено):')
        client.register_next_step_handler(message, create_event_step9,
                                          theme, name, description, date, time, place, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step8,
                                          theme, name, description, date, time, place)


def create_event_step9(message: types.Message, theme, name, description, date, time, place, pay):
    if message.text is not None and is_correct_digit(message.text):
        if bd.add_event_in_database(name, description, date, time,
                                 place, theme, pay, message.text, message.chat.id):
            client.send_message(message.chat.id,
                                'Ваше мероприятие успешно добавлено.')
        else:
            client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_event_step9,
                                          theme, name, description, date, time, place, pay)


def show_events(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_from_database()
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id, 'Мероприятий нет')
        return
    client.send_message(message.chat.id,
                        'Предстоящие мероприятия:',
                        reply_markup=markup_inline)


def show_events_next(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_from_database()
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id, 'Мероприятий нет')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def show_event(message: types.Message, event_id):
    event_info = bd.get_event_info_from_database(event_id)
    if event_info is False:
        client.send_message(message.chat.id,
                            "Не удалось выполнить запрос.")
        return
    if event_info is not None:
        seats = ''
        if event_info.event_number_of_seats == str(0):
            seats = 'не ограничено'
        else:
            seats = event_info.event_number_of_seats
        text = ('Название: ' + event_info.event_name +
                '\nДата: ' + event_info.event_date +
                '\nВремя: ' + event_info.event_time +
                '\nОписание: ' + event_info.event_description +
                '\nКатегория: ' + event_info.event_subject.lower() +
                '\nСтоимость: ' + str(event_info.event_pay) +
                '\nКоличество мест: ' + str(seats)
                )
        markup_inline = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Посмотреть местоположение',
                                             callback_data='show_coord|' + event_info.event_place)
        markup_inline.add(button1)
        if event_info.user_who_create == message.chat.id:
            button2 = types.InlineKeyboardButton(text='Редактировать',
                                                 callback_data='edit_event|' + str(event_id))
            button3 = types.InlineKeyboardButton(text='Удалить',
                                                 callback_data='delete_event|' + str(event_id))
            markup_inline.add(button2, button3)
        else:
            flag_is_registered = bd.user_is_registered(message.chat.id, event_id)
            if flag_is_registered is True:
                button2 = types.InlineKeyboardButton(text='Отменить регистрацию',
                                                     callback_data='cansel_reg|' + str(event_id))
                markup_inline.add(button2)
            elif flag_is_registered is False:
                button2 = types.InlineKeyboardButton(text='Зарегистрироваться',
                                                     callback_data='register|' + str(event_id))
                markup_inline.add(button2)
            else:
                client.send_message(message.chat.id, flag_is_registered)
        client.send_message(message.chat.id, text, reply_markup=markup_inline)
    else:
        client.send_message(message.chat.id,
                            "Мероприятия не существует")


def edit_event(message: types.Message, event_id):
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='Выставка',
                                          callback_data='edit_event_st2|Выставка|' + str(event_id))
    button_2 = types.InlineKeyboardButton(text='Концерт',
                                          callback_data='edit_event_st2|Концерт|' + str(event_id))
    button_3 = types.InlineKeyboardButton(text='Спектакль',
                                          callback_data='edit_event_st2|Спектакль|' + str(event_id))
    button_4 = types.InlineKeyboardButton(text='Обучение',
                                          callback_data='edit_event_st2|Обучение|' + str(event_id))
    button_5 = types.InlineKeyboardButton(text='Встреча',
                                          callback_data='edit_event_st2|Встреча|' + str(event_id))
    button_6 = types.InlineKeyboardButton(text='Экскурсия',
                                          callback_data='edit_event_st2|Экскурсия|' + str(event_id))
    button_7 = types.InlineKeyboardButton(text='Праздник',
                                          callback_data='edit_event_st2|Праздник|' + str(event_id))
    button_8 = types.InlineKeyboardButton(text='Другое',
                                          callback_data='edit_event_st2|Другое|' + str(event_id))
    button_9 = types.InlineKeyboardButton(text='Без категории',
                                          callback_data='edit_event_st2|Без категории|' + str(event_id))
    markup_inline.add(button_1, button_2, button_3, button_4, button_5,
                      button_6, button_7, button_8, button_9, row_width=2)
    client.send_message(message.chat.id,
                        'Выберите тематику вашего мероприятия:',
                        reply_markup=markup_inline)


def edit_event_step2(message: types.Message, event_id, theme):
    client.send_message(message.chat.id, 'Введите название вашего мероприятия:')
    client.register_next_step_handler(message, edit_event_step3, event_id, theme)


def edit_event_step3(message: types.Message, event_id, theme):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_text(message.text):
                client.send_message(message.chat.id,
                                    'Введите описание вашего мероприятия:')
                client.register_next_step_handler(message, edit_event_step4,
                                                  event_id, theme, message.text)
            else:
                client.send_message(message.chat.id,
                                    'В названии мероприятия должно быть хотя бы одно слово. '
                                    + 'Попробуйте ещё раз.')
                client.register_next_step_handler(message, edit_event_step3, event_id, theme)
        else:
            client.send_message(message.chat.id,
                                'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step3, event_id, theme)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step3, event_id, theme)


def edit_event_step4(message: types.Message, event_id, theme, name):
    if message.text is not None:
        if len(message.text) < 255:
            if is_correct_text(message.text):
                client.send_message(message.chat.id,
                                    'Введите дату вашего мероприятия в формате дд.мм.гггг:')
                client.register_next_step_handler(message, edit_event_step5,
                                                  event_id, theme, name, message.text)
            else:
                client.send_message(message.chat.id,
                                    'В описании мероприятия должно быть хотя бы одно слово. '
                                    + 'Попробуйте ещё раз.')
                client.register_next_step_handler(message, edit_event_step4,
                                                  event_id, theme, name)
        else:
            client.send_message(message.chat.id,
                                'Слишком длинная строка. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step4,
                                              event_id, theme, name)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step4,
                                          event_id, theme, name)


def edit_event_step5(message: types.Message, event_id, theme, name, description):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            user_date = datetime.date(user_datetime.year, user_datetime.month, user_datetime.day)
            now_date = datetime.date.today()
            if user_date < now_date:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, edit_event_step5,
                                                  event_id, theme, name, description)
            else:
                client.send_message(message.chat.id,
                                    'Введите время вашего мероприятия (в формате чч:мм):')
                client.register_next_step_handler(message, edit_event_step6,
                                                  event_id, theme, name, description, message.text)
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step5,
                                              event_id, theme, name, description)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step5,
                                          event_id, theme, name, description)


def edit_event_step6(message: types.Message, event_id, theme, name, description, date):
    if message.text is not None and is_correct_time(message.text):
        now_date = datetime.datetime.now()
        now_date_str = now_date.strftime("%d.%m.%Y")
        if now_date_str == date and int(message.text.split(':')[0]) * 100 + int(
                message.text.split(':')[1]) <= now_date.hour * 100 + now_date.minute:
            client.send_message(message.chat.id,
                                'Невозможное время. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step6,
                                              event_id, theme, name, description, date)
        else:
            client.send_message(message.chat.id,
                                'Введите место проведения или прикрепите геолокацию:')
            client.register_next_step_handler(message, edit_event_step7,
                                              event_id, theme, name,
                                              description, date, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step6,
                                          event_id, theme, name, description, date)


def edit_event_step7(message: types.Message, event_id, theme, name, description, date, time):
    latitude = None
    longitude = None

    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.text is not None:
        loc = message.text
        try:
            location = geocode(loc, provider="nominatim", user_agent='my_request')
            point = location.geometry.iloc[0]
            latitude = point.y
            longitude = point.x
        except Exception:
            client.send_message(message.chat.id,
                                'Некорректный адрес. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step7,
                                              event_id, theme, name, description, date, time)
            return
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step7,
                                          event_id, theme, name, description, date, time)
        return

    place = str(latitude) + '|' + str(longitude)
    client.send_message(message.chat.id,
                        'Введите стоимость посещения (целое число):')
    client.register_next_step_handler(message, edit_event_step8,
                                      event_id, theme, name, description, date, time, place)



def edit_event_step8(message: types.Message, event_id, theme, name, description, date, time, place):
    if message.text is not None and is_correct_digit(message.text):
        client.send_message(message.chat.id,
                            'Введите количество мест (0 - не ограничено):')
        client.register_next_step_handler(message, edit_event_step9,
                                          event_id, theme, name, description,
                                          date, time, place, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step8,
                                          event_id, theme, name, description, date, time, place)


def edit_event_step9(message: types.Message, event_id, theme,
                     name, description, date, time, place, pay):
    if message.text is not None and is_correct_digit(message.text):
        client.send_message(message.chat.id,
                            'Вы действительно хотите редактировать ваше мероприятие? \
                            Введите "Да" или "Нет".')
        client.register_next_step_handler(message, edit_event_step10,
                                          event_id, theme, name, description,
                                          date, time, place, pay, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step9,
                                          event_id, theme, name, description,
                                          date, time, place, pay)


def edit_event_step10(message: types.Message, event_id, theme, name,
                      description, date, time, place, pay, seats):
    if message.text is not None:
        if message.text.lower() == "да":
            if bd.edit_event_info_in_database(event_id, name, description, date,
                                           time, place, theme, pay, seats, message.chat.id):
                client.send_message(message.chat.id,
                                    'Данные успешно изменены')
            else:
                client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        elif message.text.lower() != "нет":
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, edit_event_step10,
                                              event_id, theme, name, description,
                                              date, time, place, pay, seats)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_event_step10,
                                          event_id, theme, name, description, date, time, place, pay, seats)


def delete_event(message: types.Message, event_id):
    client.send_message(message.chat.id,
                        'Вы действительно хотите удалить мероприятие? '
                        + 'Введите "Да" или "Нет".')
    client.register_next_step_handler(message, delete_event_step2, event_id)


def delete_event_step2(message: types.Message, event_id):
    if message.text is not None:
        if message.text.lower() == "да":
            event = bd.get_event_info_from_database(event_id)
            if event is False:
                client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
                return
            if event is None:
                client.send_message(message.chat.id,
                                'Мероприятие не существует.')
                return
            text = ('Мероприятие "' + event.event_name
                    + '", на которое вы были зарегистрированы, '
                    + 'удалено из списка мероприятий его создателем.')
            list_users = bd.get_user_who_registered(event_id)
            if list_users is False:
                client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
                return
            for user in list_users:
                client.send_message(user, text)
            if bd.delete_event_from_database(event_id):
                client.send_message(message.chat.id,
                                'Мероприятие успешно удалено.')
            else:
                client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        elif message.text.lower() != "нет":
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, delete_event_step2, event_id)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, delete_event_step2, event_id)


def show_coord(message: types.Message, latitude, longitude):
    client.send_location(message.chat.id, latitude, longitude)


def register_on_event(message: types.Message, event_id):
    client.send_message(message.chat.id,
                        'Вы действительно хотите зарегистрироваться? Введите "Да" или "Нет".')
    client.register_next_step_handler(message, register_on_event_step2, event_id)


def register_on_event_step2(message: types.Message, event_id):
    if message.text is not None:
        if message.text.lower() == "да":
            if bd.add_registration_in_database(message.chat.id, event_id):
                client.send_message(message.chat.id,
                            'Вы успешно зарегистрированы.')
            else:
                client.send_message(message.chat.id,
                            'Не удалось выполнить запрос.')
        elif message.text.lower() != "нет":
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, register_on_event_step2, event_id)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, register_on_event_step2, event_id)


def cansel_registration(message: types.Message, event_id):
    client.send_message(message.chat.id,
                        'Вы действительно хотите отменить регистрацию? Введите "Да" или "Нет".')
    client.register_next_step_handler(message, cansel_registration_step2, event_id)


def cansel_registration_step2(message: types.Message, event_id):
    if message.text is not None:
        if message.text.lower() == "да":
            if bd.delete_registration_from_database(message.chat.id, event_id):
                client.send_message(message.chat.id,
                            'Регистрация успешно отменена.')
            else:
                client.send_message(message.chat.id,
                            'Не удалось выполнить запрос.')
        elif message.text.lower() != "нет":
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, cansel_registration_step2, event_id)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, cansel_registration_step2, event_id)


def events_in_user_plans(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_in_user_plans_from_database(message.chat.id)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>', callback_data='next_page_2|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Вы еще не зарегистрировались ни на одно мероприятие.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия, на которые вы зарегистрировались:',
                        reply_markup=markup_inline)


def events_in_user_plans_next(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_in_user_plans_from_database(message.chat.id)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_2|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_2|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_2|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_2|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Вы еще не зарегистрировались ни на одно мероприятие.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def events_of_user(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_of_user_from_database(message.chat.id)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_3|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Вы еще не создали ни одного мероприятия.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия, которые вы создали:',
                        reply_markup=markup_inline)


def events_of_user_next(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_of_user_from_database(message.chat.id)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_3|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_3|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_3|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_3|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Вы еще не создали ни одного мероприятия.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def search(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='По локации',
                                          callback_data='search_location')
    button_2 = types.InlineKeyboardButton(text='По дате и времени',
                                          callback_data='search_date')
    button_3 = types.InlineKeyboardButton(text='По тематике',
                                          callback_data='search_theme')
    button_4 = types.InlineKeyboardButton(text='По стоимости',
                                          callback_data='search_pay')
    markup_inline.add(button_1, button_2, button_3, button_4,
                      row_width=2)
    client.send_message(message.chat.id,
                        'Выберите фильтр для поиска:',
                        reply_markup=markup_inline)


def search_location(message: types.Message):
    client.send_message(message.chat.id,
                        'Введите место проведения или прикрепите геолокацию:')
    client.register_next_step_handler(message, search_location_step2)


def search_location_step2(message: types.Message):
    latitude = None
    longitude = None

    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.text is not None:
        loc = message.text
        try:
            location = geocode(loc, provider="nominatim", user_agent='my_request')
            point = location.geometry.iloc[0]
            latitude = point.y
            longitude = point.x
        except Exception:
            client.send_message(message.chat.id,
                                'Некорректный адрес. Попробуйте ещё раз.')
            client.register_next_step_handler(message, search_location_step2)
            return
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, search_date_step2)
        return

    place = str(latitude) + '|' + str(longitude)
    show_events_filter_location(message, place)


def show_events_filter_location(message: types.Message, place):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_location_from_database(place.split('|')[0],
                                                         place.split('|')[1])
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_4|' + place + '|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий в данной локации нет.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия в данной локации:',
                        reply_markup=markup_inline)


def show_events_filter_location_next(message: types.Message, place, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_location_from_database(place.split('|')[0],
                                                         place.split('|')[1])
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_4|' + place + '|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_4|' + place + '|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_4|' + place + '|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_4|' + place + '|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий в данной локации нет.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def search_date(message: types.Message):
    client.send_message(message.chat.id,
                        'Введите нижнюю границу поиска в формате дд.мм.гггг:')
    client.register_next_step_handler(message, search_date_step2)


def search_date_step2(message: types.Message):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            user_date = datetime.date(user_datetime.year,
                                      user_datetime.month,
                                      user_datetime.day)
            now_date = datetime.date.today()
            if user_date < now_date:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, search_date_step2)
            else:
                client.send_message(message.chat.id,
                                    'Введите верхнюю границу поиска в формате дд.мм.гггг:')
                client.register_next_step_handler(message, search_date_step3, message.text)
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, search_date_step2)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, search_date_step2)


def search_date_step3(message: types.Message, date_begin):
    if message.text is not None:
        try:
            user_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            begin_datetime = datetime.datetime.strptime(date_begin, "%d.%m.%Y")
            if user_datetime < begin_datetime:
                client.send_message(message.chat.id,
                                    'Невозможная дата. Попробуйте еще раз.')
                client.register_next_step_handler(message, search_date_step3, date_begin)
            else:
                show_events_filter_date(message, date_begin, message.text)
        except ValueError:
            client.send_message(message.chat.id,
                                'Некорректный ввод. Попробуйте ещё раз.')
            client.register_next_step_handler(message, search_date_step3, date_begin)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, search_date_step3, date_begin)


def show_events_filter_date(message: types.Message, date_begin, date_end):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_date_from_database(date_begin, date_end)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_5|'
                                            + date_begin + '|' + date_end + '|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий, проходящих в данные даты, нет.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия, проходящие в данные даты:',
                        reply_markup=markup_inline)


def show_events_filter_date_next(message: types.Message, date_begin, date_end, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_date_from_database(date_begin, date_end)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_5|'
                                             + date_begin + '|' + date_end + '|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_5|'
                                             + date_begin + '|' + date_end + '|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_5|'
                                            + date_begin + '|' + date_end + '|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_5|'
                                            + date_begin + '|' + date_end + '|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий, проходящих в данные даты, нет.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def search_theme(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text='Выставка',
                                          callback_data='search_theme_st2|Выставка|')
    button_2 = types.InlineKeyboardButton(text='Концерт',
                                          callback_data='search_theme_st2|Концерт|')
    button_3 = types.InlineKeyboardButton(text='Спектакль',
                                          callback_data='search_theme_st2|Спектакль|')
    button_4 = types.InlineKeyboardButton(text='Обучение',
                                          callback_data='search_theme_st2|Обучение|')
    button_5 = types.InlineKeyboardButton(text='Встреча',
                                          callback_data='search_theme_st2|Встреча|')
    button_6 = types.InlineKeyboardButton(text='Экскурсия',
                                          callback_data='search_theme_st2|Экскурсия|')
    button_7 = types.InlineKeyboardButton(text='Праздник',
                                          callback_data='search_theme_st2|Праздник|')
    button_8 = types.InlineKeyboardButton(text='Другое',
                                          callback_data='search_theme_st2|Другое|')
    button_9 = types.InlineKeyboardButton(text='Без категории',
                                          callback_data='search_theme_st2|Без категории|')
    markup_inline.add(button_1, button_2, button_3, button_4, button_5,
                      button_6, button_7, button_8, button_9, row_width=2)
    client.send_message(message.chat.id,
                        'Выберите тематику:',
                        reply_markup=markup_inline)


def show_events_filter_theme(message: types.Message, theme):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_theme_from_database(theme)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_6|' + theme + '|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий данной тематики нет.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия данной тематики:',
                        reply_markup=markup_inline)


def show_events_filter_theme_next(message: types.Message, theme, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_theme_from_database(theme)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_6|' + theme + '|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_6|' + theme + '|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_6|' + theme + '|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_6|' + theme + '|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий данной тематики нет.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


def search_pay(message: types.Message):
    client.send_message(message.chat.id,
                        'Введите минимальную стоимость:')
    client.register_next_step_handler(message, search_pay_step2)


def search_pay_step2(message: types.Message):
    if message.text is not None and is_correct_digit(message.text):
        client.send_message(message.chat.id,
                            'Введите максимальную стоимость:')
        client.register_next_step_handler(message, search_pay_step3, message.text)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, search_pay_step2)


def search_pay_step3(message: types.Message, min_pay):
    if message.text is not None and is_correct_digit(message.text):
        if int(message.text) >= int(min_pay):
            show_events_filter_pay(message, min_pay, message.text)
        else:
            client.send_message(message.chat.id,
                                'Максимальная сумма не может быть меньше минимальной. '
                                + 'Попробуйте ещё раз.')
            client.register_next_step_handler(message, search_pay_step3, min_pay)
    else:
        client.send_message(message.chat.id,
                            'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, search_pay_step3, min_pay)


def show_events_filter_pay(message: types.Message, min_pay, max_pay):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_pay_from_database(min_pay, max_pay)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 <= number <= 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > 5:
            break

    if 0 != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_7|'
                                            + min_pay + '|' + max_pay + '|0')
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий в данном диапазоне стоимости нет.')
        return
    client.send_message(message.chat.id,
                        'Мероприятия в данном диапазоне стоимости:',
                        reply_markup=markup_inline)


def show_events_filter_pay_next(message: types.Message, min_pay, max_pay, page):
    markup_inline = types.InlineKeyboardMarkup()
    events = bd.get_events_filter_pay_from_database(min_pay, max_pay)
    if events is False:
        client.send_message(message.chat.id,
                                'Не удалось выполнить запрос.')
        return
    number = 0
    for event in events:
        number += 1
        if 1 + page * 5 <= number <= page * 5 + 5:
            button = types.InlineKeyboardButton(
                text=event.event_name + '\n' + event.event_date + ' ' + event.event_time,
                callback_data='show_event|' + str(event.event_id))
            markup_inline.add(button)
        elif number > page * 5 + 5:
            break
    if page not in (0, (len(events) - 1) // 5):
        button1 = types.InlineKeyboardButton(text='<',
                                             callback_data='prev_page_7|'
                                             + min_pay + '|' + max_pay + '|' + str(page))
        button2 = types.InlineKeyboardButton(text='>',
                                             callback_data='next_page_7|'
                                             + min_pay + '|' + max_pay + '|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text='<',
                                            callback_data='prev_page_7|'
                                            + min_pay + '|' + max_pay + '|' + str(page))
        markup_inline.add(button)
    elif page != (len(events) - 1) // 5 and number != 0:
        button = types.InlineKeyboardButton(text='>',
                                            callback_data='next_page_7|'
                                            + min_pay + '|' + max_pay + '|' + str(page))
        markup_inline.add(button)
    elif number == 0:
        client.send_message(message.chat.id,
                            'Мероприятий в данном диапазоне стоимости нет.')
        return
    client.edit_message_reply_markup(chat_id=message.chat.id,
                                     message_id=message.id,
                                     reply_markup=markup_inline)


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
    elif func == 'show_coord':
        latitude = call.data.split('|')[1]
        longitude = call.data.split('|')[2]
        show_coord(call.message, latitude, longitude)
    elif func == 'register':
        event_id = int(call.data.split('|')[1])
        register_on_event(call.message, event_id)
    elif func == 'cansel_reg':
        event_id = int(call.data.split('|')[1])
        cansel_registration(call.message, event_id)
    elif func == 'next_page_2':
        page = int(call.data.split('|')[1])
        events_in_user_plans_next(call.message, page + 1)
    elif func == 'prev_page_2':
        page = int(call.data.split('|')[1])
        events_in_user_plans_next(call.message, page - 1)
    elif func == 'edit_event_st2':
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                         inline_message_id=None)
        theme = call.data.split('|')[1]
        event_id = int(call.data.split('|')[2])
        edit_event_step2(call.message, event_id, theme)
    elif func == 'next_page_3':
        page = int(call.data.split('|')[1])
        events_of_user_next(call.message, page + 1)
    elif func == 'prev_page_3':
        page = int(call.data.split('|')[1])
        events_of_user_next(call.message, page - 1)
    elif func == 'search_location':
        search_location(call.message)
    elif func == 'search_date':
        search_date(call.message)
    elif func == 'search_theme':
        search_theme(call.message)
    elif func == 'search_pay':
        search_pay(call.message)
    elif func == 'next_page_4':
        place = int(call.data.split('|')[1])
        page = int(call.data.split('|')[2])
        show_events_filter_location_next(call.message, place, page + 1)
    elif func == 'prev_page_4':
        place = int(call.data.split('|')[1])
        page = int(call.data.split('|')[2])
        show_events_filter_location_next(call.message, place, page - 1)
    elif func == 'next_page_5':
        date_begin = int(call.data.split('|')[1])
        date_end = int(call.data.split('|')[2])
        page = int(call.data.split('|')[3])
        show_events_filter_date_next(call.message, date_begin, date_end, page + 1)
    elif func == 'prev_page_5':
        date_begin = int(call.data.split('|')[1])
        date_end = int(call.data.split('|')[2])
        page = int(call.data.split('|')[3])
        show_events_filter_date_next(call.message, date_begin, date_end, page - 1)
    elif func == 'search_theme_st2':
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                         inline_message_id=None)
        theme = call.data.split('|')[1]
        show_events_filter_theme(call.message, theme)
    elif func == 'next_page_6':
        theme = int(call.data.split('|')[1])
        page = int(call.data.split('|')[2])
        show_events_filter_theme_next(call.message, theme, page + 1)
    elif func == 'prev_page_6':
        theme = int(call.data.split('|')[1])
        page = int(call.data.split('|')[2])
        show_events_filter_theme_next(call.message, theme, page - 1)
    elif func == 'next_page_7':
        min_pay = int(call.data.split('|')[1])
        max_pay = int(call.data.split('|')[2])
        page = int(call.data.split('|')[3])
        show_events_filter_date_next(call.message, min_pay, max_pay, page + 1)
    elif func == 'prev_page_7':
        min_pay = int(call.data.split('|')[1])
        max_pay = int(call.data.split('|')[2])
        page = int(call.data.split('|')[3])
        show_events_filter_pay_next(call.message, min_pay, max_pay, page - 1)


def unknown(message: types.Message):
    client.send_message(message.chat.id, 'Я вас не понимаю. Введите другой запрос.')


client.infinity_polling()
