import datetime
import re
import telebot
from telebot import types
import configure

client = telebot.TeleBot(configure.config['token'])

class Ivent:
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

ivent_dict = {}
ivent_list = []
i = 0
user_set = dict()

# TODO сделать везде проверку на длину строк (слишком большие)
# TODO изменить логику поведения, чтоб можно было прервать
# add_ivent, edit_ivent, view_ivent, search_ivent
@client.message_handler(commands=['start', 'reset'])
def welcome_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id not in user_set.keys():
        # registration
        keyboard.add(*["Регистрация"])
        client.send_message(message.chat.id, 'Чтобы начать работать с ботом, вам необходимо зарегистрироваться.',
                        reply_markup=keyboard)
    else:
        keyboard.add(*["Создать мероприятие", "Посмотреть мероприятия"])
        keyboard.add(*["Мои события", "Мои планы"])
        keyboard.add(*["Поиск по событиям", "Мой аккаунт"])
        client.send_message(message.chat.id, 'Что ты хочешь сделать?',
                        reply_markup=keyboard)
    return

@client.message_handler(content_types=["text"])
def choose_handler(message: types.Message):    
    if message.text == "Регистрация":
        registration(message)
    elif message.chat.id not in user_set.keys():
        welcome_message(message)
    elif message.text == "Посмотреть мероприятия":
        show_ivents(message, 0)
    elif message.text == "Создать мероприятие":
        create_ivent(message)
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
    if isCorrectName(message.text):
        client.send_message(message.chat.id, 'Введите вашу дату рождения в формате дд.мм.гггг:')
        client.register_next_step_handler(message, registration_step3, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step2)

def registration_step3(message: types.Message, name):
    try:
        datetime.datetime.strptime(message.text,"%d.%m.%Y")
        client.send_message(message.chat.id, 'Вы успешно зарегистрированы')
        # TODO Здесь подключение к бд
        user_set[message.chat.id] = [name, message.text]
        welcome_message(message)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, registration_step3, name)

def info_account(message: types.Message):
    markup_inline = types.InlineKeyboardMarkup()
    button_edit_info = types.InlineKeyboardButton(text = 'Редактировать информацию', callback_data='edit_info|')
    markup_inline.add(button_edit_info)
    client.send_message(message.chat.id, 'Имя: ' + user_set[message.chat.id][0] + '\nДата рождения: ' + user_set[message.chat.id][1],
                        reply_markup=markup_inline)

def edit_info(message: types.Message):
    client.send_message(message.chat.id, 'Введите ваше ФИО:')
    client.register_next_step_handler(message, edit_info_step2)

def edit_info_step2(message: types.Message):
    if re.match(r'^[А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*( [А-ЯЁ][а-яё]+(-[А-Яа-яЁё][а-яё]+)*)+$', message.text) is not None:
        client.send_message(message.chat.id, 'Введите вашу дату рождения в формате дд.мм.гггг:')
        client.register_next_step_handler(message, edit_info_step3, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step2)

def edit_info_step3(message: types.Message, name):
    try:
        datetime.datetime.strptime(message.text,"%d.%m.%Y")
        client.send_message(message.chat.id, 'Данные успешно изменены')
        # TODO Здесь подключение к бд
        user_set[message.chat.id] = [name, message.text]
        welcome_message(message)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, edit_info_step3, name)

# TODO сделать ожидание, как везде, но учитывая callback
def create_ivent(message: types.Message):    
    markup_inline = types.InlineKeyboardMarkup()
    button_1 = types.InlineKeyboardButton(text = 'Выставка', callback_data='create_ivent_step2|Выставка')
    button_2 = types.InlineKeyboardButton(text = 'Концерт', callback_data='create_ivent_step2|Концерт')
    button_3 = types.InlineKeyboardButton(text = 'Спектакль', callback_data='create_ivent_step2|Спектакль')
    button_4 = types.InlineKeyboardButton(text = 'Обучение', callback_data='create_ivent_step2|Обучение')
    button_5 = types.InlineKeyboardButton(text = 'Встреча', callback_data='create_ivent_step2|Встреча')
    button_6 = types.InlineKeyboardButton(text = 'Экскурсия', callback_data='create_ivent_step2|Экскурсия')
    button_7 = types.InlineKeyboardButton(text = 'Праздник', callback_data='create_ivent_step2|Праздник')
    button_8 = types.InlineKeyboardButton(text = 'Другое', callback_data='create_ivent_step2|Другое')
    button_9 = types.InlineKeyboardButton(text = 'Без категории', callback_data='create_ivent_step2|Без категории')
    markup_inline.add(button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8, button_9, row_width = 2)
    client.send_message(message.chat.id, 'Выберите тематику вашего мероприятия:', reply_markup=markup_inline)

