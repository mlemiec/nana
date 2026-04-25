"""Unit tests for nana.actions.tagger"""
import pytest
from pathlib import Path
from nana.actions.tagger import assign_tag


@pytest.fixture
def tmp_vault(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "note1.md").write_text("# Note 1\nSome content here.")
    (raw / "note2.md").write_text("# Note 2\nAlready tagged.\n\n#incomplete")
    (raw / "note3.md").write_text("# Note 3\nAnother clean note.")
    return tmp_path


def test_assigns_tag_to_untagged_files(tmp_vault):
    raw = tmp_vault / "raw"
    assign_tag(raw, "#incomplete", {})
    assert "#incomplete" in (raw / "note1.md").read_text()
    assert "#incomplete" in (raw / "note3.md").read_text()


def test_skips_already_tagged_files(tmp_vault):
    raw = tmp_vault / "raw"
    assign_tag(raw, "#incomplete", {})
    assert (raw / "note2.md").read_text().count("#incomplete") == 1


def test_adds_hash_prefix_if_missing(tmp_vault):
    raw = tmp_vault / "raw"
    assign_tag(raw, "incomplete", {})
    assert "#incomplete" in (raw / "note1.md").read_text()


def test_handles_nonexistent_path(capsys):
    assign_tag(Path("/nonexistent/path"), "#incomplete", {})


def test_single_file_tagging(tmp_vault):
    note = tmp_vault / "raw" / "note1.md"
    assign_tag(note, "#incomplete", {})
    assert "#incomplete" in note.read_text()


def test_does_not_tag_non_md_files(tmp_vault):
    raw = tmp_vault / "raw"
    (raw / "image.png").write_bytes(b"\x89PNG")
    assign_tag(raw, "#incomplete", {})
    assert (raw / "image.png").read_bytes() == b"\x89PNG"
