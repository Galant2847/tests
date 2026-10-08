import pytest

from models import ObjectIDsResponse

NOTHING_FOUND_QUERY = "zzqqxxnotanartwork123456"


def search_ok(client, q=None, **filters) -> ObjectIDsResponse:
    response = client.search(q, **filters)
    assert response.status_code == 200, (
        f"Статус {response.status_code}: {response.text[:200]}"
    )
    return ObjectIDsResponse.model_validate(response.json())


def test_search_by_keyword_returns_valid_structure(client):
    response = client.search("sunflowers")

    assert response.status_code == 200
    data = ObjectIDsResponse.model_validate(response.json())
    assert data.total > 0
    assert 0 < len(data.objectIDs) <= data.total
    assert len(set(data.objectIDs)) == len(data.objectIDs), (
        "ID не должны повторяться"
    )


def test_search_results_are_relevant_to_keyword(client, load_object):
    keyword = "sunflowers"
    data = search_ok(client, keyword)

    found = []
    for object_id in data.objectIDs[:10]:
        obj = load_object(object_id)
        text = " ".join([
            obj.title,
            obj.objectName,
            obj.medium,
            obj.classification,
            *[tag.term for tag in (obj.tags or [])],
        ]).lower()
        found.append(keyword in text)

    assert any(found), (
        f"ни в одном из первых объектов нет слова '{keyword}'"
    )


def test_search_with_no_matches_returns_empty_result(client):
    data = search_ok(client, NOTHING_FOUND_QUERY)

    assert data.total == 0
    assert data.objectIDs == []


def test_default_page_size_is_100(client):
    data = search_ok(client, "painting")

    assert data.total > 100
    assert len(data.objectIDs) == 100


@pytest.mark.parametrize("limit", [1, 5, 50])
def test_limit_controls_number_of_results(client, limit):
    data = search_ok(client, "painting", limit=limit)

    assert len(data.objectIDs) == limit


def test_limit_above_maximum_is_capped_at_500(client):
    data = search_ok(client, "painting", limit=1000)

    assert len(data.objectIDs) == 500


def test_offset_returns_next_page_without_overlap(client):
    page1 = search_ok(client, "painting", offset=0, limit=20)
    page2 = search_ok(client, "painting", offset=20, limit=20)

    assert len(page1.objectIDs) == len(page2.objectIDs) == 20
    assert not set(page1.objectIDs) & set(page2.objectIDs)


def test_filter_department_id(client, load_object):
    european_paintings = 11
    data = search_ok(
        client, "flowers", departmentId=european_paintings, limit=5
    )

    assert data.total > 0
    for object_id in data.objectIDs[:3]:
        assert load_object(object_id).department == "European Paintings"


def test_filter_is_highlight(client, load_object):
    data = search_ok(client, "sunflowers", isHighlight=True, limit=5)

    assert data.total > 0
    for object_id in data.objectIDs[:3]:
        assert load_object(object_id).isHighlight is True


def test_filter_title_matches_title_field(client, load_object):
    data = search_ok(client, "sunflowers", title=True, limit=5)

    assert data.total > 0
    for object_id in data.objectIDs[:3]:
        assert "sunflower" in load_object(object_id).title.lower()


def test_filter_date_range(client, load_object):
    date_begin, date_end = 1700, 1800
    data = search_ok(
        client, "African", dateBegin=date_begin, dateEnd=date_end, limit=5
    )

    assert data.total > 0
    for object_id in data.objectIDs[:3]:
        obj = load_object(object_id)
        assert obj.objectEndDate >= date_begin
        assert obj.objectBeginDate <= date_end


def test_filter_narrows_down_results(client):
    without_filter = search_ok(client, "flowers", limit=1)
    with_filter = search_ok(client, "flowers", isHighlight=True, limit=1)

    assert with_filter.total <= without_filter.total


def test_api_has_no_sort_parameter(client):
    plain = search_ok(client, "cat", limit=20)
    with_sort = search_ok(client, "cat", limit=20, sort="title")

    assert plain.objectIDs == with_sort.objectIDs