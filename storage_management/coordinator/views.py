from datetime import timedelta
from django.core.mail import send_mail, send_mass_mail
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import logging
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
from storage_management.settings import STORAGE_RULES
from .utils import pretty_datetime


logger = logging.getLogger(__name__)


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

        # send confirmation email
        msg = f"You have signed out of project storage spot {ticket.spot.name}. You can use project storage again after {pretty_datetime(banned_until)}."
        send_mail("[DMS Storage] Spot Reserved", msg, None, [ticket.member.email])

        return Response(ticket_serializer.data)

    @action(detail=False)
    def check(self, request):
        messages = ()
        for ticket in Ticket.objects.filter(finished_at=None):
            # todo: check against /member/create (lookupByRfid), in case their email address changed
            prior_notification_types = [
                notification.type
                for notification in Notification.objects.filter(ticket=ticket)
            ]

            if (
                timezone.now() + timedelta(hours=48) > ticket.expires_at
                and "48_UNTIL_EXPIRED" not in prior_notification_types
            ):
                # Send notice: 48 hours remaining
                msg = f"Your storage spot ({ticket.spot.name}) will expire at {pretty_datetime(ticket.expires_at)}. Please remove your items and signout of the storage spot before that time."
                messages += (
                    ("[DMS Storage] 48 Hour Notice", msg, None, [ticket.member.email]),
                )

            if (
                timezone.now() + timedelta(hours=24) > ticket.expires_at
                and "24_UNTIL_EXPIRED" not in prior_notification_types
            ):
                # Send notice: 24 hours remaining
                msg = f"Your storage spot ({ticket.spot.name}) will expire at {pretty_datetime(ticket.expires_at)}. Please remove your items and signout of the storage spot before that time or you will be temporarilly blocked from using project storage."
                messages += (
                    ("[DMS Storage] 24 Hour Notice", msg, None, [ticket.member.email]),
                )

            if (
                timezone.now() > ticket.expires_at
                and "EXPIRED" not in prior_notification_types
            ):
                # Send notice: Storage ticket expired
                msg = f"Your storage spot ({ticket.spot.name}) HAS EXPIRED as of {pretty_datetime(ticket.expires_at)}. Please remove your items and signout of the storage spot as soon as possible."
                messages += (
                    (
                        "[DMS Storage] Storage Spot EXPIRED",
                        msg,
                        None,
                        [ticket.member.email],
                    ),
                )

            if (
                timezone.now() + timedelta(hours=48)
                > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "48_UNTIL_FORFEIT" not in prior_notification_types
            ):
                # Send notice: 48 hours before items are forfeit and marked to be discarded
                msg = f"Your storage spot ({ticket.spot.name}) expired {pretty_datetime(ticket.expires_at)}. If you do not remove your items and signout of the storage spot your property will be discarded and you will be banned from using storage for 90 days."
                messages += (
                    (
                        "[DMS Storage] 48 Hour Notice - Property Forfeiture",
                        msg,
                        None,
                        [ticket.member.email],
                    ),
                )

            if (
                timezone.now() + timedelta(hours=24)
                > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "24_UNTIL_FORFEIT" not in prior_notification_types
            ):
                # Send notice: 24 hours before items are forfeit and marked to be discarded
                msg = f"Your storage spot ({ticket.spot.name}) expired {pretty_datetime(ticket.expires_at)}. If you do not remove your items and signout of the storage spot your property will be discarded and you will be banned from using storage for 90 days."
                messages += (
                    (
                        "[DMS Storage] 24 Hour Notice - Property Forfeiture",
                        msg,
                        None,
                        [ticket.member.email],
                    ),
                )

            if (
                timezone.now() > ticket.expires_at + STORAGE_RULES["grace_period"]
                and "FORFEIT" not in prior_notification_types
            ):
                # Send notice: items are forfeit and marked to be discarded
                msg = f"Your storage spot ({ticket.spot.name}) expired {pretty_datetime(ticket.expires_at)}. Multiple notices have been sent, your property has been tagged to be discarded and you are banned from using project storage again for 90 days."
                messages += (
                    (
                        "[DMS Storage] Final Notice - Property Forfeiture",
                        msg,
                        None,
                        [ticket.member.email],
                    ),
                )

                # Update member.banned_until to now + STORAGE_RULES['long_ban']
                member_serializer = MemberSerializer(
                    ticket.member,
                    data={"banned_until": timezone.now() + STORAGE_RULES["long_ban"]},
                    partial=True,
                    context={"request": request},
                )
                if not member_serializer.is_valid():
                    logger.warning(
                        f"Unable to update banned_until for member {ticket.member.id}"
                    )
                    logger.warning(member_serializer)
                member_serializer.save()

                # Update ticket.finished_at to now
                ticket_serializer = TicketSerializer(
                    ticket,
                    data={"finished_at": timezone.now()},
                    partial=True,
                    context={"request": request},
                )
                if not ticket_serializer.is_valid():
                    logger.warning(
                        f"Unable to update finished_at for ticket {ticket.id}"
                    )
                    logger.warning(ticket_serializer)
                ticket_serializer.save()

        send_mass_mail(messages)
        return Response({})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows notifications to be viewed or edited.
    """

    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
