from reminder import Reminder


def test_not_due_until_interval(clock):
    r = Reminder(60, 10, clock)
    clock.advance(59)
    assert not r.is_due()
    clock.advance(1)
    assert r.is_due()


def test_reset_restarts_full_interval(clock):
    r = Reminder(60, 10, clock)
    clock.advance(61)
    r.reset()
    assert not r.is_due()
    assert r.remaining() == 60

def test_snooze_uses_short_delay(clock):
    r = Reminder(60, 10, clock)
    clock.advance(61)
    r.snooze()
    assert r.remaining() == 10

def test_overdue_after_sleep(clock):
    r = Reminder(60, 10, clock)
    clock.advance(10_000)
    assert r.is_due() and r.remaining() == 0