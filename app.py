from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from uuid import UUID
from models import db, Flight, Passenger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'  # Set up caching
cache = Cache(app)

db.init_app(app)
api = Api(app)
migrate = Migrate(app, db)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'message': 'The requested resource was not found.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'An internal server error occurred.'}), 500

# Resources

class FlightResource(Resource):
    @cache.cached(timeout=120)
    def get(self, flight_id=None):
        if flight_id:
            flight = Flight.query.get(str(flight_id))
            if not flight:
                return {'message': 'Flight not found'}, 404
            return flight.to_dict(), 200
        else:
            flights = Flight.query.all()
            return [flight.to_dict() for flight in flights], 200


    def post(self):
        data = request.get_json()
        
        flight_id = data.get('flight_id')
        
        if not flight_id:
            return {'message': 'Flight ID is required'}, 400

        try:
            # Validate flight_id format
            flight_id = str(UUID(flight_id))
        except ValueError:
            return {'message': 'Invalid flight ID format'}, 400

        # Find the flight by flight_id
        flight = Flight.query.filter_by(id=flight_id).first()
        if not flight:
            return {'message': 'Flight not found'}, 404

        # Create a new passenger
        passenger = Passenger(
            name=data.get('name'),
            email=data.get('email'),
            flight_id=flight_id  # Use the flight_id directly
        )

        try:
            # Add the passenger to the session and commit
            db.session.add(passenger)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error occurred: {str(e)}'}, 500

        return passenger.to_dict(), 201


class PassengerResource(Resource):
    @cache.cached(timeout=120, query_string=True)
    def post(self):
        data = request.get_json()
        flight_id = data.get('flight_id')
        try:
            flight_id = str(UUID(flight_id))
        except ValueError:
            return {'message': 'Invalid flight ID format'}, 400
        
        flight = Flight.query.filter_by(id=flight_id).first()
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
            passenger = Passenger.query.get(str(passenger_id))
            if not passenger:
                return {'message': 'Passenger not found'}, 404
            return passenger.to_dict(), 200
        else:
            passengers = Passenger.query.filter(Passenger.deleted_at.is_(None)).all()
            return [passenger.to_dict() for passenger in passengers], 200

    def put(self, passenger_id):
        passenger = Passenger.query.get(str(passenger_id))
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
        passenger = Passenger.query.get(str(passenger_id))
        if not passenger:
            return {'message': 'Passenger not found'}, 404
        
        passenger.soft_delete()
        return {'message': 'Passenger soft deleted'}, 200


class PassengerRestoreResource(Resource):
    def patch(self, passenger_id):
        passenger = Passenger.query.get(str(passenger_id))
        if not passenger:
            return {'message': 'Passenger not found'}, 404
        
        if passenger.deleted_at is None:
            return {'message': 'Passenger is not soft deleted'}, 400
        
        passenger.restore()
        return {'message': 'Passenger restored'}, 200


# Add resources to the API
api.add_resource(FlightResource, '/flights', '/flights/<uuid:flight_id>')
api.add_resource(PassengerResource, '/passengers', '/passengers/<uuid:passenger_id>')
api.add_resource(PassengerSoftDeleteResource, '/passengers/<uuid:passenger_id>/soft_delete')
api.add_resource(PassengerRestoreResource, '/passengers/<uuid:passenger_id>/restore')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
