import pytest  # noqa: F401

test_user = "octocat"


def test_healthz_returns_ok(test_client):
    r = test_client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_read_user_gists_fake_paginated(monkeypatch, test_client):
    """Verify the `/users/{username}` endpoint aggregates paginated results.

    This test monkeypatches the `paginate_git_pages` helper used by the
    route to return two small pages, and asserts that the endpoint
    returns them under the `results` key.
    """
    pages = [{"id": 1}, {"id": 2}]

    def fake_paginate(client, url):
        for p in pages:
            yield p

    monkeypatch.setattr("app.routes.paginate_git_pages", fake_paginate)

    r = test_client.get(f"/users/{test_user}")
    assert r.status_code == 200
    assert r.json() == {"results": pages}


def test_read_user_gists_e2e_paginated(test_client):
    """Verify the `/users/{username}` endpoint & aggregates paginated results.

    This test runs e2e test on the github api to ensure that pagination
    is working as expected.
    """

    r = test_client.get(f"/users/{test_user}")
    assert r.status_code == 200
    results = r.json().get("results", [])
    assert len(results) >= 1  # At least one page should be returned


def test_metrics_endpoint_available(test_client):
    """Ensure the Instrumentator exposes a `/metrics` endpoint.

    We don't assert on specific metrics content; it's sufficient that the
    endpoint exists and returns plain-text metrics data.
    """
    r = test_client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")
