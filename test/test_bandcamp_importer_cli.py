import pytest

from bandcamp_importer import cli


@pytest.mark.xfail
def test_tests_are_implemented():
    assert cli.main()
