import pytest
import json
from server import loadClubs,loadCompetitions,app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client