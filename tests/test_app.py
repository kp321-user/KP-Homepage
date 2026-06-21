import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    with flask_app.test_client() as client:
        yield client


def test_home_redirects_or_loads(client):
    response = client.get("/")
    assert response.status_code in (200, 302)


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
