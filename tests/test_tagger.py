"""Unit tests for src/actions/tagger.py"""
import pytest
from pathlib import Path
from actions.tagger import assign_tag


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault directory with some markdown files."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "note1.md").write_text("# Note 1\nSome content here.")
    (raw / "note2.md").write_text("# Note 2\nAlready tagged.\n\n#incomplete")
    (raw / "note3.md").write_text("# Note 3\nAnother clean note.")
    return tmp_path


def test_assigns_tag_to_untagged_files(tmp_vault):
    """Tag should be added to files that don't have it."""
    raw = tmp_vault / "raw"
    assign_tag(raw, "#incomplete", {})

    assert "#incomplete" in (raw / "note1.md").read_text()
    assert "#incomplete" in (raw / "note3.md").read_text()


def test_skips_already_tagged_files(tmp_vault):
    """Tag should not be duplicated on files that already have it."""
    raw = tmp_vault / "raw"
    assign_tag(raw, "#incomplete", {})
    content = (raw / "note2.md").read_text()

    assert content.count("#incomplete") == 1


def test_adds_hash_prefix_if_missing(tmp_vault):
    """Passing 'incomplete' (no #) should still add '#incomplete'."""
    raw = tmp_vault / "raw"
    assign_tag(raw, "incomplete", {})

    assert "#incomplete" in (raw / "note1.md").read_text()


def test_handles_nonexistent_path(capsys):
    """Should not crash on a nonexistent path."""
    assign_tag(Path("/nonexistent/path"), "#incomplete", {})
    # Should complete without raising an exception


def test_single_file_tagging(tmp_vault):
    """Should work on a single file, not just directories."""
    note = tmp_vault / "raw" / "note1.md"
    assign_tag(note, "#incomplete", {})

    assert "#incomplete" in note.read_text()


def test_does_not_tag_non_md_files(tmp_vault):
    """Should only tag .md files."""
    raw = tmp_vault / "raw"
    (raw / "image.png").write_bytes(b"\x89PNG")
    assign_tag(raw, "#incomplete", {})

    # The PNG file should not be touched
    assert (raw / "image.png").read_bytes() == b"\x89PNG"
