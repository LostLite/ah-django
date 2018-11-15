from django.urls import path

from .views import ( 
    schema_view,
    LoginAPIView, 
    RegistrationAPIView, 
    UserRetrieveUpdateAPIView,
    ArticleAPIView,
    CommentAPIView
)

urlpatterns = [
    path('user/<int:pk>', UserRetrieveUpdateAPIView.as_view()),
    path('users/registration/', RegistrationAPIView.as_view(), name="users-register"),
    path('users/login/', LoginAPIView.as_view(), name="auth-login"),
    path('articles/create/', ArticleAPIView.as_view(), name="articles-register"),
    path('articles/', ArticleAPIView.as_view(), name="articles-all"),
    path('articles/<int:pk>', ArticleAPIView.as_view(), name="articles-single"),
    path('articles/<int:pk>/comments/add', CommentAPIView.as_view(), name="article-comments-add"),
    path('articles/<int:pk>/comments/', CommentAPIView.as_view(), name="article-comments"),
    path('', schema_view)
]
