import datetime
import json
import os
import requests
import smtplib
import ssl


def check_status(config):
    inactive_sensors = [
        sensor["name"] for sensor in get_sensors() if sensor["is_active"] is False
    ]
    if len(inactive_sensors) > 0:
        send_email(config, create_msg(inactive_sensors))
    else:
        print("All sensors is OK. No need for any action.")


def send_email(config, msg):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["host"], config["port"], context=context) as server:
        server.login(config["sender_email"], config["password"])
        server.sendmail(config["sender_email"], config["recipients"], msg)
        server.quit()
        print("Email sent.")


def create_msg(sensors):
    return """Subject: Sensors not responding

        I am sorry to inform you that one or more sensors might not be active anymore. I have failed to receive status from {}.

        This message was generated {}

        Yours sincerely,
        Walter
        """.format(
        ", ".join(sensors), datetime.datetime.now()
    )


def get_sensors():
    return requests.get("http://localhost:5000/api/sensors").json()


if __name__ == "__main__":
    with open(os.path.join("scripts", "check_status_config.json"), "r") as f:
        data = f.read()
    config = json.loads(data)
    check_status(config)
