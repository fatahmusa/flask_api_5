import pytest
import uuid
from app import app, db
from models import Flight, Passenger

@pytest.fixture(scope='function')
def setup_db():
    """Fixture to set up and tear down the database."""
    with app.app_context():
        db.create_all()  # Create tables before each test
        yield db  # Provide the test access to the db
        db.session.remove()
        db.drop_all()  # Drop tables after each test to ensure a clean slate

@pytest.fixture(scope='function')
def client(setup_db):
    """Fixture to provide a test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def clear_flights_db():
    # Clear flights table
    Flight.query.delete()
    db.session.commit()


def test_get_all_flights(client, clear_flights_db):
    """Test retrieving all flights when there are no flights in the database."""
    response = client.get('/flights')
    assert response.status_code == 200
    assert response.get_json() == []

def test_post_flight(client):
    """Test posting a new flight."""
    flight_id = str(uuid.uuid4())
    flight_data = {
        'id': flight_id,
        'flight_name': 'Test Flight',
        'origin': 'City A',
        'destination': 'City B',
        'cost': 100
    }
    response = client.post('/flights', json=flight_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['flight_name'] == 'Test Flight'
    assert data['origin'] == 'City A'
    assert data['destination'] == 'City B'
    assert data['cost'] == 100

def test_get_flight_by_id(client):
    """Test retrieving a flight by ID."""
    flight_id = str(uuid.uuid4())
    flight = Flight(
        id=flight_id,
        flight_name='Test Flight',
        origin='City A',
        destination='City B',
        cost=100
    )
    db.session.add(flight)
    db.session.commit()

    response = client.get(f'/flights/{flight_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['flight_name'] == 'Test Flight'

def test_create_passenger(client):
    """Test creating a passenger for an existing flight."""
    flight_id = str(uuid.uuid4())
    flight = Flight(
        id=flight_id,
        flight_name='Test Flight',
        origin='City A',
        destination='City B',
        cost=100
    )
    db.session.add(flight)
    db.session.commit()

    passenger_data = {
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'flight_id': flight_id
    }
    response = client.post('/passengers', json=passenger_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'John Doe'
    assert data['email'] == 'johndoe@example.com'

def test_update_passenger(client):
    """Test updating a passenger's information."""
    flight_id = str(uuid.uuid4())
    passenger_id = str(uuid.uuid4())
    flight = Flight(
        id=flight_id,
        flight_name='Test Flight',
        origin='City A',
        destination='City B',
        cost=100
    )
    passenger = Passenger(
        id=passenger_id,
        name='John Doe',
        email='johndoe@example.com',
        flight_id=flight_id
    )
    db.session.add(flight)
    db.session.add(passenger)
    db.session.commit()

    update_data = {
        'name': 'Jane Doe',
        'email': 'janedoe@example.com'
    }
    response = client.put(f'/passengers/{passenger_id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Jane Doe'
    assert data['email'] == 'janedoe@example.com'

def test_soft_delete_passenger(client):
    """Test soft-deleting a passenger."""
    flight_id = str(uuid.uuid4())
    passenger_id = str(uuid.uuid4())
    flight = Flight(
        id=flight_id,
        flight_name='Test Flight',
        origin='City A',
        destination='City B',
        cost=100
    )
    passenger = Passenger(
        id=passenger_id,
        name='John Doe',
        email='johndoe@example.com',
        flight_id=flight_id
    )
    db.session.add(flight)
    db.session.add(passenger)
    db.session.commit()

    response = client.delete(f'/passengers/{passenger_id}/soft_delete')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Passenger soft deleted'

    passenger = db.session.get(Passenger, passenger.id)
    assert passenger.deleted_at is not None

def test_find_cheapest_route(client):
    """Test finding the cheapest route between two cities."""
    flight1_id = str(uuid.uuid4())
    flight2_id = str(uuid.uuid4())
    flight1 = Flight(
        id=flight1_id,
        flight_name='Flight 1',
        origin='City A',
        destination='City B',
        cost=100.0
    )
    flight2 = Flight(
        id=flight2_id,
        flight_name='Flight 2',
        origin='City B',
        destination='City C',
        cost=50.0
    )
    db.session.add_all([flight1, flight2])
    db.session.commit()

    response = client.get('/flights/cheapest_route?origin=City A&destination=City C')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total_cost'] == 150.0
    assert len(data['route']) == 2
    assert data['route'][0]['id'] == flight1_id
    assert data['route'][1]['id'] == flight2_id
