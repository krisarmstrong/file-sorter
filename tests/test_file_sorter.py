#!/usr/bin/env python3
"""
Tests for FileSorter.
"""
import os
import pytest
from file_sorter import __version__, organize_files
from pathlib import Path

@pytest.fixture
def tmp_dir(tmp_path):
    """Create temporary source and target directories."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    return source, target

def test_version() -> None:
    """Test version format."""
    assert __version__ == "1.0.1"

def test_organize_mime_mode(tmp_dir) -> None:
    """Test MIME-type sorting."""
    source, target = tmp_dir
    with open(source / "test.jpg", "w") as f:
        f.write("fake image")
    with open(source / "test.pdf", "w") as f:
        f.write("fake pdf")

    organize_files(str(source), str(target), "mime", False)

    assert os.path.exists(target / "Images" / "test.jpg")
    assert os.path.exists(target / "PDF" / "test.pdf")
    assert not os.path.exists(source / "test.jpg")
    assert not os.path.exists(source / "test.pdf")

def test_organize_extension_mode(tmp_dir) -> None:
    """Test extension-based sorting with renaming."""
    source, target = tmp_dir
    with open(source / "test.txt", "w") as f:
        f.write("fake text")
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m")

    organize_files(str(source), str(target), "extension", True)

    assert os.path.exists(target / "txt" / f"{timestamp}-test.txt")
    assert not os.path.exists(source / "test.txt")