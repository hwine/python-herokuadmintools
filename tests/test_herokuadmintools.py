import pytest

from herokuadmintools.cli import main
import herokuadmintools


@pytest.fixture(autouse=True)
def reset_status_code_before_each_test():
    herokuadmintools.status_code = 0


def test_main_help():
    with pytest.raises(SystemExit) as e_info:
        main(["-h"])
    assert e_info.value.code == 0


def test_main_bad_args():
    with pytest.raises(SystemExit) as e_info:
        main(["-xxxx"])
    # argparse exits with 2 on bad args
    assert e_info.value.code == 2


def test_pass_bad_org():
    with pytest.raises(SystemExit) as e_info:
        main("--organization fred".split())
    assert e_info.value.code == 3


def test_pass_no_org():
    with pytest.raises(SystemExit) as e_info:
        main("".split())
    # now passes, as we have a default org
    assert e_info.value.code in [0, 2]
