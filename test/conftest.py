import os

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def fixtures():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def media_root(tmp_path_factory):
    return tmp_path_factory.mktemp('media')


@pytest.fixture
def main_args(media_root, fixtures):
    return {
        'verbose': True,
        'log_level': 'DEBUG',
        'media_root': media_root,
        'downloads': fixtures / "downloads",
        'config_file': fixtures / 'bandcamp-importer.conf',
    }


@pytest.fixture(autouse=True)
def mock_env(monkeypatch, fixtures, media_root):
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']
