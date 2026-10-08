import pytest

from models import MetObject

NON_EXISTENT_ID = 999_999_999


@pytest.mark.parametrize("object_id", [45734, 436535])
def test_get_object_returns_200_and_valid_model(client, object_id):
    response = client.get_object(object_id)

    assert response.status_code == 200
    obj = MetObject.model_validate(response.json())
    assert obj.objectID == object_id
    assert obj.title.strip()


def test_known_object_has_expected_data(load_object):
    obj = load_object(436535)

    assert obj.isHighlight is True
    assert obj.isPublicDomain is True
    assert "van Gogh" in obj.artistDisplayName
    assert obj.objectBeginDate <= obj.objectEndDate
    assert obj.objectURL.endswith("/436535")


def test_get_non_existent_object_returns_404(client):
    response = client.get_object(NON_EXISTENT_ID)

    assert response.status_code == 404
    assert response.json().get("message"), "в ответе ожидается поле message"