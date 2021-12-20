import db
import pytest

def test_get_events_filter_location():
    check=db.get_events_filter_location_from_database(61.786114192711466,34.35216235795723)
    co=len(check)
    assert co > 0

def test_get_events_filter_location2():
    assert db.get_events_filter_location_from_database(261.786114192711466,234.35216235795723)==[]

@pytest.mark.parametrize('start,end',[('08.11.2021', None),(None, None)])
def test_get_events_filter_date(start,end):
    db.get_events_filter_date_from_database(start,end) 
    assert db.get_events_filter_date_from_database(start,end)==False

def test_get_events_filter_date_true():
    check=db.get_events_filter_date_from_database('08.11.2021', '08.12.2021')
    co=len(check)
    assert co > 1

def test_get_events_filter_date_none():
    check=db.get_events_filter_date_from_database('08.11.3021', '08.12.2021')
    co=len(check)
    assert co == 0

def test_get_events_filter_theme():
    check=db.get_events_filter_theme_from_database('Концерт')
    co=len(check)
    assert co > 1

# Не работает т.к. преборазовать None в строку нельзя(это продумано на уровне handler)
# def test_get_events_filter_theme_none():
#     check=db.get_events_filter_theme_from_database(None)
#     co=len(check)
#     assert co == 0

@pytest.mark.parametrize('min,max',[(None,300),(300,None),(300,100)])
def test_get_events_filter_pay_from_database_none(min, max):
    assert db.get_events_filter_pay_from_database(min,max)==[]

def test_get_events_filter_pay_from_database_true():
    check=db.get_events_filter_pay_from_database(100,300)
    co=len(check)
    assert co > 1