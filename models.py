from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    flight_name = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    deleted = db.Column(db.Boolean, default=False)

    passengers = db.relationship('Passenger', backref='flight', cascade='all, delete-orphan')

    def soft_delete(self):
        self.deleted = True

    def restore(self):
        self.deleted = False

    def to_dict(self):
        return {
            'id': self.id,
            'flight_name': self.flight_name,
            'destination': self.destination,
            'passengers': [passenger.to_dict() for passenger in self.passengers]
        }

    def __repr__(self):
        return f'<Flight {self.flight_name}>'

class Passenger(db.Model):
    __tablename__ = 'passengers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    checked_in = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)

    def soft_delete(self):
        self.deleted = True

    def restore(self):
        self.deleted = False

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'checked_in': self.checked_in,
            'deleted': self.deleted,
            'flight_id': self.flight_id
        }

    def __repr__(self):
        return f'<Passenger {self.name}>'
