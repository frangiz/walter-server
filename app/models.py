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

    def __repr__(self):
        return "<Sensor {}, {}, {}, {}>".format(
            self.id, self.name, self.sensor_type, self.next_update
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "sensor_type": self.sensor_type,
            "is_active": datetime.utcnow() <= self.next_update
            if self.next_update is not None
            else False,
        }

    @staticmethod
    def get_all():
        return Sensor.query.all()

    @staticmethod
    def get_by_id(id):
        return Sensor.query.filter_by(id=id).first()

    @staticmethod
    def create(id, name, sensor_type, next_update=datetime.min):
        sensor = Sensor(
            id=id, name=name, sensor_type=sensor_type, next_update=next_update
        )
        db.session.add(sensor)
        db.session.commit()
        return sensor
