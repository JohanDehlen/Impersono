from __future__ import annotations

import impersonic.__main__ as cli


def test_default_command_preserves_existing_identity_output(
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli.platform, "python_version", lambda: "3.12.10")
    monkeypatch.setattr(cli.platform, "platform", lambda: "Windows-Test")
    monkeypatch.setattr(cli.sys, "executable", r"C:\Test\python.exe")

    result = cli.main([])

    output = capsys.readouterr().out
    assert result == 0
    assert "Impersonic 0.1.0-dev" in output
    assert "Professional Local AI Voice Creation" in output
    assert "Python: 3.12.10" in output
    assert r"Executable: C:\Test\python.exe" in output
    assert "Platform: Windows-Test" in output


def test_hardware_command_uses_hardware_report(capsys, monkeypatch) -> None:
    sentinel = object()

    monkeypatch.setattr(cli, "detect_hardware", lambda: sentinel)
    monkeypatch.setattr(
        cli,
        "format_hardware_report",
        lambda info: "TEST HARDWARE REPORT" if info is sentinel else "wrong",
    )

    result = cli.main(["--hardware"])

    assert result == 0
    assert capsys.readouterr().out.strip() == "TEST HARDWARE REPORT"


def test_compatibility_command_uses_detected_hardware(capsys, monkeypatch) -> None:
    hardware = object()
    assessment = object()

    monkeypatch.setattr(cli, "detect_hardware", lambda: hardware)
    monkeypatch.setattr(
        cli,
        "assess_vibevoice_1_5b",
        lambda info: assessment if info is hardware else None,
    )
    monkeypatch.setattr(
        cli,
        "format_model_compatibility",
        lambda value: "TEST COMPATIBILITY REPORT" if value is assessment else "wrong",
    )

    result = cli.main(["--compatibility"])

    assert result == 0
    assert capsys.readouterr().out.strip() == "TEST COMPATIBILITY REPORT"


def test_hardware_and_compatibility_are_mutually_exclusive() -> None:
    parser = cli._build_parser()

    try:
        parser.parse_args(["--hardware", "--compatibility"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected argparse to reject mutually exclusive options.")
