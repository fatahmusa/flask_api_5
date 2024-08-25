from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from functools import lru_cache
import numpy as np

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deleted = db.Column(db.Boolean, default=False)

    def soft_delete(self):
        self.deleted = True
        db.session.commit()

    def restore(self):
        self.deleted = False
        db.session.commit()

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

class Flight(BaseModel):
    __tablename__ = 'flights'

    flight_name = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    origin = db.Column(db.String(120), nullable=False)  

    passengers = db.relationship('Passenger', backref='flight', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'flight_name': self.flight_name,
            'origin': self.origin,  # Include origin in to_dict
            'destination': self.destination,
            'cost': self.cost,
            'passengers': [passenger.to_dict() for passenger in self.passengers]
        }

    def __repr__(self):
        return f'<Flight {self.flight_name}>'
    

    @staticmethod
    @lru_cache(maxsize=32)  # Memoize the function with a cache size of 32 entries
    def find_minimum_cost_path(origin: str, destination: str) -> float:
        """Returns the minimum cost to travel from origin to destination."""
        # Retrieve all flights
        flights = Flight.query.all()

        # Create a dictionary to store costs
        cost_dict = {}
        for flight in flights:
            if flight.flight_name not in cost_dict:
                cost_dict[flight.flight_name] = {}
            cost_dict[flight.flight_name][flight.destination] = flight.cost

        # Create a list of all cities 
        cities = list(set([flight.flight_name for flight in flights] + [flight.destination for flight in flights]))

        # Initialize cost table
        num_cities = len(cities)
        INF = float('inf')
        cost_table = np.full((num_cities, num_cities), INF)

        # Create city index mapping
        city_index = {city: i for i, city in enumerate(cities)}

        # Set cost for direct flights
        for flight in flights:
            u = city_index[flight.flight_name]
            v = city_index[flight.destination]
            cost_table[u][v] = flight.cost

        # Set the cost to reach the origin city as 0
        start_index = city_index.get(origin)
        if start_index is None:
            raise ValueError(f"Origin city {origin} not found in the flight data.")
        cost_table[start_index][start_index] = 0

        # Perform tabulation (Bellman-Ford algorithm)
        for _ in range(num_cities - 1):
            for i in range(num_cities):
                for j in range(num_cities):
                    if cost_table[i][j] == INF:
                        continue
                    for k in range(num_cities):
                        if cost_table[i][k] + cost_table[k][j] < cost_table[i][j]:
                            cost_table[i][j] = cost_table[i][k] + cost_table[k][j]

        # Retrieve the minimum cost to reach the destination city
        end_index = city_index.get(destination)
        if end_index is None:
            raise ValueError(f"Destination city {destination} not found in the flight data.")

        return cost_table[start_index][end_index] if cost_table[start_index][end_index] != INF else float('inf')
    
    @staticmethod
    @lru_cache(maxsize=32)  # Memoize the function with a cache size of 32 entries
    def get_passenger_count(flight_id):
        """Returns the total number of passengers for a given flight."""
        flight = Flight.query.get(flight_id)
        if flight:
            return len(flight.passengers)
        return 0
    


class Passenger(BaseModel):
    __tablename__ = 'passengers'

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    checked_in = db.Column(db.Boolean, default=False)
    flight_id = db.Column(db.String(36), db.ForeignKey('flights.id'), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'checked_in': self.checked_in,
            'flight_id': str(self.flight_id)
        }

    def __repr__(self):
        return f'<Passenger {self.name}>'
