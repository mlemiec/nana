"""Unit tests for nana.actions.writer"""
import pytest
from pathlib import Path
from unittest.mock import patch
from nana.actions.writer import finish_notes


@pytest.fixture
def tmp_vault(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "complete-note.md").write_text("# Complete Note\nThis note is finished.")
    (wiki / "incomplete-note.md").write_text("# Unpooling Layers\n#incomplete\nSome partial content.")
    return tmp_path


LOCALE = {}


def test_finishes_incomplete_notes(tmp_vault):
    with patch("nana.actions.writer.send_request_to_model", return_value="## Conclusion\nMore detail here."):
        finish_notes(tmp_vault, {}, LOCALE)
    content = (tmp_vault / "wiki" / "incomplete-note.md").read_text()
    assert "## Conclusion" in content
    assert "More detail here." in content


def test_removes_incomplete_tag(tmp_vault):
    with patch("nana.actions.writer.send_request_to_model", return_value="## Conclusion\nDone."):
        finish_notes(tmp_vault, {}, LOCALE)
    content = (tmp_vault / "wiki" / "incomplete-note.md").read_text()
    assert "#incomplete" not in content


def test_skips_complete_notes(tmp_vault):
    with patch("nana.actions.writer.send_request_to_model", return_value="## Conclusion\nDone.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE)
    assert mock_model.call_count == 1


def test_finish_specific_file_without_tag(tmp_vault):
    target = tmp_vault / "wiki" / "complete-note.md"
    with patch("nana.actions.writer.send_request_to_model", return_value="## Conclusion\nAdded.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE, target_path=target)
    mock_model.assert_called_once()
    assert "## Conclusion" in target.read_text()


def test_finish_specific_directory(tmp_vault):
    wiki = tmp_vault / "wiki"
    with patch("nana.actions.writer.send_request_to_model", return_value="## Conclusion\nDone."):
        finish_notes(tmp_vault, {}, LOCALE, target_path=wiki)
    assert "## Conclusion" in (wiki / "incomplete-note.md").read_text()


def test_passes_filename_to_model(tmp_vault):
    with patch("nana.actions.writer.send_request_to_model", return_value="Done.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE)
    user_prompt = mock_model.call_args.kwargs.get("user_prompt", "")
    assert "incomplete-note" in user_prompt
