import pytest

from herokuadmintools.cli import main


def test_main_help():
    with pytest.raises(SystemExit) as e_info:
        main(["-h"])
    assert e_info.value.code == 0


def test_main_bad_args():
    with pytest.raises(SystemExit) as e_info:
        main(["-xxxx"])
    # argparse exits with 2 on bad args
    assert e_info.value.code == 2
