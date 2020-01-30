import pytest

from datetime import datetime
from time import time

from app import create_app
from app import db
from app.models import Sensor
from config import Config
from flask import url_for


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


def setup_function(function):
    db.create_all()


def teardown_function(function):
    db.session.remove()
    db.drop_all()


def test_get_sensors_with_no_sensors_returns_empty_result(client):
    res = client.get(url_for("api.get_sensors"))
    assert res.json == []
    assert res.status_code == 200


def test_get_sensors_with_sensors_returns_the_sensors(client):
    sensor = Sensor.create(id="the-id", name="the-name", sensor_type="temperature")

    res = client.get(url_for("api.get_sensors"))
    assert res.json == [sensor.to_json()]


def test_get_sensor_when_sensor_exists(client):
    sensor = Sensor.create(id="the-id", name="the-name", sensor_type="temperature")

    res = client.get(url_for("api.get_sensor", sensor_id=sensor.id))
    assert res.status_code == 200
    assert res.json == sensor.to_json()


def test_get_sensor_when_sensor_DNE(client):
    res = client.get(url_for("api.get_sensor", sensor_id="nope"))
    assert res.status_code == 404


def test_get_sensor_new_reading_set_sensor_to_active(client):
    sensor_name = "my-sensor"
    temp_reading = {
        "timestamp": int(time()),
        "sensor": sensor_name,
        "value": 42.1,
        "next_update": 12 * 60,
    }
    res = client.post(url_for("api.add_temperature"), json=temp_reading)
    assert res.status_code == 201

    res = client.get(url_for("api.get_sensor", sensor_id=sensor_name))
    assert res.json["id"] == sensor_name
    assert res.json["is_active"] is True


def test_get_sensor_old_reading_set_sensor_to_inactive(client):
    sensor_name = "my-sensor"
    temp_reading = {
        "timestamp": 1567447540,
        "sensor": sensor_name,
        "value": 42.1,
        "next_update": 12 * 60,
    }
    res = client.post(url_for("api.add_temperature"), json=temp_reading)
    assert res.status_code == 201

    res = client.get(url_for("api.get_sensor", sensor_id=sensor_name))
    assert res.json["id"] == sensor_name
    assert res.json["is_active"] is False


def test_update_sensor_set_name_when_sensor_exists(client):
    sensor = Sensor.create(
        id="the-id",
        name="the-name",
        sensor_type="temperature",
        next_update=datetime.max,
    )

    new_name = "some-name"
    res = client.patch(
        url_for("api.update_sensor", sensor_id=sensor.id),
        json=[{"op": "replace", "path": "/name", "value": new_name}],
    )
    expected = Sensor(
        id=sensor.id,
        name=new_name,
        sensor_type=sensor.sensor_type,
        next_update=datetime.max,
    )
    assert res.status_code == 200
    assert res.json == expected.to_json()

    res = client.get(url_for("api.get_sensor", sensor_id=sensor.id))
    assert res.json == expected.to_json()


def test_update_sensor_when_sensor_DNE(client):
    res = client.patch(url_for("api.update_sensor", sensor_id="nope"))
    assert res.status_code == 404


def test_update_sensor_when_sensor_exists_and_patch_changes_is_invalid(client):
    sensor = Sensor.create(id="the-id", name="the-name", sensor_type="temperature")

    res = client.patch(
        url_for("api.update_sensor", sensor_id=sensor.id),
        json=[{"op": "replace", "path": "/name", "valu": "some-name"}],
    )
    assert res.status_code == 400


def test_sensor_add_sensor_log_when_sensor_exists(client):
    sensor_id = "some-id"
    Sensor.create(
        id=sensor_id,
        name="the-name",
        sensor_type="temperature",
        next_update=datetime.max,
    )

    log = {"timestamp": 1567447541, "message": "some message to log here"}
    res = client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log)
    assert res.status_code == 201


def test_sensor_add_sensor_log_when_sensor_DNE(client):
    sensor_id = "some-id"
    log = {"timestamp": 1567447541, "message": "some message to log here"}
    res = client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log)
    assert res.status_code == 404


def test_sensor_add_sensor_log_when_timestamp_missing(client):
    sensor_id = "some-id"
    Sensor.create(
        id=sensor_id,
        name="the-name",
        sensor_type="temperature",
        next_update=datetime.max,
    )

    log = {"message": "some message to log here"}
    res = client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log)
    assert res.status_code == 400


def test_sensor_add_sensor_log_when_message_missing(client):
    sensor_id = "some-id"
    Sensor.create(
        id=sensor_id,
        name="the-name",
        sensor_type="temperature",
        next_update=datetime.max,
    )

    log = {"timestamp": 1567447541}
    res = client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log)
    assert res.status_code == 400


def test_sensor_add_sensor_log_when_message_length_over_256_chars(client):
    sensor_id = "some-id"
    Sensor.create(
        id=sensor_id,
        name="the-name",
        sensor_type="temperature",
        next_update=datetime.max,
    )

    log = {"timestamp": 1567447541, "message": "*" * 257}
    res = client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log)
    assert res.status_code == 400


