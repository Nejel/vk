import datetime
import pytest

FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)

@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'datetime', mydatetime)


def test_patch_datetime(patch_datetime_now):
    assert datetime.datetime.now() == FAKE_TIME