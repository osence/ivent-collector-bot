import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", database="chat_bot2")

class Event:
    def __init__(self, id, name, description, date, time, place, subject,
                 pay, number_of_seats, who_create):
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


def add_event_in_database(name, description, date, time, place, theme, pay, seats, user_id):
    cursor = conn.cursor()
    date_elements = str(date).split('.')
    date_right = date_elements[2] + '-' + date_elements[1] + '-' + date_elements[0]
    sql = "INSERT INTO Events_t(event_name, event_description, event_date,\
     event_time, event_place, event_subject,\
     event_pay, event_number_of_seats, user_who_creat)\
     VALUES (%s, %s, %s, %s, %s, %s , %s, %s, %s)"

    val = (name, description, date_right, time, place, theme, pay, seats, user_id)
    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def edit_event_info_in_database(event_id, name, description, date, time, place,
                                theme, pay, seats, user_id):
    cursor = conn.cursor()
    date_elements = str(date).split('.')
    date_right = date_elements[2] + '-' + date_elements[1] + '-' + date_elements[0]
    sql = "UPDATE Events_t set Events_t.event_name = %s,\
    Events_t.event_description = %s, Events_t.event_date = %s,\
    Events_t.event_time = %s, Events_t.event_place = %s, \
    Events_t.event_subject = %s,\
    Events_t.event_pay = %s, Events_t.event_number_of_seats = %s, Events_t.user_who_creat = %s\
    where Events_t.event_id = %s"

    val = name, description, date_right, time, place, theme, pay, seats, user_id, event_id
    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def delete_event_from_database(event_id):
    cursor = conn.cursor()
    sql = "DELETE FROM events_t WHERE events_t.event_id = "+str(event_id)
    try:
        cursor.execute(sql)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def id_in_database(user_id):
    cursor = conn.cursor()
    sql = "SELECT count(*) FROM users where users.users_id =" +str(user_id)
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        check = data[0]
        if check > 0:
            return True
        return False
    except:
        conn.rollback()
        return "Не удалось выполнить запрос."


def add_user_in_database(name, birthday, user_id):
    cursor = conn.cursor()
    date_elements = str(birthday).split('.')
    date_right = date_elements[2] + '-' + date_elements[1] + '-' + date_elements[0]
    sql = "Insert into users (users_id,FIO, dataBirthday) values (%s,%s,%s)"
    val = (user_id,name, date_right)

    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def edit_user_in_database(name, birthday, user_id):
    cursor = conn.cursor()
    date_elements = str(birthday).split('.')
    date_right = date_elements[2] + '-' + date_elements[1] + '-' + date_elements[0]
    sql = "UPDATE users set users.FIO = %s, users.dataBirthday = %s\
    where users.users_id = %s"
    val = (name, date_right, user_id)
    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def get_events_from_database():
    cursor = conn.cursor()
    sql = "SELECT * from events_t ORDER BY events_t.event_date, events_t.event_time"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        event_list = []
        for row in data:
            date_elements = str(row[3]).split('-')
            time = str(row[4]).split(':')
            date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
            time_right = time[0] + ':' + time[1]
            event_list.append(Event(row[0], row[1], row[2],
                                    date_right, time_right,
                                    row[5], row[6], row[7],
                                    row[8], row[9]))
        return event_list
    except:
        conn.rollback()
        return False


def get_user_info_from_database(user_id):
    cursor = conn.cursor()
    sql = "SELECT FIO, dataBirthday from users where users.users_id = " + str(user_id)
    try:
        cursor.execute(sql)
    except:
        conn.rollback()
        return False

    data = cursor.fetchone()
    if data is None:
        return None

    user_info = []
    user_info.append(data[0])
    date_elements = str(data[1]).split('-')
    user_info.append(date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0])
    return user_info


def get_event_info_from_database(event_id):
    cursor = conn.cursor()
    sql = "SELECT * from events_t\
    where event_id = " + str(event_id)
    try:
        cursor.execute(sql)
    except:
        conn.rollback()
        return False

    data=cursor.fetchone()
    if data is None:
        return None

    date_elements = str(data[3]).split('-')
    time = str(data[4]).split(':')
    date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
    time_bag = time[0] + ':' + time[1]

    return Event(data[0], data[1], data[2],
                 date_right, time_bag, data[5],
                 data[6], data[7], data[8], data[9])


def user_is_registered(user_id, event_id):
    cursor = conn.cursor()
    sql = "SELECT count(*) FROM participations\
    where (participations.event_id = %s)\
    and (participations.users_id = %s)"
    val = (event_id, user_id)
    try:
        cursor.execute(sql,val)
    except:
        conn.rollback()
        return 'Не удалось выполнить запрос'

    data = cursor.fetchone()
    check = data[0]
    return check > 0


def add_registration_in_database(user_id, event_id):
    cursor = conn.cursor()
    sql = "INSERT INTO participations\
    (users_id, event_id) VALUES (%s, %s)"

    val = (user_id, event_id)
    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def delete_registration_from_database(user_id, event_id):
    cursor = conn.cursor()
    sql = "DELETE FROM participations\
    WHERE (participations.users_id = %s)\
    and (participations.event_id = %s)"
    val = (user_id, event_id)

    try:
        cursor.execute(sql, val)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False


