from impersonic import __app_name__, __version__


def test_package_identity() -> None:
    assert __app_name__ == "Impersonic"
    assert __version__ == "0.1.0-dev"