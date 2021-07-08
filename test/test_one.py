import pytest
from vk.chatbot import today_metric

def test_failing():
    assert (1, 2, 3) == (3, 2, 1)

# @pytest.fixture
# def first_entry():
#     return datetime.datetime.today().weekday() == 1

@pytest.mark.run_these_please
def test_passing():
    assert (1, 2, 3) == (1, 2, 3)

@pytest.mark.run_these_please
def test_chatbot():
    from chatbot import today_metric
    range_name, text_to_send = today_metric
    assert range_name == 'Dashboard!I46:I46'

# marker pytest.mark.run_these_please require import pytest
# pytest -v test/test_one.py::test_passing
# pytest -v -m run_these_please