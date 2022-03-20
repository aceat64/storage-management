from django.contrib import admin
from .models import (
    Area,
    Spot,
    Member,
    Ticket,
    Notification,
)

admin.site.register(Area)
admin.site.register(Spot)
admin.site.register(Member)
admin.site.register(Ticket)
admin.site.register(Notification)
