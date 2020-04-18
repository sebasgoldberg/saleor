from django.urls import path

from . import views

urlpatterns = [
    path('notification/<int:order_id>/<str:secret>/', views.notification),
]
