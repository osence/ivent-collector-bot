import db

def test_get_events():
    example=db.get_events_from_database()
    assert False!=example

def test_get_user():
    assert db.get_user_info_from_database(3)!=False

def test_get_user2():
    assert db.get_user_info_from_database(103)==None

def test_get_event_info():
    assert db.get_event_info_from_database(14)!=False

def test_get_event_info2():
    assert db.get_event_info_from_database(140)==None

def test_get_events_in_user_plans():
    check=db.get_events_in_user_plans_from_database(3)
    co=len(check)
    assert co >-1

def test_get_events_in_user_plans2():
    assert db.get_events_in_user_plans_from_database(23)==[]

def test_get_events_of_users():
    check=db.get_events_of_user_from_database(3)
    co=len(check)
    assert co >-1

def test_get_events_of_users2():
    assert db.get_events_of_user_from_database(23)==[]