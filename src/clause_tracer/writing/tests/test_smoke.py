from clause_tracer.writing.__main__ import main


def test_main_returns_zero() -> None:
    assert main() == 0
