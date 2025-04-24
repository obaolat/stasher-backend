import pytest
from app import create_app, db  # Adjust imports based on your app structure
from app.models import Stashpoint, Booking  # Ensure correct imports

# Fixture for setting up and tearing down the app context
@pytest.fixture
def app():
    app = create_app('app.config.TestingConfig')  # Adjust according to how you initialize your app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/test_db'  # Adjust as needed
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up the database
    with app.app_context():
        db.create_all()  # Creates the tables for the test run
    yield app

    # Clean up the database after tests are done
    with app.app_context(): 
        db.drop_all()  # Drops the tables after the test

# Fixture for providing the test client to make requests
@pytest.fixture
def client(app):
    return app.test_client()