def create_ivent_step2(message: types.Message, theme):
    client.send_message(message.chat.id, 'Введите название вашего мероприятия:')
    client.register_next_step_handler(message, create_ivent_step3, theme)

def create_ivent_step3(message: types.Message, theme):
    if re.match(r'[А-ЯЁа-яёa-zA-Z]{3,}', message.text) is not None:
        client.send_message(message.chat.id, 'Введите описание вашего мероприятия:')
        client.register_next_step_handler(message, create_ivent_step4, theme, message.text)
    else:
        client.send_message(message.chat.id, 'В названии мероприятия должно быть хотя бы одно слово. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step3, theme)

def create_ivent_step4(message: types.Message, theme, name):
    # TODO Неверная регулярка
    if re.match(r'[А-ЯЁа-яёa-zA-Z]{3,}', message.text) is not None:
        client.send_message(message.chat.id, 'Введите дату вашего мероприятия в формате дд.мм.гггг:')
        client.register_next_step_handler(message, create_ivent_step5, theme, name, message.text)
    else:
        client.send_message(message.chat.id, 'В описании мероприятия должно быть хотя бы одно слово. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step4, theme, name)

def create_ivent_step5(message: types.Message, theme, name, description):
    try:
        user_datetime = datetime.datetime.strptime(message.text,"%d.%m.%Y")
        user_date = datetime.date(user_datetime.year, user_datetime.month, user_datetime.day)
        now_date = datetime.date.today()
        if user_date < now_date:
            client.send_message(message.chat.id, 'Невозможная дата. Попробуйте еще раз.')
            client.register_next_step_handler(message, create_ivent_step5, theme, name, description)
        else:
            client.send_message(message.chat.id, 'Введите время вашего мероприятия (в формате чч:мм):')
            client.register_next_step_handler(message, create_ivent_step6, theme, name, description, message.text)
    except ValueError:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step5, theme, name, description)

def create_ivent_step6(message: types.Message, theme, name, description, date):
    if re.match(r'([0-1][0-9]|2[0-3]):([0-5][0-9])', message.text) is not None:
        now_date = datetime.datetime.now()
        now_date_str = now_date.strftime("%d.%m.%Y")
        if now_date_str == date and int(message.text.split(':')[0]) * 100 + int(message.text.split(':')[1]) <= now_date.hour * 100 + now_date.minute:
            client.send_message(message.chat.id, 'Невозможное время. Попробуйте ещё раз.')
            client.register_next_step_handler(message, create_ivent_step6, theme, name, description, date)
        else:
            client.send_message(message.chat.id, 'Введите место проведения:')
            client.register_next_step_handler(message, create_ivent_step7, theme, name, description, date, message.text)
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step6, theme, name, description, date)

# TODO Координаты!
def create_ivent_step7(message: types.Message, theme, name, description, date, time):
    client.send_message(message.chat.id, 'Введите стоимость посещения (целое число):')
    client.register_next_step_handler(message, create_ivent_step8, theme, name, description, date, time, message.text)

def create_ivent_step8(message: types.Message, theme, name, description, date, time, place):
    if re.match(r'([1-9][0-9]+)|[0-9]', message.text) is not None:
        client.send_message(message.chat.id, 'Введите количество мест (0 - не ограничено):')
        client.register_next_step_handler(message, create_ivent_step9, theme, name, description, date, time, place, message.text)  
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step8, theme, name, description, date, time, place)

def create_ivent_step9(message: types.Message, theme, name, description, date, time, place, pay):
    if re.match(r'([1-9][0-9]+)|[0-9]', message.text) is not None:
        client.send_message(message.chat.id, 'Ваше мероприятие успешно добавлено.')
        global i # pylint: disable=global-statement
        # TODO Здесь подключение к бд
        ivent_list.append(Ivent(i, name, description, date, time, place, theme, pay, message.text, message.chat.id))
        i += 1
    else:
        client.send_message(message.chat.id, 'Некорректный ввод. Попробуйте ещё раз.')
        client.register_next_step_handler(message, create_ivent_step9, theme, name, description, date, time, place, pay)
        
