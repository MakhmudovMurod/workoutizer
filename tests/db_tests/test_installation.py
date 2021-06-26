import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest
from packaging import version

from wkz import models
from workoutizer import __version__ as current_version
from workoutizer import settings as django_settings

workoutizer = "workoutizer"


def _add_wkz_bin(venv):
    wkz = Path(venv.bin) / "wkz"
    setattr(venv, "wkz", wkz)
    return venv


def _build_wheel() -> Path:
    # build wheel
    subprocess.check_call([sys.executable, "setup.py", "bdist_wheel"])
    # install wheel
    path_to_wheel = Path(django_settings.WORKOUTIZER_DIR) / "dist" / f"workoutizer-{current_version}-py3-none-any.whl"
    return path_to_wheel


@pytest.fixture
def venv_with_latest_pypi_wkz(venv):
    """Fixture to install latest workoutizer from PyPi"""
    os.environ["WKZ_ENV"] = "devel"
    venv.install(workoutizer, upgrade=True)
    venv = _add_wkz_bin(venv)
    yield venv


@pytest.fixture
def venv_with_current_wkz(venv):
    """Fixture to install current local development version of workoutizer"""
    path_to_wheel = _build_wheel()
    venv.install(str(path_to_wheel))
    # change dir to new home (in order to pick up correct django settings)
    new_wkz_home = list((Path(venv.path) / "lib").iterdir())[0] / "site-packages"
    os.chdir(new_wkz_home)
    # add wkz path as attribute to venv
    venv = _add_wkz_bin(venv)
    yield venv


@pytest.fixture
def venv_with_current_wkz__initialized(venv_with_current_wkz):
    """Fixture to install current local development version of workoutizer initialized"""
    subprocess.check_call([venv_with_current_wkz.wkz, "init"])
    yield venv_with_current_wkz


@pytest.fixture
def venv_with_current_wkz__initialized_demo(venv_with_current_wkz):
    """Fixture to install current local development version of workoutizer initialized with demo data"""
    subprocess.check_call([venv_with_current_wkz.wkz, "init", "--demo"])
    yield venv_with_current_wkz


def test_install_dev_version(venv_with_current_wkz__initialized):
    installed_version = str(venv_with_current_wkz__initialized.get_version(workoutizer))

    # check that the installed version equals the current version
    assert version.parse(current_version) == version.parse(installed_version)


def test_install_latest_pypi_version(venv_with_latest_pypi_wkz):
    latest_version_on_pypi = str(venv_with_latest_pypi_wkz.get_version(workoutizer))

    # check that the latest version from pypi is always smaller than or equal to the current version
    assert version.parse(current_version) >= version.parse(latest_version_on_pypi)


def test_upgrade_latest_pypi_to_dev(venv_with_latest_pypi_wkz, monkeypatch, db, capsys, client, caplog):
    wkz = venv_with_latest_pypi_wkz.wkz
    subprocess.check_call([wkz, "init"])
    subprocess.check_call([wkz, "check"])

    # get path to installed cli module
    lib_path = (
        Path(venv_with_latest_pypi_wkz.path)
        / "lib"
        / f"python{sys.version[:3]}"
        / "site-packages"
        / "workoutizer"
        / "cli.py"
    )
    spec = importlib.util.spec_from_file_location("cli.py", lib_path)
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)

    # running upgrade now would not upgrade wkz since the latest version from pypi is already installed
    cli._upgrade()
    captured = capsys.readouterr()
    assert "No update available. You are running the latest version:" in captured.out

    # mock 'get_version_pypi' and '_pip_install'
    dummy_version = "0.0.1"

    def mocked_get_version_pypi(pkg: str) -> str:
        print("mocking luddite get version pypi func")
        return dummy_version

    monkeypatch.setattr(cli.luddite, "get_version_pypi", mocked_get_version_pypi)

    def mocked_pip_install_func(pkg: str, upgrade: bool):
        print("installing local dev wheel instead of latest version from pypi")
        wheel = _build_wheel()
        subprocess.check_call([sys.executable, "-m", "pip", "install", wheel, "--force"])
        return "dummy-string"

    monkeypatch.setattr(cli, "_pip_install", mocked_pip_install_func)

    # upgrading now will upgrade the installed wkz version to the current local dev wheel
    cli._upgrade()

    captured = capsys.readouterr()
    assert f"Successfully upgraded from {current_version} to {dummy_version}" in captured.out

    # initialize wkz with demo activities
    cli._init(import_demo_activities=True)

    assert "finished inserting demo data" in caplog.text

    # a few sanity checks
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 19

    for activity in all_activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200
