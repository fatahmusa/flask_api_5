import pytest
from app import app, db

@pytest.fixture(scope='function')
def setup_database():
    # Setup
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
    with app.app_context():
        db.create_all()  # Create all tables
        yield db
        db.drop_all()  # Drop all tables after test
