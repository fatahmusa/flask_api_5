from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from models import db, Flight, Passenger
from flask_migrate import Migrate
from uuid import UUID


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'  # set the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'The requested resource was not found.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'An internal server error occurred.'}), 500


db.init_app(app)
api = Api(app)
migrate = Migrate(app, db)

# Resources
class FlightResource(Resource):
    def post(self):
        data = request.get_json()
        flight = Flight(
        flight_name=data.get('flight_name'),
        origin=data.get('origin'),
        destination=data.get('destination'),
        cost=data.get('cost')
    )
        db.session.add(flight)
        db.session.commit()
        return {'message': 'Flight created', 'flight_id': flight.id}, 201
    
    def get(self, flight_id=None):
        if flight_id:
            try:
                flight_id = UUID(flight_id)  # Ensure flight_id is a UUID
            except ValueError:
                return {'message': 'Invalid flight ID format'}, 400
            flight = Flight.query.get(flight_id)
            if not flight:
                return {'message': 'Flight not found'}, 404
            return flight.to_dict(), 200
        else:
            flights = Flight.query.all()
            return [flight.to_dict() for flight in flights], 200
        
    def put(self, flight_id):
        try:
            flight_id = UUID(flight_id)  # Ensure flight_id is a UUID
        except ValueError:
            return {'message': 'Invalid flight ID format'}, 400
        flight = Flight.query.get(flight_id)
        if not flight:
            return {'message': 'Flight not found'}, 404
        data = request.get_json()
        flight.flight_name = data.get('flight_name', flight.flight_name)
        flight.origin = data.get('origin', flight.origin)
        flight.destination = data.get('destination', flight.destination)
        flight.cost = data.get('cost', flight.cost)
        db.session.commit()
        return {'message': 'Flight updated'}, 200
    

class PassengerResource(Resource):
    def post(self):
        data = request.get_json()

        flight_id = data.get('flight_id')
        try:
            flight_id = UUID(flight_id)  # Ensure flight_id is a UUID
        except ValueError:
            return {'message': 'Invalid flight ID format'}, 400
        flight = Flight.query.get(flight_id)
        if not flight:
            return {'message': 'Flight not found'}, 404
        passenger = Passenger(
            name=data.get('name'),
            email=data.get('email'),
            flight=flight,
        )
        db.session.add(passenger)
        db.session.commit()
        return passenger.to_dict(), 201

    def get(self, passenger_id=None):
        if passenger_id:
            try:
                passenger_id = UUID(passenger_id)  # Ensure passenger_id is a UUID
            except ValueError:
                return {'message': 'Invalid passenger ID format'}, 400
            passenger = Passenger.query.get(passenger_id)
            if not passenger:
                return {'message': 'Passenger not found'}, 404
            return passenger.to_dict(), 200
        else:
            passengers = Passenger.query.filter_by(deleted=False).all()
            return [passenger.to_dict() for passenger in passengers], 200

    def put(self, passenger_id):
        try:
            passenger_id = UUID(passenger_id)  # Ensure passenger_id is a UUID
        except ValueError:
            return {'message': 'Invalid passenger ID format'}, 400
        passenger = Passenger.query.get(passenger_id)
        if not passenger:
            return {'message': 'Passenger not found'}, 404
        data = request.get_json()
        passenger.name = data.get('name', passenger.name)
        passenger.email = data.get('email', passenger.email)
        passenger.checked_in = data.get('checked_in', passenger.checked_in)
        db.session.commit()
        return passenger.to_dict(), 200

class PassengerSoftDeleteResource(Resource):
    def delete(self, passenger_id):
        try:
            passenger_id = UUID(passenger_id)  # Ensure passenger_id is a UUID
        except ValueError:
            return {'message': 'Invalid passenger ID format'}, 400
        passenger = Passenger.query.get(passenger_id)
        if passenger is None:
            return {'message': 'Passenger not found'}, 404
        passenger.soft_delete()
        db.session.commit()
        return {'message': 'Passenger soft deleted'}, 200



class PassengerRestoreResource(Resource):
    def patch(self, passenger_id):
        try:
            passenger_id = UUID(passenger_id)  # Ensure passenger_id is a UUID
        except ValueError:
            return {'message': 'Invalid passenger ID format'}, 400
        passenger = Passenger.query.get(passenger_id)
        if passenger is None:
            return {'message': 'Passenger not found'}, 404
        if not passenger.deleted:
            return {'message': 'Passenger is not soft deleted'}, 400
        passenger.deleted = False
        db.session.commit()
        return {'message': 'Passenger restored'}, 200
    



# Add resources to the API
api.add_resource(FlightResource, '/flights', '/flights/<uuid:flight_id>')
api.add_resource(PassengerResource, '/passengers', '/passengers/<uuid:passenger_id>')
api.add_resource(PassengerSoftDeleteResource, '/passengers/<uuid:passenger_id>/soft_delete')
api.add_resource(PassengerRestoreResource, '/passengers/<uuid:passenger_id>/restore')



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
