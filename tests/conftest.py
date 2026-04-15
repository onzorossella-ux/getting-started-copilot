import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(scope="session")
def client():
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def clean_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original_activities