def get_events_in_user_plans_from_database(user_id):
    cursor = conn.cursor()
    sql = ("SELECT * FROM events_t JOIN participations ON\
    (events_t.event_id = participations.event_id)\
    where participations.users_id = "+str(user_id)
    +" ORDER BY events_t.event_date, events_t.event_time"
    )

    try:
        cursor.execute(sql)
    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    event_list = []
    for row in data:
        date_elements = str(row[3]).split('-')
        time = str(row[4]).split(':')
        date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
        time_right = time[0] + ':' + time[1]
        event_list.append(Event(row[0], row[1], row[2],
                                date_right, time_right, row[5],
                                row[6], row[7], row[8], row[9]))
    return event_list


def get_events_of_user_from_database(user_id):
    cursor = conn.cursor()
    sql = ("SELECT * FROM events_t where events_t.user_who_creat = "
           +str(user_id)
           +" ORDER BY events_t.event_date, events_t.event_time")

    try:
        cursor.execute(sql)
        data=cursor.fetchall()
        event_list=[]
        for row in data:
            date_elements = str(row[3]).split('-')
            time = str(row[4]).split(':')
            date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
            time_right = time[0] + ':' + time[1]
            event_list.append(Event(row[0], row[1], row[2],
                                    date_right, time_right, row[5],
                                    row[6], row[7], row[8], row[9]))
        return event_list
    except:
        conn.rollback()
        return False


def get_events_filter_location_from_database(latitude, longitude):
    cursor =conn.cursor()
    sql = ("SELECT * FROM Events_t where Events_t.event_place LIKE '"
           + str(round(float(latitude),3)) + "%|"
           + str(round(float(longitude),3)) + "%'"
           +" ORDER BY events_t.event_date, events_t.event_time")
    try:
        cursor.execute(sql)
    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    event_list = []
    for row in data:
        date_elements = str(row[3]).split('-')
        time = str(row[4]).split(':')
        date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
        time_right = time[0] + ':' + time[1]
        event_list.append(Event(row[0], row[1], row[2],
                                date_right, time_right, row[5],
                                row[6], row[7], row[8], row[9]))

    return event_list


def get_events_filter_date_from_database(date_begin, date_end):
    cursor = conn.cursor()
    sql = ("SELECT * FROM Events_t where (Events_t.event_date >= %s)\
    and (Events_t.event_date <= %s)"
    +" ORDER BY events_t.event_date, events_t.event_time")

    date_begin_elements = str(date_begin).split('.')
    date_end_elements = str(date_end).split('.')
    date_begin_right = (date_begin_elements[2] +
                        '-' + date_begin_elements[1] +
                        '-' + date_begin_elements[0])
    date_end_right = (date_end_elements[2] +
                      '-' + date_end_elements[1] +
                      '-' + date_end_elements[0])

    val = (date_begin_right, date_end_right)
    try:
        cursor.execute(sql,val)

    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    event_list = []
    for row in data:
        date_elements = str(row[3]).split('-')
        time = str(row[4]).split(':')
        date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
        time_right = time[0] + ':' + time[1]
        event_list.append(Event(row[0], row[1], row[2],
                                date_right, time_right, row[5],
                                row[6], row[7], row[8], row[9]))

    return event_list


def get_events_filter_theme_from_database(theme):
    cursor = conn.cursor()
    sql = ("SELECT * FROM events_t where events_t.event_subject ='"
           + theme + "'"
           + " ORDER BY events_t.event_date, events_t.event_time")

    try:
        cursor.execute(sql)
    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    event_list = []
    for row in data:
        date_elements = str(row[3]).split('-')
        time = str(row[4]).split(':')
        date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
        time_right = time[0] + ':' + time[1]
        event_list.append(Event(row[0], row[1], row[2],
                                date_right, time_right, row[5],
                                row[6], row[7], row[8], row[9]))
    return event_list


def get_events_filter_pay_from_database(min_pay, max_pay):
    cursor = conn.cursor()
    sql =  ("SELECT * FROM Events_t where (Events_t.event_pay >= %s) \
    and (Events_t.event_pay <= %s)"
    +" ORDER BY events_t.event_date, events_t.event_time")

    val = (min_pay, max_pay)
    try:
        cursor.execute(sql,val)   
    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    event_list = []
    for row in data:
        date_elements = str(row[3]).split('-')
        time = str(row[4]).split(':')
        date_right = date_elements[2] + '.' + date_elements[1] + '.' + date_elements[0]
        time_right = time[0] + ':' + time[1]
        event_list.append(Event(row[0], row[1], row[2],
                                date_right, time_right, row[5],
                                row[6], row[7], row[8], row[9]))
    return event_list


def get_user_who_registered(event_id):
    cursor =conn.cursor()
    sql = "SELECT users_id FROM Participations \
    where Participations.event_id = " + str(event_id)
    try:
        cursor.execute(sql)

    except:
        conn.rollback()
        return False

    data = cursor.fetchall()
    user_list = []
    for row in data:
        user_list.append(row[0])
    return user_list
