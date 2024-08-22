from app import app, db, Flight, Passenger
from faker import Faker

fake = Faker()

def seed():
    with app.app_context():
        # Create flight records
        flights = []
        for _ in range(5):  # Generate flights
            flight = Flight(
                flight_name=fake.company() + ' Flight',
                destination=fake.city()
            )
            flights.append(flight)
        
        # Add flights to the session
        db.session.add_all(flights)
        db.session.commit()

        # Create passenger records
        passengers = []
        for flight in flights:
            for _ in range(3):  # Generate 3 passengers per flight
                passenger = Passenger(
                    name=fake.name(),
                    email=fake.email(),
                    flight_id=flight.id
                )
                passengers.append(passenger)
        
        # Add passengers to the session
        db.session.add_all(passengers)
        db.session.commit()

    print('Database seeded successfully!')

if __name__ == '__main__':
    seed()