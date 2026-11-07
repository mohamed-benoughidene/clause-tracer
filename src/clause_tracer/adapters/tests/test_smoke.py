from clause_tracer.adapters.__main__ import main


def test_main_returns_zero() -> None:
    assert main() == 0
