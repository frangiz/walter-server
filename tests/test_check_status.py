import json
import os
import pytest
import requests_mock

import scripts.check_status


def setup_function(function):
    pass


def teardown_function(function):
    state_file_path = os.path.join("scripts", "check_status_state.json")
    if os.path.exists(state_file_path):
        os.remove(state_file_path)


@pytest.mark.parametrize(
    "new_state, old_state, result",
    [
        ({"s1": True}, {}, []),
        ({"s1": True}, {"s1": False}, ["s1"]),
        ({"s1": False}, {}, []),
        ({"s1": False}, {"s1": True}, []),
    ],
)
def test_get_activated(new_state, old_state, result):
    assert scripts.check_status.get_activated(new_state, old_state) == result


@pytest.mark.parametrize(
    "new_state, old_state, result",
    [
        ({"s1": True}, {}, []),
        ({"s1": True}, {"s1": False}, []),
        ({"s1": False}, {}, []),
        ({"s1": False}, {"s1": True}, ["s1"]),
    ],
)
def test_get_deactivated(new_state, old_state, result):
    assert scripts.check_status.get_deactivated(new_state, old_state) == result


def test_saving_state():
    assert scripts.check_status.get_last_known_state() == {}
    new_state = {"s1": True, "s2": False, "s3": True}
    scripts.check_status.save_state(new_state)
    assert new_state == scripts.check_status.get_last_known_state()


def test_get_last_known_state_with_empty_file():
    state_file_path = os.path.join("scripts", "check_status_state.json")
    with open(state_file_path, "w") as f:
        f.write("")

    assert {} == scripts.check_status.get_last_known_state()


def test_get_current_state(mocker):
    with requests_mock.Mocker() as m:
        mocked_response = [
            {"name": "s1", "is_active": False},
            {"name": "s2", "is_active": True},
        ]
        m.get("http://localhost:5000/api/sensors", text=json.dumps(mocked_response))
        assert {"s1": False, "s2": True} == scripts.check_status.get_current_state()


def test_create_msg_with_empty_lists():
    """ Basically check that the method does not crash."""
    assert scripts.check_status.create_msg([], []) is not None


def test_create_msg_with_populated_lists():
    msg = scripts.check_status.create_msg(
        ["activated-sensor-1"], ["deactivated-sensor-2"]
    )
    assert "activated-sensor-1" in msg
    assert "deactivated-sensor-2" in msg
