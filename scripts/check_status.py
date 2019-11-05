import datetime
import json
import os
import requests
import smtplib
import ssl


def check_status(config):
    new_state = get_current_state()
    last_known_state = get_last_known_state()
    activated = get_activated(new_state, last_known_state)
    deactivated = get_deactivated(new_state, last_known_state)
    save_state(new_state)
    if len(activated) == 0 and len(deactivated) == 0:
        print("No change in the state, will not send any email.")
        return
    send_email(config, create_msg(activated, deactivated))


def send_email(config, msg):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["host"], config["port"], context=context) as server:
        server.login(config["sender_email"], config["password"])
        server.sendmail(config["sender_email"], config["recipients"], msg)
        server.quit()
        print("Email sent.")


def create_msg(activated_sensors, deactivated_sensors):

    msg = ["Subject: Sensors have changed state", ""]
    if len(deactivated_sensors) > 0:
        msg.append(
            "I am sorry to inform you that one or more sensors might not be"
            " active anymore. I have failed to receive status from:"
        )
        [msg.append("* " + sensor) for sensor in deactivated_sensors]
        msg.append("")
    if len(activated_sensors) > 0:
        msg.append("Some sensors have been activated again:")
        [msg.append("* " + sensor) for sensor in activated_sensors]
        msg.append("")
    msg.append("This message was generated {}".format(datetime.datetime.utcnow()))
    msg.append("")
    msg.append("Yours sincerely,")
    msg.append("Walter")

    return "\r\n".join(msg)


def get_activated(new_state, old_state):
    result = []
    for sensor, value in new_state.items():
        if value is True and sensor in old_state and old_state[sensor] is False:
            result.append(sensor)
    return result


def get_deactivated(new_state, old_state):
    result = []
    for sensor, value in new_state.items():
        if value is False and sensor in old_state and old_state[sensor] is True:
            result.append(sensor)
    return result


def get_last_known_state():
    state_file_path = os.path.join("scripts", "check_status_state.json")
    if not os.path.exists(state_file_path):
        return {}
    with open(state_file_path, "r") as f:
        data = f.read()
    if data == "":
        return {}
    return json.loads(data)


def save_state(state):
    state_file_path = os.path.join("scripts", "check_status_state.json")
    with open(state_file_path, "w+") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


def get_current_state():
    return {sensor["name"]: sensor["is_active"] for sensor in get_sensors()}


def get_sensors():
    return requests.get("http://localhost:5000/api/sensors").json()


if __name__ == "__main__":
    with open(os.path.join("scripts", "check_status_config.json"), "r") as f:
        data = f.read()
    config = json.loads(data)
    check_status(config)