def test_get_sensor_log_when_sensor_has_logs(client):
    sensor_id = "some-id"
    Sensor.create(
        id=sensor_id, name="a name", sensor_type="temperature", next_update=datetime.max
    )

    log_row_1 = {"timestamp": 1547477541, "message": "some message to log here"}
    log_row_2 = {"timestamp": 1547478541, "message": "some other message to log here"}
    client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log_row_1)
    client.post(url_for("api.add_sensor_log", sensor_id=sensor_id), json=log_row_2)

    res = client.get(url_for("api.get_sensor_log", sensor_id=sensor_id))

    assert res.status_code == 200
    for row_in_res in res.json:
        assert "id" in row_in_res
        assert row_in_res["timestamp"] in ["2019-01-14T14:52:21", "2019-01-14T15:09:01"]
        assert row_in_res["message"] in log_row_1["message"] or log_row_2["message"]


def test_get_sensor_log_when_sensor_DNE(client):
    res = client.get(url_for("api.get_sensor_log", sensor_id="some-id"))
    assert res.status_code == 404


def test_sensor_reading_last_when_sensor_exists(client):
    sensor_name = "my-sensor"
    client.post(
        url_for("api.add_temperature"),
        json={
            "timestamp": 1567447540,
            "sensor": sensor_name,
            "value": 42.4,
            "next_update": 12 * 60,
        },
    )
    temp_reading = {
        "timestamp": 1567447560,
        "sensor": sensor_name,
        "value": 42.5,
        "next_update": 12 * 60,
    }
    client.post(url_for("api.add_temperature"), json=temp_reading)
    client.post(
        url_for("api.add_temperature"),
        json={
            "timestamp": 1567447550,
            "sensor": sensor_name,
            "value": 42.6,
            "next_update": 12 * 60,
        },
    )

    res = client.get(url_for("api.get_sensor_reading_last", sensor_id=sensor_name))
    assert res.status_code == 200
    assert {
        "sensor_id": sensor_name,
        "timestamp": datetime.utcfromtimestamp(temp_reading["timestamp"]).isoformat(),
        "value": temp_reading["value"],
    } == res.json


def test_sensor_reading_last_when_sensor_have_no_readings(client):
    res = client.get(url_for("api.get_sensor_reading_last", sensor_id="nope"))
    assert res.status_code == 400


def test_add_temperature_creates_new_sensor_if_not_already_exists(client):
    sensor_name = "my-sensor"
    temp_reading = {
        "timestamp": 1567447540,
        "sensor": sensor_name,
        "value": 42.1,
        "next_update": 12 * 60,
    }
    res = client.post(url_for("api.add_temperature"), json=temp_reading)
    assert res.status_code == 201

    res = client.get(url_for("api.get_sensors"))
    assert len(res.json) == 1
    assert any(sensor["name"] == sensor_name for sensor in res.json)


def test_add_temperature_when_timestamp_missing(client):
    res = client.post(
        url_for("api.add_temperature"), json={"sensor": "a-sensor", "value": 42.1}
    )
    assert res.status_code == 400


def test_add_temperature_when_sensor_id_missing(client):
    res = client.post(
        url_for("api.add_temperature"), json={"timestamp": 1567447540, "value": 42.1}
    )
    assert res.status_code == 400


def test_add_temperature_when_value_missing(client):
    res = client.post(
        url_for("api.add_temperature"),
        json={"timestamp": 1567447540, "sensor": "a-sensor"},
    )
    assert res.status_code == 400


def test_add_temperature_when_sensor_registered_as_other_type(client):
    sensor = Sensor.create(id="the-id", name="the-name", sensor_type="not-temperature")

    res = client.post(
        url_for("api.add_temperature"),
        json={"timestamp": 1567447540, "sensor": sensor.id, "value": 42.1},
    )
    assert res.status_code == 400


def test_add_humidity_creates_new_sensor_if_not_already_exists(client):
    sensor_name = "my-sensor"
    temp_reading = {
        "timestamp": 1567447540,
        "sensor": sensor_name,
        "value": 75.2,
        "next_update": 12 * 60,
    }
    res = client.post(url_for("api.add_humidity"), json=temp_reading)
    assert res.status_code == 201

    res = client.get(url_for("api.get_sensors"))
    assert len(res.json) == 1
    assert any(sensor["name"] == sensor_name for sensor in res.json)


def test_add_humidity_when_timestamp_missing(client):
    res = client.post(
        url_for("api.add_humidity"), json={"sensor": "a-sensor", "value": 75.2}
    )
    assert res.status_code == 400


def test_add_humidity_when_sensor_id_missing(client):
    res = client.post(
        url_for("api.add_humidity"), json={"timestamp": 1567447540, "value": 75.2}
    )
    assert res.status_code == 400


def test_add_humidity_when_value_missing(client):
    res = client.post(
        url_for("api.add_humidity"),
        json={"timestamp": 1567447540, "sensor": "a-sensor"},
    )
    assert res.status_code == 400


def test_add_humidity_when_sensor_registered_as_other_type(client):
    sensor = Sensor.create(id="the-id", name="the-name", sensor_type="not-humidity")

    res = client.post(
        url_for("api.add_humidity"),
        json={"timestamp": 1567447540, "sensor": sensor.id, "value": 75.2},
    )
    assert res.status_code == 400
