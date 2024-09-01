from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
import uuid
from collections import defaultdict, deque  

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

    #create a relationship to Layover Model
    layovers = db.relationship('Layover', backref='flight', lazy=True)

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
    
    def calculate_total_cost(self):
        """Calculate total cost of the flight including all layovers."""
        total_cost = self.cost
        for layover in self.layovers:
            total_cost += layover.cost
        return total_cost
    
    @staticmethod #Dijkstra Algorithm
    def find_cheapest_route(start, end):
        """Find the cheapest route between two destinations using Dijkstra's algorithm."""
        
        # Step 1: Build the graph
        graph = defaultdict(list)
        flights = Flight.query.all()
        for flight in flights:
            graph[flight.origin].append((flight.destination, flight.cost, flight.id))

        # Step 2: Initialize the Dijkstra's algorithm structures
        min_cost = {start: 0}
        previous_flight = {}
        flight_route = {}
        queue = deque([start])

        while queue:
            current_airport = queue.popleft()

            for destination, cost, flight_id in graph[current_airport]:
                new_cost = min_cost[current_airport] + cost

                if destination not in min_cost or new_cost < min_cost[destination]:
                    min_cost[destination] = new_cost
                    previous_flight[destination] = current_airport
                    flight_route[destination] = flight_id
                    queue.append(destination)

        # Step 3: Construct the cheapest route
        route = []
        total_cost = min_cost.get(end, None)

        if total_cost is None: #check if the destination is unreachable
            return None, float('inf')

        step = end #starts tracing back from the destination to the start
        while step != start:
            flight_id = flight_route.get(step)
            if flight_id:
                flight = db.session.get(Flight, flight_id)
                route.insert(0, flight)# adds the flight to the beginning of the route list in reverse order
                step = previous_flight[step]
            else:
                break

        return route, total_cost
    
class Layover(BaseModel, db.Model):
    __tablename__ = 'layover'

    airport = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    flight_id = db.Column(db.String(36), db.ForeignKey('flight.id'))

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'airport': self.airport,
            'cost': self.cost,
            'flight_id': str(self.flight_id),
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
    