import os
import json
import logging
from unittest.mock import MagicMock, patch
import pytest
from PyQt5.QtWidgets import QFileDialog
from common.profile_manager import ProfileManager, ProfileNotValid


@pytest.fixture
def mock_qfiledialog():
    with patch("common.profile_manager.QFileDialog") as mock:
        yield mock


@pytest.fixture
def mock_qmessagebox():
    with patch("common.profile_manager.QMessageBox") as mock:
        yield mock


def test_init():
    script_directory = "/path/to/scripts"
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    assert profile_manager.script_directory == script_directory
    assert profile_manager.version == version
    assert profile_manager.window is None
    assert profile_manager.profile_data is None
    assert profile_manager.settings == {
        "port_name": "",
        "channel": 0,
        "profile": "default.json",
        "icon": "icon.icns",
    }


def test_reload_window():
    script_directory = "/path/to/scripts"
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    window_mock = MagicMock()
    profile_manager.reload_window(window_mock)
    assert profile_manager.window == window_mock


def test_reload_profile_data():
    script_directory = "/path/to/scripts"
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    profile_data_mock = {"name": "Test Profile", "channel": 1, "buttons": []}
    profile_manager.reload_profile_data(profile_data_mock)
    assert profile_manager.profile_data == profile_data_mock


def test_ensure_directories_exist(tmpdir):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    profile_manager.ensure_directories_exist()
    profiles_directory = os.path.join(script_directory, "profiles")
    assert os.path.isdir(profiles_directory)


def test_load_profile_data(tmpdir):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    profile_name = "test_profile.json"
    profiles_directory = os.path.join(script_directory, "profiles")
    profile_path = os.path.join(profiles_directory, profile_name)

    os.makedirs(profiles_directory, exist_ok=True)

    test_profile_data = {"name": "Test Profile", "channel": 1, "buttons": []}
    with open(profile_path, "w") as profile_file:
        json.dump(test_profile_data, profile_file)

    loaded_profile_data = profile_manager.load_profile_data(profile_name)

    assert loaded_profile_data == test_profile_data


def test_load_profile_data_nonexistent(tmpdir, caplog):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    profile_name = "nonexistent_profile.json"
    with caplog.at_level(logging.WARNING):
        loaded_profile_data = profile_manager.load_profile_data(profile_name)
        assert "Profile file not found" in caplog.text
        assert loaded_profile_data == {
            "name": "New Profile",
            "channel": 0,
            "buttons": [],
        }


def test_load_profile_data_invalid(tmpdir, caplog):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    profile_name = "invalid_profile.json"
    profiles_directory = os.path.join(script_directory, "profiles")
    profile_path = os.path.join(profiles_directory, profile_name)

    os.makedirs(profiles_directory, exist_ok=True)

    with open(profile_path, "w") as profile_file:
        profile_file.write("invalid_json")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ProfileNotValid):
            profile_manager.load_profile_data(profile_name)


def test_load_settings(tmpdir):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    settings_filename = "settings.json"
    settings_path = os.path.join(script_directory, settings_filename)

    test_settings = {
        "port_name": "/dev/ttyUSB0",
        "channel": 1,
        "profile": "custom.json",
        "icon": "custom_icon.icns",
    }
    with open(settings_path, "w") as settings_file:
        json.dump(test_settings, settings_file)

    loaded_settings = profile_manager.load_settings(settings_filename)
    assert loaded_settings == test_settings


def test_load_settings_nonexistent(tmpdir, caplog):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    settings_filename = "nonexistent_settings.json"
    with caplog.at_level(logging.WARNING):
        loaded_settings = profile_manager.load_settings(settings_filename)
        assert "Settings file not found" in caplog.text
        assert loaded_settings == {
            "port_name": "",
            "channel": 0,
            "profile": "default.json",
            "icon": "icon.icns",
        }


def test_load_settings_invalid(tmpdir, caplog):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)

    settings_filename = "invalid_settings.json"
    settings_path = os.path.join(script_directory, settings_filename)

    with open(settings_path, "w") as settings_file:
        settings_file.write("invalid_json")

    with caplog.at_level(logging.ERROR):
        loaded_settings = profile_manager.load_settings(settings_filename)
        assert "Error loading settings" in caplog.text
        assert loaded_settings == {
            "port_name": "",
            "channel": 0,
            "profile": "default.json",
            "icon": "icon.icns",
        }


def test_change_profile_dialog_accepted(mock_qfiledialog, tmpdir):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    profile_manager.window = MagicMock()

    initial_profile_data = {}

    with patch.object(
        profile_manager, "load_profile_data", return_value=initial_profile_data
    ):
        selected_file = os.path.join(script_directory, "profiles", "test_profile.json")
        profile_data = profile_manager.change_profile(selected_file)

    assert profile_data == initial_profile_data
    assert profile_manager.settings["profile"] == "test_profile.json"
    assert profile_manager.profile_data == initial_profile_data


def test_change_profile_dialog_canceled(mock_qfiledialog, tmpdir):
    script_directory = str(tmpdir)
    version = "1.0"
    profile_manager = ProfileManager(script_directory, version)
    profile_manager.window = MagicMock()

    mock_qfiledialog_instance = mock_qfiledialog.return_value
    mock_qfiledialog_instance.exec_.return_value = QFileDialog.Rejected

    profile_manager.change_profile()

    assert profile_manager.settings["profile"] == "default.json"
    assert profile_manager.profile_data is None
    profile_manager.window.update_status_bar.assert_called_once_with(
        "No profile selected"
    )
