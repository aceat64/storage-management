from datetime import timedelta
from django.utils import timezone


def seven_days():
    return timezone.now() + timedelta(days=7)


def mock_members(id: int):
    if id % 2 == 0:
        accessGranted = True
    else:
        accessGranted = False
    return {
        "accessGranted": accessGranted,
        "user": {"fullName": f"Test User {id}", "email": f"testuser{id}@test.test"},
    }
