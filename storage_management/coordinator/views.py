from datetime import timedelta
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


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
    search_fields = ["name"]


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

    @action(detail=False)
    def check(self, request):
        for ticket in Ticket.objects.filter(finished_at=None):
            member = ticket.member
            print(f"MEMBER: {type(member)}")
            prior_notification_types = [
                notification.type
                for notification in Notification.objects.filter(ticket=ticket)
            ]
            if (
                timezone.now() + timedelta(hours=48) > ticket.expires_at
                and "48_UNTIL_EXPIRED" not in prior_notification_types
            ):
                pass
            if (
                timezone.now() + timedelta(hours=24) > ticket.expires_at
                and "24_UNTIL_EXPIRED" not in prior_notification_types
            ):
                pass
            if (
                timezone.now() > ticket.expires_at
                and "EXPIRED" not in prior_notification_types
            ):
                pass
            if (
                timezone.now() + timedelta(hours=48)
                > ticket.expires_at + timedelta(days=7)
                and "48_UNTIL_FORFEIT" not in prior_notification_types
            ):
                pass
            if (
                timezone.now() + timedelta(hours=24)
                > ticket.expires_at + timedelta(days=7)
                and "24_UNTIL_FORFEIT" not in prior_notification_types
            ):
                pass
            if (
                timezone.now() > ticket.expires_at + timedelta(days=7)
                and "FORFEIT" not in prior_notification_types
            ):
                pass

        return Response({})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows notifications to be viewed or edited.
    """

    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
