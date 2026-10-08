import logging

import pytest

from client import MetClient
from models import MetObject

logger = logging.getLogger("met_api")

@pytest.fixture(scope="session")
def client() -> MetClient:
    return MetClient()

@pytest.fixture(scope="session")
def load_object(client):
    def _load(object_id: int) -> MetObject:
        response = client.get_object(object_id)
        assert response.status_code == 200, f"Объект {object_id}: статус {response.status_code}"
        return MetObject.model_validate(response.json())

    return _load

@pytest.fixture(autouse=True)
def log_test_boundaries(request):
    logger.info("START %s :", request.node.nodeid)
    yield
    logger.info("END %s :", request.node.nodeid)