import pytest
import datetime
import pandas as pd
from chatbot import Chatbot

d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame(data=d)
print(df)
print(df['col2'].sum(axis=0, skipna=True))


# @pytest.mark.run_these_please
def test_passing():
    assert (1, 2, 3) == (1, 2, 3)


# Dates to fixtures
# https://stackoverflow.com/questions/20503373/how-to-monkeypatch-pythons-datetime-datetime-now-with-py-test

@pytest.mark.xfail()
def test_failing():
    assert (1, 2, 3) == (3, 2, 1)


def test_df_value():
    assert df.iloc[0]['col1'] == 1


def test_df():
    assert df['col2'].sum(axis=0, skipna=True) == 7


@pytest.mark.xfail()
def test_df_fail():
    assert df['col2'].sum(axis=0, skipna=True) == 8


FAKE_MONDAY = datetime.datetime(2021, 2, 8, 17, 5, 55)
FAKE_TUESDAY = datetime.datetime(2021, 2, 9, 17, 5, 55)


@pytest.fixture
def patch_datetime_monday(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_MONDAY

    monkeypatch.setattr(datetime, 'datetime', mydatetime)


def test_patch_datetime(patch_datetime_monday):
    assert datetime.datetime.now() == FAKE_MONDAY

# @pytest.fixture
# def monday():
#     return datetime.datetime.today().weekday() == 0
#
#
# @pytest.fixture
# def tuesday():
#     return datetime.datetime.today().weekday() == 1


# @pytest.mark.run_these_please
# def test_chatbot_at_monday(patch_datetime_monday):
#
#     Cb = Chatbot()
#     range_name, text_to_send = Cb.today_metric()
#     assert range_name == 'Dashboard!I42:I42'
#
#
# def test_chatbot_2(patch_datetime_monday):
#     assert datetime.now() == datetime.datetime(2021, 2, 8, 17, 5, 55)

# def test_chatbot_at_tuesday(tuesday):
#     Cb = Chatbot()
#     range_name, text_to_send = Cb.today_metric()
#     assert range_name == 'Dashboard!I46:I46'


# marker pytest.mark.run_these_please require import pytest
# pytest -v test/test_one.py::test_passing
# pytest -v -m run_these_please
