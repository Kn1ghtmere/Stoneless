from datetime import date, datetime, timedelta

import settings
import stats
from config import GOAL



def seed(days_ago, count):
    when = datetime.combine(date.today() -timedelta(days=days_ago), datetime.min.time())
    with stats.connect() as db:
        for i in range(count):
            db.execute("INSERT INTO drinks (amount_ml, logged_at) VALUES (250, ?)",
                       ((when + timedelta(hours=8 + i )).isoformat(),))



def test_log_and_count():
    assert stats.today_count() == 0
    stats.log_drink()
    stats.log_drink()
    assert stats.today_count() == 2 

def test_streak_counts_consecutive_goal_days():
    seed(1, GOAL)
    seed(2, GOAL)
    seed(3, GOAL - 1)
    assert stats.current_streak() ==2

def test_today_does_not_break_until_done():
    seed(1, GOAL)
    assert stats.current_streak() == 2
    seed(0, GOAL)
    assert stats.current_streak() == 2\


def test_daily_counts_is_zero_filled():
    seed(0,3)
    data = stats.daily_counts(7)
    assert len(data) == 7 and data[-1][1] ==3 and data[0][1] == 0


def test_sync_marking():
    stats.log_drink()
    rows = stats.unsynced()
    assert len(rows) == 1
    stats.mark_synced([r["id"] for r in rows])
    assert stats.unsynced() ==[]

def test_settings_roundtrip():
    settings.update(interval_minutes=30)
    assert settings.load()["interval_minutes"] ==30