def show_ivents(message: types.Message, page):
    markup_inline = types.InlineKeyboardMarkup()
    # TODO тут должно быть получение списка из бд
    number = 0
    for ivent in ivent_list: 
        number += 1
        if number >= 1+page*5 and number <= page*5+5:
            button = types.InlineKeyboardButton(text = ivent.event_name + '\n' + ivent.event_date + ' ' + ivent.event_time, callback_data='show_ivent|' + str(ivent.event_id))
            markup_inline.add(button)
        elif number > page*5+5:
            break
    if page != 0 and page != (len(ivent_list) - 1)//5:
        button1 = types.InlineKeyboardButton(text = '<', callback_data='prev_page|' + str(page))
        button2 = types.InlineKeyboardButton(text = '>', callback_data='next_page|' + str(page))
        markup_inline.add(button1, button2, row_width=2)
    elif page != 0:
        button = types.InlineKeyboardButton(text = '<', callback_data='prev_page|' + str(page))
        markup_inline.add(button)
    elif page != (len(ivent_list) - 1)//5:
        button = types.InlineKeyboardButton(text = '>', callback_data='next_page|' + str(page))
        markup_inline.add(button)
    client.send_message(message.chat.id, 'Предстоящие мероприятия:', reply_markup=markup_inline)

def show_ivent(message: types.Message, id):
    # TODO Здесь запрос к БД по id вместо того, что ниже
    cur_ivent = None
    for ivent in ivent_list:
        if ivent.event_id == id:
            cur_ivent = ivent
            break
    seats = ''
    if cur_ivent.event_number_of_seats == 0:
        seats = 'Не ограничено'
    else:
        seats = cur_ivent.event_number_of_seats
    text = ('Название: ' + cur_ivent.event_name + 
            '\nДата: ' + cur_ivent.event_date + 
            '\nВремя: ' + cur_ivent.event_time +
            '\nОписание: ' + cur_ivent.event_description + 
            '\nМесто: ' + cur_ivent.event_place + 
            '\nКатегория: ' + cur_ivent.event_subject +
            '\nСтоимость: ' + cur_ivent.event_pay + 
            '\nКоличество мест: ' + seats
            )
    if cur_ivent.user_who_create == message.chat.id:
        markup_inline = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text = 'Редактировать', callback_data='edit_ivent|' + str(id))
        button2 = types.InlineKeyboardButton(text = 'Удалить', callback_data='delete_ivent|' + str(id))
        markup_inline.add(button1, button2)
        client.send_message(message.chat.id, text, reply_markup=markup_inline)
    else:
        # TODO Регистрация
        client.send_message(message.chat.id, text)

# TODO Редактирование мероприятия
def edit_ivent(message: types.Message, id):
    client.send_message(message.chat.id, 'Тут можно будет редактировать')

# TODO Удаление мероприятия
def delete_ivent(message: types.Message, id):
    client.send_message(message.chat.id, 'Тут можно будет удалять')

# Обработка нажатий на кнопки
@client.callback_query_handler(func = lambda call: True)
def answer(call):
    func = call.data.split('|')[0]
    if func == 'edit_info':           
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, inline_message_id=None)
        edit_info(call.message)
    elif func == 'create_ivent_step2':
        client.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, inline_message_id=None)
        theme = call.data.split('|')[1]
        create_ivent_step2(call.message, theme)
    # TODO изменить, чтоб сообщение заново не отправлялось
    elif func == 'next_page':
        client.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        page = int(call.data.split('|')[1])
        show_ivents(call.message, page+1)
    elif func == 'prev_page':
        client.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        page = int(call.data.split('|')[1])
        show_ivents(call.message, page-1)
    elif func == 'show_ivent':
        ivent_id = int(call.data.split('|')[1])
        show_ivent(call.message, ivent_id)
    elif func == 'edit_ivent':
        ivent_id = int(call.data.split('|')[1])
        edit_ivent(call.message, ivent_id)
    elif func == 'delete_ivent':
        ivent_id = int(call.data.split('|')[1])
        delete_ivent(call.message, ivent_id)

client.infinity_polling()
