from app import db
from datetime import datetime


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Integer)

    def __repr__(self):
        return "<Reading {}, {}, {}>".format(self.sensor, self.timestamp, self.value)


class Sensor(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), index=True)
    sensor_type = db.Column(db.String(64), index=True)

    def __repr__(self):
        return "<Sensor {}, {}, {}>".format(self.id, self.name, self.sensor_type)

    def to_json(self):
        return {"id": self.id, "name": self.name, "sensor_type": self.sensor_type}

    @staticmethod
    def get_all():
        return Sensor.query.all()

    @staticmethod
    def get_by_id(id):
        return Sensor.query.filter_by(id=id).first()

    @staticmethod
    def create(id, name, sensor_type):
        sensor = Sensor(id=id, name=name, sensor_type=sensor_type)
        db.session.add(sensor)
        db.session.commit()
        return sensor
