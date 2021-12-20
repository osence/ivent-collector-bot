import db
import pytest

@pytest.mark.parametrize("name, descrip,date, time,place,type,\
    cost,seats,who_create, output",[
        #1 Неправильный who_create
        ('Новый год','Отпразновать\
        Новый Год','31.12.2021','13:40','Дом','Сбор',0,10,10,False),\
        #2
        ('Красивый салют','Посмотреть салют 1 числа\
         из окна','01.01.2022','00:05','Дом','Семейный вечер',0,10,4,True),\
        #3
        ('Проект db','Сдать проект до конца года и\
         получить зачет','24.12.2021','15:20','ПетрГУ','Учеба',0,4,3,True),\
        #4
        ('Вечер поэзии','Встреча поэтов города\
         Петрозаводск','08.11.2021','19:00','61.786153|34.352475','творчество',0,50,4,True),\
        #5 Не написано название мероприятия
        (None,'Встреча поэтов города\
         Петрозаводск','08.11.2021','19:00','61.786153,34.352475','творчество',0,50,3,False),\
        #6 Не написано описание
        ('Вечер поэзии',None,'08.11.2021','19:00','61.786153,34.352475','творчество',0,50,4,False),\
        #7 Неправильная дата события
        ('Вечер поэзии','Встреча поэтом города\
         Петрозаводск','08.31.2021','19:00','61.786153,34.352475','творчество',0,50,4,False),\
        #8 Неправильные координаты
        ('Вечер поэзии','Встреча поэтом города\
         Петрозаводск','08.11.2021','19:00',None,'творчество',0,50,4,False),\
        #9 Не написана тематика
        # ('Вечер поэзии','Встреча поэтом города\
        #  Петрозаводск','08.11.2021','19:00','61.786153,34.352475',None,0,50,4,False),\
        #10 Не написана цена мероприятия
        ('Вечер поэзии','Встреча поэтом города\
         Петрозаводск','08.11.2021','19:00','61.786153,34.352475','творчество','',50,4,False),\
        #11 Не написано количество мест
        ('Вечер поэзии','Встреча поэтом города\
         Петрозаводск','08.11.2021','19:00','61.786153,34.352475','творчество',0,'',4,False)])
def test_add_event_in_database(name,descrip,date,time,place,type,cost,seats,who_create,output):
    assert db.add_event_in_database(name,descrip,date,time,place,type,cost,seats,who_create)==output

@pytest.mark.parametrize('name, birthday, user_id, output',[('Чайникова Полина','11.02.1999',42,True),\
        (None,'15.03.2001',15,False),('Миша Смирнов','20.34.2003',46,False),('Ефимова Дарья','14.08.2008',6,False)])
def test_add_user(name, birthday, user_id,output):
    assert db.add_user_in_database(name,birthday,user_id)==output

@pytest.mark.parametrize('name, birthday, user_id, output',[(None,'15.03.2001',16,False),\
    ('Миша Смирнов','20.34.2003',36,False),('Миша Смирнов','15.03.2001',16,True),\
        ('Миша Смирнов','15.03.2001',106,True)])
def test_edit_user(name, birthday, user_id,output):
    assert db.edit_user_in_database(name,birthday,user_id)==output

@pytest.mark.parametrize('user_id, event_id, output',[(3,64,True),(3,194,False)])
def test_add_registration(user_id, event_id,output):
    assert db.add_registration_in_database(user_id,event_id)==output

@pytest.mark.parametrize('user_id, event_id, output',[(3,64,True),(3,194,True)])
def test_delete_registration(user_id, event_id,output):
    assert db.delete_registration_from_database(user_id,event_id)==output
