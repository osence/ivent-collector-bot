import db
import pytest

@pytest.mark.parametrize("event_id, name, description, date, time, place,\
        theme, pay, seats, user_id, output",[
        #1 
        (60,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00','61.786153,34.352475','творчество',0,50,3,True),
        #2
        (50,None,'Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00','61.786153,34.352475','творчество',0,50,3,False),
        #3
        (62,'Вечер поэзии','Встреча поэтов города Петрозаводск','12.:0.r3',\
        '20:00','61.786153,34.352475','творчество',0,50,3,False),
        #4
        (63,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '12:0r3','61.786153,34.352475','творчество',0,50,3,False),
        #5
        (64,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00',None,'творчество',0,50,3,False),
        #6
        # (65,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        # '20:00','61.786153,34.352475',None,0,50,3,False),
        #7
        (66,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00','61.786153,34.352475','творчество','123ttt3',50,3,False),
        #8
        (67,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00','61.786153,34.352475','творчество',0,'123ttt3',3,False),
        #9
        (57,'Вечер поэзии','Встреча поэтов города Петрозаводск','08.11.2021',\
        '20:00','61.786153,34.352475','творчество',0,50,133,False)])         
def test_edit_event(event_id, name, description, date, time, place,theme, pay, seats, user_id, output):
    assert db.edit_event_info_in_database(event_id, name, description, date, time, place,\
        theme, pay, seats, user_id)==output


@pytest.mark.parametrize('id, output',[(3,True),(103,True)])
def test_delete_event(id,output):
    assert db.delete_event_from_database(id)==output

@pytest.mark.parametrize('id, output',[(3,True),(103,False)])
def test_id_in(id,output):
    assert db.id_in_database(id)==output