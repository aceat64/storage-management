from datetime import timedelta
from django.utils import timezone


def seven_days():
    return timezone.now() + timedelta(days=7)
