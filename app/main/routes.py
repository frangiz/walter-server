from flask import render_template, send_from_directory

from app.main import bp
from app.models import Sensor


@bp.route("/", methods=["GET"])
def get_dashboard():
    sensors = Sensor.get_all()
    return render_template(
        "index.html",
        my_string="Wheeeee!",
        temp_sensors=[s for s in sensors if s.sensor_type == "temperature"],
        humidity_sensors=[s for s in sensors if s.sensor_type == "humidity"],
    )


@bp.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


@bp.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


@bp.route("/vendors/<path:path>")
def send_vendor(path):
    return send_from_directory("vendors", path)
