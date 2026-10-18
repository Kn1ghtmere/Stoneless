import pytest
import settings
import stats



@pytest.fixture(autouse=True)




def isolated_data(tmp_path, monkeypatch):

    monkeypatch.setattr(stats, "DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr(settings, "SETTING_PATH", str(tmp_path / "settings.json"))
    stats.init_db()