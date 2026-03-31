# Tests

This directory contains tests for the Mergington High School Activities API.

## Running Tests

To run the tests, make sure you have the dependencies installed:

```bash
pip install -r requirements.txt
```

Then run the tests with pytest:

```bash
pytest tests/
```

## Test Coverage

The tests cover the following API endpoints:

- `GET /activities` - Retrieve all activities
- `POST /activities/{activity_name}/signup` - Sign up for an activity
- `POST /activities/{activity_name}/unregister` - Unregister from an activity
- `GET /` - Root redirect to static HTML

Tests include:
- Successful operations
- Error handling (non-existent activities, duplicate signups, etc.)
- Data validation
- HTTP status codes and response formats