import json

import config
import settings

def use_temp_file(monkeypatch, tmp_path):
    file = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "path", lambda: file)
    monkeypatch.setattr(config, "GOAL", 8)
    monkeypatch.setattr(config, "DEFAULT_MINUTES", 45)
    monkeypatch.setattr(config, "SNOOZE_MINUTES", 5)
    return file

def test_update_changes_config_and_saves(monkeypatch, tmp_path):
    file = use_temp_file(monkeypatch, tmp_path)
    settings.update({"GOAL" : 5})
    assert config.GOAL == 5
    assert json.loads(file.read_text())["GOAL"] == 5


def test_load_applies_saved_values(monkeypatch, tmp_path):
    file = use_temp_file(monkeypatch, tmp_path)
    file.write_text(json.dumps({"GOAL": 6, "DEFAULT_MINUTES": 30}))
    settings.load()
    assert config.GOAL == 6
    assert config.DEFAULT_MINUTES == 30
    assert config.SNOOZE_MINUTES == 5


def test_load_ignores_out_of_range_values(monkeypatch, tmp_path):
    file = use_temp_file(monkeypatch, tmp_path)
    file.write_text(json.dumps({"GOAL": 999, "SNOOZE_MINUTES" : 0}))
    settings.load()
    assert config.GOAL == 8
    assert config.SNOOZE_MINUTES == 5


def test_load_survives_a_broken_file(monkeypatch, tmp_path):
    file = use_temp_file(monkeypatch, tmp_path)
    file.write_text("{nope")
    settings.load()
    assert config.GOAL == 8
