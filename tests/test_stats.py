from datetime import datetime

from stats import Stats 


def test_add_and_count(data_file):
    s = Stats(data_file)
    assert s.count() == 0
    s.add_drink()
    assert s.add_drink() == 2


def test_persists_between_runs(data_file):
    Stats(data_file).add_drink()
    assert Stats(data_file).count() == 2


def test_persists_between_runs(data_file):
    Stats(data_file).add_drink()
    assert Stats(data_file).count() == 1


def test_days_are_seperate(data_file):
    s = Stats(data_file)
    s.add_drink(datetime(2026, 10, 17, 9, 0))
    s.add_drink(datetime(2026, 10, 18, 9, 0))
    assert s.count(datetime(2026, 10, 18)) == 1
    assert s.history() == {"2026-10-17": 1, "2026-10-18" : 1}

def test_undo_removes_last_drink(data_file):
    s = Stats(data_file)
    s.add_drink()
    s.add_drink()
    assert s.undo_drink() == 1
    assert Stats(data_file).count() == 1

def test_undo_with_nothing_logged(data_file):
    s = Stats(data_file)
    assert s.undo_drink() == 0


def test_undo_last_drink_removes_the_day(data_file):
    s = Stats(data_file)
    s.add_drink()
    s.undo_drink()
    assert s.history() == {}


def test_corrupt_file_is_kept_and_reset(data_file):
    data_file.write_text("{not json}")
    s = Stats(data_file)
    assert s.count() == 0
    assert data_file.with_suffix(".bad").exists()