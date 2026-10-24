"""
Unit tests for the API client module.

These tests verify HTTP requests, response handling, timeout retries,
error handling, and pagination without making real API requests.
"""

import requests

import api_client


def test_fetch_data_from_api_returns_json_data(monkeypatch):
    # Testing whether a successful API response returns its JSON data.
    monkeypatch.setattr(api_client, "API_URL", "https://example.com")

    expected_data = {
        "products": [{"id": 1, "title": "Product A"}],
        "limit": 30,
        "skip": 0,
        "total": 1,
    }

    class MockResponse:
        # Simulating a successful HTTP response.
        def raise_for_status(self):
            pass

        def json(self):
            return expected_data

    def mock_get(url, timeout):
        # Verifying the requested endpoint and timeout value.
        assert url == "https://example.com/products?limit=30&skip=0"
        assert timeout == 10
        return MockResponse()

    monkeypatch.setattr(api_client.requests, "get", mock_get)

    result = api_client.fetch_data_from_api(skip=0, limit=30)

    # Verifying that the returned data matches the API response.
    assert result == expected_data


def test_fetch_data_from_api_returns_none_on_http_error(monkeypatch):
    # Testing whether an HTTP error results in None without retrying.
    monkeypatch.setattr(api_client, "API_URL", "https://example.com")

    class MockResponse:
        # Simulating an unsuccessful HTTP status.
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("404 Not Found")

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(api_client.requests, "get", mock_get)

    result = api_client.fetch_data_from_api(skip=0, limit=30)

    # Verifying that the HTTP error is handled as implemented.
    assert result is None


def test_fetch_data_from_api_retries_after_timeout(monkeypatch):
    # Testing whether a timeout is retried and a later success is returned.
    monkeypatch.setattr(api_client, "API_URL", "https://example.com")

    expected_data = {"products": [{"id": 1}]}
    call_count = 0
    sleep_calls = []

    class MockResponse:
        # Simulating a successful response after the timeout.
        def raise_for_status(self):
            pass

        def json(self):
            return expected_data

    def mock_get(url, timeout):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            raise requests.exceptions.Timeout("Request timed out")

        return MockResponse()

    # Mocking sleep so the test does not wait during retry backoff.
    monkeypatch.setattr(api_client.requests, "get", mock_get)
    monkeypatch.setattr(api_client.time, "sleep", sleep_calls.append)

    result = api_client.fetch_data_from_api(
        skip=0,
        limit=30,
        max_retries=2,
    )

    # Verifying the second request succeeds and the first backoff is 2 seconds.
    assert result == expected_data
    assert call_count == 2
    assert sleep_calls == [2]


def test_fetch_data_from_api_returns_none_after_all_timeouts(monkeypatch):
    # Testing whether repeated timeouts eventually stop and return None.
    monkeypatch.setattr(api_client, "API_URL", "https://example.com")

    call_count = 0
    sleep_calls = []

    def mock_get(url, timeout):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("Request timed out")

    # Mocking sleep to avoid real delays during retry attempts.
    monkeypatch.setattr(api_client.requests, "get", mock_get)
    monkeypatch.setattr(api_client.time, "sleep", sleep_calls.append)

    result = api_client.fetch_data_from_api(
        skip=0,
        limit=30,
        max_retries=2,
    )

    # Verifying the initial request plus two retries are attempted.
    assert result is None
    assert call_count == 3
    assert sleep_calls == [2, 4]


def test_fetch_data_from_api_returns_none_on_invalid_json(monkeypatch):
    # Testing whether invalid JSON returned by the server is handled safely.
    monkeypatch.setattr(api_client, "API_URL", "https://example.com")

    class MockResponse:
        # Simulating a successful HTTP response with invalid JSON content.
        def raise_for_status(self):
            pass

        def json(self):
            raise requests.exceptions.JSONDecodeError(
                "Invalid JSON", "", 0
            )

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(api_client.requests, "get", mock_get)

    result = api_client.fetch_data_from_api(skip=0, limit=30)

    # Verifying that invalid JSON results in None.
    assert result is None


def test_fetch_all_products_collects_multiple_pages(monkeypatch):
    # Testing whether products from every valid page are collected.
    first_page = {
        "products": [{"id": 1}, {"id": 2}],
        "limit": 2,
        "skip": 0,
        "total": 3,
    }
    second_page = {
        "products": [{"id": 3}],
        "limit": 2,
        "skip": 2,
        "total": 3,
    }

    # Mocking the API function so no real network request is made.
    def mock_fetch_data_from_api(skip, limit):
        if skip == 0:
            return first_page
        if skip == 2:
            return second_page
        return None

    monkeypatch.setattr(
        api_client,
        "fetch_data_from_api",
        mock_fetch_data_from_api,
    )

    result = api_client.fetch_all_products()

    # Verifying that all three products are returned in page order.
    assert result == [
        {"id": 1},
        {"id": 2},
        {"id": 3},
    ]


def test_fetch_all_products_returns_products_from_one_page(monkeypatch):
    # Testing whether pagination stops when the first page contains all products.
    first_page = {
        "products": [{"id": 1}, {"id": 2}],
        "limit": 30,
        "skip": 0,
        "total": 2,
    }

    # Tracking calls to ensure that no additional page is requested.
    calls = []

    def mock_fetch_data_from_api(skip, limit):
        calls.append((skip, limit))
        return first_page

    monkeypatch.setattr(
        api_client,
        "fetch_data_from_api",
        mock_fetch_data_from_api,
    )

    result = api_client.fetch_all_products()

    # Verifying the products are returned and only the first page is fetched.
    assert result == [{"id": 1}, {"id": 2}]
    assert calls == [(0, 30)]


def test_fetch_all_products_stops_when_a_page_fails(monkeypatch):
    # Testing whether pagination stops and preserves collected products on failure.
    first_page = {
        "products": [{"id": 1}],
        "limit": 1,
        "skip": 0,
        "total": 2,
    }

    calls = []

    def mock_fetch_data_from_api(skip, limit):
        calls.append((skip, limit))

        if skip == 0:
            return first_page

        # Simulating a failed second page.
        return None

    monkeypatch.setattr(
        api_client,
        "fetch_data_from_api",
        mock_fetch_data_from_api,
    )

    result = api_client.fetch_all_products()

    # Verifying that collected products are retained when a later page fails.
    assert result == [{"id": 1}]
    assert calls == [(0, 30), (1, 1)]