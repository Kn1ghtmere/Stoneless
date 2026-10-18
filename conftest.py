import pytest 

class FakeClock:
    def __init__(self, t=1000.0):
        self.t = t


    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def data_file(tmp_path):
    return tmp_path / "data.json"