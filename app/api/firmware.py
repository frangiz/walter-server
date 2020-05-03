import os
import glob
from flask import jsonify, request, current_app, send_from_directory

from app import db
from app.models import Sensor

from app.api import bp
from app.api.errors import error_response, bad_request


@bp.route("/firmware/updates", methods=["GET"])
def get_new_firmware():
    ver = request.args.get("ver", default=None)
    if ver is None or not ver.isdigit():
        return bad_request("Required parameter 'ver' is missing or not an int.")

    dev_type = request.args.get("dev_type", default=None)
    if dev_type is None:
        return bad_request("Required parameter 'dev_type' is missing.")
    dev_type = dev_type.lower()

    dev_id = request.args.get("dev_id", default=None)
    if dev_id is None:
        return bad_request("Required parameter 'dev_id' is missing.")

    current_app.logger.debug(
        "ver: " + ver + ", dev: " + dev_type + " dev_id: " + dev_id
    )
    set_version_on_sensors(ver, dev_id)

    latest_firmware = find_latest_firmware(ver, dev_type)
    if latest_firmware is None:
        current_app.logger.debug("Device already up to date")
        return error_response(304, "Device already up to date")

    current_app.logger.debug("Found firmware version: " + latest_firmware)
    return send_from_directory(
        directory="../firmwares",
        filename=latest_firmware,
        as_attachment=True,
        mimetype="application/octet-stream",
        attachment_filename=latest_firmware,
    )


def find_latest_firmware(ver, dev_type):
    if not os.path.exists("firmwares"):
        os.makedirs("firmwares")
    firmwares = sorted(glob.glob("firmwares/" + dev_type + "-*.bin"), reverse=True)
    if len(firmwares) > 0:
        firmware_filename = firmwares[0].replace("firmwares" + os.sep, "")
        if firmware_filename != dev_type + "-" + str(ver) + ".bin":
            return firmware_filename
    return None


def set_version_on_sensors(ver, dev_id):
    for s in Sensor.get_all():
        if s.id.startswith(dev_id + "-"):
            s.firmware_version = str(ver)
    db.session.commit()
