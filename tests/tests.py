from flask_testing import TestCase
from app import app, db, Flight, Passenger
import uuid

class TestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_flight(self):
        response = self.client.post('/flights', json={
            'flight_name': 'Flight 1',
            'origin': 'A',
            'destination': 'B',
            'cost': 100
        })
        self.assertEqual(response.status_code, 201)

    def test_soft_delete_passenger(self):
        flight = Flight(flight_name='Flight 1', origin='A', destination='B', cost=100)
        db.session.add(flight)
        db.session.commit()
        passenger = Passenger(name='John Doe', email='john.doe@example.com', flight=flight)
        db.session.add(passenger)
        db.session.commit()
        passenger_id = passenger.id
        response = self.client.delete(f'/passengers/{passenger_id}/soft_delete')
        self.assertEqual(response.status_code, 200)
        # Verify soft delete
        passenger = Passenger.query.get(passenger_id)
        self.assertIsNotNone(passenger.deleted_at)
