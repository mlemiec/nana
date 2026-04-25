"""Unit tests for src/actions/writer.py"""
import pytest
from pathlib import Path
from unittest.mock import patch
from actions.writer import finish_notes


@pytest.fixture
def tmp_vault(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "complete-note.md").write_text("# Complete Note\nThis note is finished.")
    (wiki / "incomplete-note.md").write_text("# Unpooling Layers\n#incomplete\nSome partial content.")
    return tmp_path


LOCALE = {}


def test_finishes_incomplete_notes(tmp_vault):
    """Should append content to notes tagged #incomplete."""
    with patch("actions.writer.send_request_to_model", return_value="## Conclusion\nMore detail here."):
        finish_notes(tmp_vault, {}, LOCALE)

    content = (tmp_vault / "wiki" / "incomplete-note.md").read_text()
    assert "## Conclusion" in content
    assert "More detail here." in content


def test_removes_incomplete_tag(tmp_vault):
    """The #incomplete tag should be removed after finishing."""
    with patch("actions.writer.send_request_to_model", return_value="## Conclusion\nDone."):
        finish_notes(tmp_vault, {}, LOCALE)

    content = (tmp_vault / "wiki" / "incomplete-note.md").read_text()
    assert "#incomplete" not in content


def test_skips_complete_notes(tmp_vault):
    """Should not touch notes without the #incomplete tag."""
    with patch("actions.writer.send_request_to_model", return_value="## Conclusion\nDone.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE)

    # Model should only be called once (for the incomplete note)
    assert mock_model.call_count == 1


def test_finish_specific_file_without_tag(tmp_vault):
    """When a specific file path is given, finish it even without the tag."""
    target = tmp_vault / "wiki" / "complete-note.md"
    with patch("actions.writer.send_request_to_model", return_value="## Conclusion\nAdded.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE, target_path=target)

    mock_model.assert_called_once()
    content = target.read_text()
    assert "## Conclusion" in content


def test_finish_specific_directory(tmp_vault):
    """When a directory is given, scan recursively for #incomplete."""
    wiki = tmp_vault / "wiki"
    with patch("actions.writer.send_request_to_model", return_value="## Conclusion\nDone."):
        finish_notes(tmp_vault, {}, LOCALE, target_path=wiki)

    content = (wiki / "incomplete-note.md").read_text()
    assert "## Conclusion" in content


def test_passes_filename_to_model(tmp_vault):
    """Model should receive the filename so it knows the real topic."""
    with patch("actions.writer.send_request_to_model", return_value="Done.") as mock_model:
        finish_notes(tmp_vault, {}, LOCALE)

    call_kwargs = mock_model.call_args
    user_prompt = call_kwargs.kwargs.get("user_prompt", "")
    assert "incomplete-note" in user_prompt
