"""Architecture tests for the core module (T9, T1, B3)."""

import dataclasses
import enum
import subprocess
import sys


def _exported_classes() -> list[type]:
    import clause_tracer.core

    classes: list[type] = []
    for name in clause_tracer.core.__all__:
        obj = getattr(clause_tracer.core, name)
        if isinstance(obj, type) and dataclasses.is_dataclass(obj):
            classes.append(obj)
    return classes


def _exported_enums() -> list[type]:
    import clause_tracer.core

    found: list[type] = []
    for name in clause_tracer.core.__all__:
        obj = getattr(clause_tracer.core, name)
        if isinstance(obj, type) and issubclass(obj, enum.Enum):
            found.append(obj)
    return found


def test_import_core_loads_only_stdlib() -> None:
    # The plan's wording compared against sys.stdlib_module_names alone, but
    # the interpreter loads its own startup modules first (on this OS,
    # /usr/lib/python3*/sitecustomize.py, the apport hook). The owner chose
    # the baseline comparison: importing core may add only clause_tracer
    # names and stdlib names, measured against a run that does not import
    # core. Change recorded in the plan's change log, 16 Nov 2026.
    plain = subprocess.run(
        (sys.executable, "-c", "import sys; print('\\n'.join(sorted(sys.modules)))"),
        check=True,
        capture_output=True,
        text=True,
    )
    with_core = subprocess.run(
        (
            sys.executable,
            "-c",
            "import sys, clause_tracer.core; print('\\n'.join(sorted(sys.modules)))",
        ),
        check=True,
        capture_output=True,
        text=True,
    )
    baseline = {m.split(".", 1)[0] for m in plain.stdout.split()}
    loaded = {m.split(".", 1)[0] for m in with_core.stdout.split()}
    added = loaded - baseline
    for top in added:
        assert top == "clause_tracer" or top in sys.stdlib_module_names, (
            f"importing clause_tracer.core loaded non-stdlib module {top}"
        )


def test_public_dataclasses_are_frozen_slotted_keyword_only() -> None:
    for shape in _exported_classes():
        params = shape.__dataclass_params__  # type: ignore[attr-defined]
        assert params.frozen, f"{shape.__name__} is not frozen"
        assert "__slots__" in shape.__dict__, f"{shape.__name__} has no slots"
        for field in dataclasses.fields(shape):
            assert field.kw_only, f"{shape.__name__}.{field.name} is not keyword-only"


def test_no_mutable_container_fields() -> None:
    for shape in _exported_classes():
        for field in dataclasses.fields(shape):
            hint = str(field.type)
            for bad in ("list[", "dict[", "set["):
                assert bad not in hint, f"{shape.__name__}.{field.name} is {hint}"


def test_no_provider_specific_field_names() -> None:
    forbidden = (
        "openrouter",
        "zdr",
        "data_collection",
        "require_parameters",
        "response_format",
        "provider_order",
        "usage_cost",
        "anthropic",
        "openai",
    )
    for shape in _exported_classes():
        for field in dataclasses.fields(shape):
            for word in forbidden:
                assert word not in field.name, (
                    f"{shape.__name__}.{field.name} names the provider setting {word}"
                )


def test_enums_are_str_enums() -> None:
    for members in _exported_enums():
        assert issubclass(members, enum.StrEnum), f"{members.__name__} is not a StrEnum"
        for member in members:
            assert member.value == member.name.lower(), (
                f"{members.__name__}.{member.name} has value {member.value!r}"
            )
