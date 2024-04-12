import os

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer

from bandcamp_importer import cli


@pytest.fixture
def context():
    return MagicMock(spec=typer.Context, args=[], invoked_subcommand=None)


@pytest.mark.parametrize("files, downloads, expected", [
    ([], None, [
        "artist",
        "artist/album",
        "artist/album/one.mp3",
        "artist/album/two.m4a",
        "artist/album/cover.jpg",
    ]),
    (["invalid_filename.zip"], None, []),
    (["does_not_exist.zip"], None, []),
    (["invalid - zipfile_format.zip"], None, []),
])
def test_import_album(context, main_args, media_root, fixtures, files, downloads, expected):
    context.configure_mock(args=[fixtures / filename for filename in files])
    cli.main(context, **main_args)
    results = sorted([str(Path(p).relative_to(media_root)) for p in media_root.rglob("*")])
    assert results == sorted(expected)


def test_imports_are_idempotent(context, main_args, media_root, fixtures):
    cli.main(context, **main_args)
    cover = media_root / 'artist' / 'album' / 'cover.jpg'
    mtime = cover.stat().st_mtime
    cli.main(context, **main_args)
    assert cover.stat().st_mtime == mtime


def test_main(context, main_args):
    context.configure_mock(invoked_subcommand=None)
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']
    cli.main(context, **main_args)
    assert cli.app_state['verbose'] is True
    assert os.environ['LOG_LEVEL'] == 'INFO'
