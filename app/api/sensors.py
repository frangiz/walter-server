from flask import jsonify, request, current_app
from collections import defaultdict

from datetime import datetime, timedelta

from app import db
from app.models import Reading, Sensor

from app.api import bp
from app.api.errors import bad_request, not_found


@bp.route("/sensors", methods=["GET"])
def get_sensors():
    return jsonify([s.to_json() for s in Sensor.get_all()]), 200


@bp.route("/api/sensors/<string:sensor_id>", methods=["GET"])
def get_sensor(sensor_id):
    sensor = Sensor.get_by_id(sensor_id)
    if sensor is None:
        return not_found("Sensor not found")
    return jsonify(sensor.to_json()), 200


@bp.route("/sensors/<string:sensor_id>", methods=["PATCH"])
def update_sensor(sensor_id):
    sensor = Sensor.get_by_id(sensor_id)
    if sensor is None:
        return not_found("Sensor not found")
    name_change = next(
        c
        for c in request.get_json()
        if {"op": "replace", "path": "/name"}.items() <= c.items()
    )
    if name_change is not None and "value" in name_change:
        sensor.name = name_change["value"]
        db.session.commit()
        return jsonify(sensor.to_json()), 200
    return bad_request("Not able to parse any patch changes")


@bp.route("/sensors/<string:sensor_id>/readings", methods=["GET"])
def get_sensor_readings(sensor_id):
    days_back = request.args.get("days_back") or 3
    timestamps = gen_timestamps(nbr_of_hours_back=int(days_back) * 24)
    response = {}
    for ts in timestamps:
        response[ts.isoformat()] = None
    diffs = defaultdict(lambda: 10 ** 4)
    for reading in Reading.query.filter(Reading.sensor == sensor_id):
        rounded_ts = hour_rounder(reading.timestamp)
        diff = abs((rounded_ts - reading.timestamp).total_seconds())
        if rounded_ts.isoformat() not in response:
            continue
        if diff < diffs[rounded_ts.isoformat()]:
            response[rounded_ts.isoformat()] = reading.value / 100.0
            diffs[rounded_ts.isoformat()] = diff
    return jsonify(response), 200


@bp.route("/sensors/<string:sensor_id>/readings/last", methods=["GET"])
def get_sensor_reading_last(sensor_id):
    reading = (
        Reading.query.filter(Reading.sensor == sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )
    if reading is None:
        return bad_request("Sensor {} had no readings".format(sensor_id))
    result = {
        "sensor_id": reading.sensor,
        "timestamp": reading.timestamp.isoformat(),
        "value": reading.value / 100.0,
    }
    return jsonify(result), 200


@bp.route("/temperature", methods=["POST"])
def add_temperature():
    return add_sensor_value("temperature")


@bp.route("/humidity", methods=["POST"])
def add_humidity():
    return add_sensor_value("humidity")


def add_sensor_value(sensor_type):
    temp_reading = request.get_json()
    if "timestamp" not in temp_reading:
        return bad_request("timestamp attribute missing")
    if "sensor" not in temp_reading:
        return bad_request("sensor attribute missing")
    if "value" not in temp_reading:
        return bad_request("value attribute missing")
    if "next_update" not in temp_reading:
        return bad_request("next_update attribute missing")
    sensor_id = temp_reading["sensor"].replace(":", "")
    sensor = Sensor.get_by_id(sensor_id)
    if sensor is not None and sensor.sensor_type != sensor_type:
        return bad_request("Sensor is already registered as another type")
    if sensor is None:
        sensor = Sensor.create(id=sensor_id, name=sensor_id, sensor_type=sensor_type)
    sensor.next_update = datetime.utcfromtimestamp(
        temp_reading["timestamp"] + temp_reading["next_update"]
    )
    db.session.commit()
    reading = Reading(
        sensor=sensor_id,
        timestamp=datetime.utcfromtimestamp(temp_reading["timestamp"]),
        value=temp_reading["value"] * 100,
    )
    db.session.add(reading)
    db.session.commit()

    return jsonify({"message": "thanks"}), 201


def gen_timestamps(nbr_of_hours_back):
    result = []
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(
        hours=1
    )
    for offset in range(nbr_of_hours_back):
        result.append(now - timedelta(hours=offset))
    result.reverse()
    return result


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return t.replace(second=0, microsecond=0, minute=0, hour=t.hour) + timedelta(
        hours=t.minute // 30
    )
