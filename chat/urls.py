from django.urls import path

from chat import views

urlpatterns = [
    path('get_room/', views.ChatRoomView.as_view()),
]
