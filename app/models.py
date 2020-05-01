from app import db
from datetime import datetime
from datetime import timedelta


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Integer)

    def __repr__(self):
        return "<Reading {}, {}, {}>".format(self.sensor, self.timestamp, self.value)

    @staticmethod
    def get_by_id_since(id, days):
        since = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=-days)
        return Reading.query.filter(Reading.sensor == id, Reading.timestamp >= since)


class Sensor(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), index=True)
    sensor_type = db.Column(db.String(64), index=True)
    next_update = db.Column(db.DateTime, default=datetime.min)
    firmware_version = db.Column(db.String(8), default="")

    def __repr__(self):
        return "<Sensor {}, {}, {}, {}, {}>".format(
            self.id,
            self.name,
            self.sensor_type,
            self.next_update,
            self.firmware_version,
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "sensor_type": self.sensor_type,
            "is_active": datetime.utcnow() <= self.next_update
            if self.next_update is not None
            else False,
            "firmware_version": self.firmware_version,
        }

    @staticmethod
    def get_all():
        return Sensor.query.all()

    @staticmethod
    def get_by_id(id):
        return Sensor.query.filter_by(id=id).first()

    @staticmethod
    def create(id, name, sensor_type, next_update=datetime.min, firmware_version=""):
        sensor = Sensor(
            id=id,
            name=name,
            sensor_type=sensor_type,
            next_update=next_update,
            firmware_version=firmware_version,
        )
        db.session.add(sensor)
        db.session.commit()
        return sensor


class LogRow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(64), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.min)
    message = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return "<LogRow {}, {}, {}, {}>".format(
            self.id, self.sensor_id, self.timestamp, self.message
        )

    def to_json(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
        }

    @staticmethod
    def get_by_sensor_id(sensor_id):
        return LogRow.query.filter_by(sensor_id=sensor_id).all()

    @staticmethod
    def create(sensor_id, timestamp, message):
        log_row = LogRow(sensor_id=sensor_id, timestamp=timestamp, message=message)
        db.session.add(log_row)
        db.session.commit()
        return log_row
