from app import app, db, Flight, Passenger
from faker import Faker
import random
import uuid

fake = Faker()

def seed():
    with app.app_context():
        # Create flight records
        flights = []
        for _ in range(5):  # Generate flights
            flight = Flight(
                id=str(uuid.uuid4()),  # Use UUID for primary key and ensure it's a string if needed
                flight_name=fake.company() + ' Flight',
                origin=fake.city(),  # Add origin for completeness
                destination=fake.city(),
                cost=random.uniform(50, 300)  # Add a random cost
            )
            flights.append(flight)
            print(f"Created flight: {flight.flight_name}, Origin: {flight.origin}, Destination: {flight.destination}, Cost: {flight.cost}")

        try:
            # Add flights to the session
            db.session.add_all(flights)
            db.session.commit()
            print('Flights added to the database successfully.')
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding flights: {e}")

        # Create passenger records
        passengers = []
        for flight in flights:
            for _ in range(3):  # Generate 3 passengers per flight
                passenger = Passenger(
                    id=str(uuid.uuid4()),  # Use UUID for primary key and ensure it's a string if needed
                    name=fake.name(),
                    email=fake.email(),
                    flight_id=flight.id
                )
                passengers.append(passenger)
                print(f"Created passenger: {passenger.name}, Email: {passenger.email}, Flight ID: {passenger.flight_id}")

        try:
            # Add passengers to the session
            db.session.add_all(passengers)
            db.session.commit()
            print('Passengers added to the database successfully.')
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding passengers: {e}")

    print('Database seeded successfully!')

if __name__ == '__main__':
    seed()
