from datetime import timedelta
from rich import inspect
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import (
    Area,
    Spot,
    Member,
    Ticket,
    Notification,
)
from .serializers import (
    AreaSerializer,
    SpotSerializer,
    MemberSerializer,
    TicketSerializer,
    NotificationSerializer,
)
from django.db.models import Q
from storage_management.settings import STORAGE_RULES


class AreaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows areas to be viewed or edited.
    """

    queryset = Area.objects.all().order_by("name")
    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated]


class SpotViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows spots to be viewed or edited.
    """

    queryset = Spot.objects.all().order_by("name")
    serializer_class = SpotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["area"]
    search_fields = ["=name"]

    @action(detail=False)
    def available(self, request):
        spots = Spot.objects.all().exclude(
            tickets__isnull=False, tickets__finished_at__isnull=True
        )
        serializer = SpotSerializer(spots, many=True, context={"request": request})
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows members to be viewed or edited.
    """

    queryset = Member.objects.all().order_by("name")
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]


class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tickets to be viewed or edited.
    """

    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["spot", "member"]

    def get_queryset(self):
        queryset = super().get_queryset()
        finished = self.request.query_params.get("finished")
        if finished == "true":
            queryset = queryset.exclude(finished_at__isnull=True)
        elif finished == "false":
            queryset = queryset.exclude(finished_at__isnull=False)
        return queryset

    @action(detail=True, methods=["post"], name="Close Ticket")
    def close(self, request, pk=None):
        ticket = self.get_object()
        member = get_object_or_404(Member, pk=ticket.member_id)

        if ticket.finished_at != None:
            return Response(
                {"error": "Ticket is already closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the ticket
        ticket_serializer = TicketSerializer(
            ticket,
            data={"finished_at": timezone.now()},  # set finished_at to current time
            partial=True,
            context={"request": request},
        )
        if not ticket_serializer.is_valid():
            return Response(
                ticket_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        ticket_serializer.save()

        # update member banned_until
        now = timezone.now()
        if ticket.expires_at > now:
            # 7 day ban, unused time refunded
            banned_until = now + STORAGE_RULES["timeout"] - (ticket.expires_at - now)
        elif ticket.expires_at + STORAGE_RULES["grace_period"] > now:
            # 14 day ban, no time refunded
            banned_until = now + STORAGE_RULES["short_ban"]
        else:
            # member should have already been automatically marked as banned by the cron job
            # something is weird if we got here
            return Response(status=status.HTTP_400_BAD_REQUEST)

        member_serializer = MemberSerializer(
            member,
            data={"banned_until": banned_until},
            partial=True,
            context={"request": request},
        )
        if not member_serializer.is_valid():
            return Response(
                member_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        member_serializer.save()

        return Response(ticket_serializer.data)

    @action(detail=False)
    def check(self, request):
        for ticket in Ticket.objects.filter(finished_at=None):
            member = ticket.member
            # todo: check against /member/create (lookupByRfid), in case their email address changed
            inspect(type(member), title="type(member)")
            prior_notification_types = [
                notification.type
                for notification in Notification.objects.filter(ticket=ticket)
            ]
            if (
                timezone.now() + timedelta(hours=48) > ticket.expires_at
                and "48_UNTIL_EXPIRED" not in prior_notification_types
            ):
                # Send notice: 48 hours remaining
                pass
            if (
                timezone.now() + timedelta(hours=24) > ticket.expires_at
                and "24_UNTIL_EXPIRED" not in prior_notification_types
            ):
                # Send notice: 24 hours remaining
                pass
            if (
                timezone.now() > ticket.expires_at
                and "EXPIRED" not in prior_notification_types
            ):
                # Send notice: Storage ticket expired
                pass
            if (
                timezone.now() + timedelta(hours=48)
                > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "48_UNTIL_FORFEIT" not in prior_notification_types
            ):
                # Send notice: 48 hours before items are forfeit and marked to be discarded
                pass
            if (
                timezone.now() + timedelta(hours=24)
                > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "24_UNTIL_FORFEIT" not in prior_notification_types
            ):
                # Send notice: 24 hours before items are forfeit and marked to be discarded
                pass
            if (
                timezone.now() > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "FORFEIT" not in prior_notification_types
            ):
                # Send notice: items are forfeit and marked to be discarded
                # Update member.banned_until to now + STORAGE_RULES['long_ban']
                # Update ticket.finished_at to now
                pass

        return Response({})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows notifications to be viewed or edited.
    """

    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
