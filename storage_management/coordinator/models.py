import uuid
from humanize import naturaldelta
from django.utils import timezone
from django.db import models
from .utils import seven_days


class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Spot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    area = models.ForeignKey(
        Area,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["area", "name"], name="unique_name")
        ]

    def __str__(self):
        return f"{self.area.name}.{self.name}"


class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    badge_id = models.CharField(max_length=50)
    banned_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=seven_days)
    finished_at = models.DateTimeField(null=True, blank=True)
    spot = models.ForeignKey(Spot, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member"],
                condition=models.Q(finished_at=None),
                name="unique_member",
            ),
            models.UniqueConstraint(
                fields=["spot"],
                condition=models.Q(finished_at=None),
                name="unique_spot",
            ),
        ]

    def __str__(self):
        return f"[{naturaldelta(timezone.now() - self.created_at)}] {self.member.name}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING)
    type = models.CharField(
        max_length=50,
        choices=[
            ("48_UNTIL_EXPIRED", "48_UNTIL_EXPIRED"),
            ("24_UNTIL_EXPIRED", "24_UNTIL_EXPIRED"),
            ("EXPIRED", "EXPIRED"),
            ("48_UNTIL_FORFEIT", "48_UNTIL_FORFEIT"),
            ("24_UNTIL_FORFEIT", "24_UNTIL_FORFEIT"),
            ("FORFEIT", "FORFEIT"),
        ],
    )

    def __str__(self):
        return f"[{self.created_at}] {self.ticket.member.name}"
