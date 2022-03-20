from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from storage_management.coordinator import views

router = routers.DefaultRouter()
router.register(r"areas", views.AreaViewSet)
router.register(r"spots", views.SpotViewSet)
router.register(r"members", views.MemberViewSet)
router.register(r"tickets", views.TicketViewSet)
router.register(r"notifications", views.NotificationViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
