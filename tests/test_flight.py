import pytest
from app import db, Flight, app

# Set up Flask application context and test database
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture(scope='function')
def setup_test_data(test_client):
    with app.app_context():
        # Insert test data
        flight1 = Flight(flight_name='A', destination='B', cost=100)
        flight2 = Flight(flight_name='B', destination='C', cost=200)
        flight3 = Flight(flight_name='A', destination='C', cost=500)
        db.session.add_all([flight1, flight2, flight3])
        db.session.commit()
        yield
        db.session.remove()

def test_find_minimum_cost_path_basic(test_client, setup_test_data):
    result = Flight.find_minimum_cost_path('A', 'C')
    assert result == 300  # Minimum cost from A to C should be 300

def test_find_minimum_cost_path_no_path(test_client, setup_test_data):
    result = Flight.find_minimum_cost_path('B', 'A')
    assert result == float('inf')  # There should be no path from B to A

def test_find_minimum_cost_path_negative_cycle(test_client):
    with app.app_context():
        # Adding a negative cycle
        flight4 = Flight(flight_name='C', destination='A', cost=-50)
        db.session.add(flight4)
        db.session.commit()
        with pytest.raises(ValueError, match="Graph contains negative weight cycle"):
            Flight.find_minimum_cost_path('A', 'C')
