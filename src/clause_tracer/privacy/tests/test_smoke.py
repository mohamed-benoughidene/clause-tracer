from clause_tracer.privacy.__main__ import main


def test_main_returns_zero() -> None:
    assert main() == 0
