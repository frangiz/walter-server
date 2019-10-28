import pytest

import scripts.check_status


def test_all_active_not_sending_email(mocker):
    # arrange
    def mocked_get_sensors():
        return [{"is_active": True, "name": "my-sensor-1"}]

    mocker.patch("scripts.check_status.get_sensors", mocked_get_sensors)
    mocker.patch("scripts.check_status.create_msg")
    mocker.patch("scripts.check_status.send_email")

    # act
    scripts.check_status.check_status({})

    # assert
    scripts.check_status.create_msg.assert_not_called()
    scripts.check_status.send_email.assert_not_called()


def test_one_not_active_trying_to_send_email(mocker):
    # arrange
    def mocked_get_sensors():
        return [
            {"is_active": False, "name": "my-sensor-1"},
            {"is_active": True, "name": "my-sensor-2"},
        ]

    mocker.patch("scripts.check_status.get_sensors", mocked_get_sensors)
    mocker.patch("scripts.check_status.create_msg")
    mocker.patch("scripts.check_status.send_email")

    # act
    scripts.check_status.check_status({})

    # assert
    scripts.check_status.create_msg.assert_called_once_with(["my-sensor-1"])
    # scripts.check_status.send_email.assert_called_once()
