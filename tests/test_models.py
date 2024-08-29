import pytest
import uuid
from app import app, db
from models import Flight, Layover, Passenger

@pytest.fixture(scope='function')
def setup_db():
    """Fixture to set up and tear down the database."""
    with app.app_context():
        db.create_all()
        yield db  # Testing happens here
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(setup_db):
    """Fixture to provide a test client."""
    with app.test_client() as client:
        with app.app_context():  # Ensure the application context is available
            yield client

def test_flight_creation(client):
    """Test the creation of a Flight instance and its attributes."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        saved_flight = Flight.query.first()
        assert saved_flight is not None
        assert saved_flight.flight_name == 'Test Flight'
        assert saved_flight.origin == 'City A'
        assert saved_flight.destination == 'City B'
        assert saved_flight.cost == 100.0

def test_layover_creation(client):
    """Test the creation of a Layover instance and its association with a Flight."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        layover = Layover(
            airport='City C',
            cost=50.0,
            flight_id=flight.id
        )
        db.session.add(layover)
        db.session.commit()

        saved_layover = Layover.query.first()
        assert saved_layover is not None
        assert saved_layover.airport == 'City C'
        assert saved_layover.cost == 50.0
        assert saved_layover.flight_id == flight.id
        assert saved_layover.flight.flight_name == 'Test Flight'

def test_passenger_creation(client):
    """Test the creation of a Passenger instance and its association with a Flight."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        passenger = Passenger(
            name='John Doe',
            email='johndoe@example.com',
            flight_id=flight.id
        )
        db.session.add(passenger)
        db.session.commit()

        saved_passenger = Passenger.query.first()
        assert saved_passenger is not None
        assert saved_passenger.name == 'John Doe'
        assert saved_passenger.email == 'johndoe@example.com'
        assert saved_passenger.flight_id == flight.id
        assert saved_passenger.flight.flight_name == 'Test Flight'

def test_flight_total_cost(client):
    """Test the calculation of the total flight cost including layovers."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        layover = Layover(
            airport='City C',
            cost=50.0,
            flight_id=flight.id
        )
        db.session.add(layover)
        db.session.commit()

        total_cost = flight.calculate_total_cost()
        assert total_cost == 150.0

def test_soft_delete(client):
    """Test the soft delete functionality of a Flight instance."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        flight.soft_delete()
        assert flight.deleted_at is not None
        assert flight.is_deleted

def test_restore(client):
    """Test restoring a soft-deleted Flight instance."""
    with app.app_context():
        flight = Flight(
            flight_name='Test Flight',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        db.session.add(flight)
        db.session.commit()

        flight.soft_delete()
        assert flight.is_deleted

        flight.restore()
        assert flight.deleted_at is None
        assert not flight.is_deleted

def test_find_cheapest_route(client):
    """Test the Dijkstra's algorithm implementation for finding the cheapest route."""
    with app.app_context():
        flight1 = Flight(
            flight_name='Flight 1',
            origin='City A',
            destination='City B',
            cost=100.0
        )
        flight2 = Flight(
            flight_name='Flight 2',
            origin='City B',
            destination='City C',
            cost=50.0
        )
        flight3 = Flight(
            flight_name='Flight 3',
            origin='City A',
            destination='City C',
            cost=200.0
        )
        db.session.add_all([flight1, flight2, flight3])
        db.session.commit()

        route, total_cost = Flight.find_cheapest_route('City A', 'City C')
        assert total_cost == 150.0
        assert len(route) == 2
        assert route[0].id == flight1.id
        assert route[1].id == flight2.id
