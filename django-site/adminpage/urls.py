from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.showAdminPage),

    # Resource API
    path('add-resource/',    views.add_resource,    name='add_resource'),
    path('remove-resource/', views.remove_resource, name='remove_resource'),
    path('get-resources/',   views.get_resources,   name='get_resources'),

    # Reservation API
    path('make-reservation/',   views.make_reservation,   name='make_reservation'),
    path('cancel-reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('get-reservations/',   views.get_reservations,   name='get_reservations'),
]