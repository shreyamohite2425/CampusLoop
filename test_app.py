
import pytest
import app as campus_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_campusloop.db"
    monkeypatch.setattr(campus_app, "DB", test_db)
    campus_app.init_db()

    campus_app.app.config.update(TESTING=True)

    with campus_app.app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CampusLoop" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_add_item(client):
    response = client.post("/add", data={
        "title": "Blue Water Bottle",
        "description": "Bottle found near the canteen",
        "category": "Accessories",
        "location": "Canteen",
        "date": "2026-10-20",
        "kind": "Found"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Blue Water Bottle" in response.data


def test_search_item(client):
    client.post("/add", data={
        "title": "Lost Laptop",
        "description": "Silver laptop",
        "category": "Electronics",
        "location": "Lab 2",
        "date": "2026-10-20",
        "kind": "Lost"
    })

    response = client.get("/?q=Lost%20Laptop")
    assert response.status_code == 200
    assert b"Lost Laptop" in response.data


def test_recover_item(client):
    client.post("/add", data={
        "title": "Lost Notebook",
        "description": "Blue notebook",
        "category": "Books",
        "location": "Library",
        "date": "2026-10-20",
        "kind": "Lost"
    })

    with campus_app.connect_db() as con:
        item = con.execute(
            "SELECT id FROM items WHERE title = ?",
            ("Lost Notebook",)
        ).fetchone()

    response = client.post(
        f"/recover/{item['id']}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Recovered" in response.data
