from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
import uuid

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = db.Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self):
        """Set the deleted_at timestamp to mark as soft deleted."""
        self.deleted_at = func.now()
        db.session.commit()

    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
    def restore(self):
        """Clear the deleted_at timestamp to restore the record."""
        self.deleted_at = None
        db.session.commit()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def to_dict(self):
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }


class Flight(BaseModel, db.Model ):
    __tablename__ = 'flight'

    id = Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_name = db.Column(db.String(255), nullable=False)
    origin = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def to_dict(self):
        # Inherit the common fields from BaseModel and add specific fields
        base_dict = super().to_dict()
        base_dict.update({
            'flight_name': self.flight_name,
            'origin': self.origin,
            'destination': self.destination,
            'cost': self.cost
        })
        return base_dict

class Passenger(BaseModel, db.Model ):
    __tablename__ = 'passenger'

    id = Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    checked_in = db.Column(db.Boolean, default=False)
    flight_id = db.Column(db.String(36), db.ForeignKey('flight.id'))
    flight = db.relationship('Flight', backref=db.backref('passengers', lazy=True))

    def to_dict(self):
        # Inherit the common fields from BaseModel and add specific fields
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'email': self.email,
            'checked_in': self.checked_in,
            'flight_id': str(self.flight_id),
        })
        return base_dict
    