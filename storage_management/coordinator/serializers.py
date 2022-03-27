from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.utils import timezone
from .utils import mock_members, pretty_datetime

import requests

from storage_management.settings import MOCK_MEMBERS, RFID_LOOKUP_URL
from .models import (
    Area,
    Spot,
    Member,
    Ticket,
    Notification,
)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "url", "name"]


class SpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spot
        fields = ["id", "url", "name", "area"]


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "url", "name", "email", "badge_id", "banned_until"]
        read_only_fields = ["name", "email"]

    def create(self, validated_data):
        """
        Lookup space member by rfid and upsert our local member record.
        """
        badge_id = validated_data.get("badge_id")
        if MOCK_MEMBERS:
            result = mock_members(int(badge_id))
        else:
            r = requests.post(RFID_LOOKUP_URL, data={"rfid": badge_id})
            r.raise_for_status()
            result = r.json().get("result", {})
        access_granted = result.get("accessGranted", None)
        user = result.get("user", {})
        name = user.get("fullName", None)
        email = user.get("email", None)
        if not access_granted:
            raise PermissionDenied()
        queryset = Member.objects.filter(badge_id=badge_id)
        if queryset.exists():
            member = queryset.first()
            if member.name == name and member.email == email:
                return member
            member.badge_id = f"#{member.badge_id}"
            member.save()
        member = Member(name=name, email=email, badge_id=badge_id)
        member.save()
        return member


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "url",
            "created_at",
            "expires_at",
            "finished_at",
            "spot",
            "member",
        ]

    def validate_spot(self, spot):
        spot_ticket_open = Ticket.objects.filter(spot=spot, finished_at=None)
        if spot_ticket_open.exists():
            raise ValidationError(f"Spot '{spot}' is in use!")
        return spot

    def validate_member(self, member):
        if member.banned_until:
            if member.banned_until > timezone.now():
                raise ValidationError(
                    f"Member '{member}' is banned until '{member.banned_until}'"
                )
        member_ticket_open = Ticket.objects.filter(member=member, finished_at=None)
        if member_ticket_open.exists():
            spot = member_ticket_open.first().spot
            raise ValidationError(f"Member '{member}' has spot '{spot}' in use!")
        return member

    def create(self, validated_data):
        ticket = Ticket(**validated_data)
        ticket.save()

        # send confirmation email
        msg = f"Your project storage spot ({ticket.spot.name}) has been reserved. This spot is yours until {pretty_datetime(ticket.expires_at)}."
        send_mail("[DMS Storage] Spot Reserved", msg, None, [ticket.member.email])

        return ticket


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "url",
            "created_at",
            "ticket",
            "type",
        ]
