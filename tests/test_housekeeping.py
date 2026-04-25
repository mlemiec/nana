"""Unit tests for nana.actions.housekeeping"""
import pytest
from pathlib import Path
from unittest.mock import patch
from nana.actions.housekeeping import tidy_vault


@pytest.fixture
def tmp_vault(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "Untitled_1.md").write_text("This note is about machine learning basics.")
    (raw / "web-clip-123.md").write_text("# Article about Python\nPython is great.")
    (raw / "clean-note.md").write_text("# Clean Note\nThis is already well named.")
    return tmp_path


LOCALE = {
    "cleaning_start": "Looking...",
    "no_mess": "All clean!",
    "cleaning_rename": "Renamed {old_name} to {new_name}",
    "cleaning_done": "Done!",
}


def test_only_renames_messy_files(tmp_vault):
    with patch("nana.actions.housekeeping.send_request_to_model", return_value="machine_learning_basics"):
        tidy_vault(tmp_vault, {}, LOCALE)
    assert (tmp_vault / "raw" / "clean-note.md").exists()


def test_renames_untitled_files(tmp_vault):
    with patch("nana.actions.housekeeping.send_request_to_model", return_value="machine_learning_basics"):
        tidy_vault(tmp_vault, {}, LOCALE)
    assert not (tmp_vault / "raw" / "Untitled_1.md").exists()
    assert (tmp_vault / "raw" / "machine_learning_basics.md").exists()


def test_renames_web_clip_files(tmp_vault):
    with patch("nana.actions.housekeeping.send_request_to_model", return_value="python_intro"):
        tidy_vault(tmp_vault, {}, LOCALE)
    assert not (tmp_vault / "raw" / "web-clip-123.md").exists()
    assert (tmp_vault / "raw" / "python_intro.md").exists()


def test_no_mess_returns_early(tmp_vault):
    raw = tmp_vault / "raw"
    (raw / "Untitled_1.md").unlink()
    (raw / "web-clip-123.md").unlink()
    with patch("nana.actions.housekeeping.send_request_to_model") as mock_model:
        tidy_vault(tmp_vault, {}, LOCALE)
        mock_model.assert_not_called()


def test_uses_custom_target_dir(tmp_path):
    custom = tmp_path / "custom"
    custom.mkdir()
    (custom / "Untitled.md").write_text("Content")
    with patch("nana.actions.housekeeping.send_request_to_model", return_value="new_name"):
        tidy_vault(tmp_path, {}, LOCALE, target_dir=custom)
    assert (custom / "new_name.md").exists()
