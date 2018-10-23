from django.urls import path

from .views import ( 
    schema_view,
    LoginAPIView, 
    RegistrationAPIView, 
    UserRetrieveUpdateAPIView
)

urlpatterns = [
    path('user/<int:pk>', UserRetrieveUpdateAPIView.as_view()),
    path('users/<int:pk>', RegistrationAPIView.as_view()),
    path('users/login/<int:pk>', LoginAPIView.as_view()),
    path('', schema_view)
]
