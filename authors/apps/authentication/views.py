import jwt, json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger.views import get_swagger_view

from .models import Articles, Comments
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, ArticleSerializer, CommentSerializer
)

schema_view = get_swagger_view(title='Authors Haven API')

class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # send email on successful account registration
        send_mail(
            'Successful account registration with Authors Haven',
            'Welcome {}, you have successfully created an account with Authors Haven.'.format(serializer.data.get('username')),
            'noreply@author-heaven.com',
            ('{}'.format(serializer.data.get('email')),),
            fail_silently=True
        )

        # return token
        payload = {
            'id': serializer.data.get('id'),
            'email':serializer.data.get('email'),
            'username':serializer.data.get('username')
        }
        token = jwt.encode(payload, settings.SECRET_KEY).decode('utf-8')
        jwt_token = {'token': token}
        return Response(jwt_token, status=status.HTTP_201_CREATED)



class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        payload = {'email':serializer.data.get('email'), 'username':serializer.data.get('username')}

        return Response({'token':jwt.encode(payload, settings.SECRET_KEY).decode('utf-8')}, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class ArticleAPIView(APIView):
    # permission classes regulate the level of access to this resource
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # renderer classes determine how to render our error messages
    renderer_classes = (UserJSONRenderer,)

    # the serializer class determines how to serialize our data
    serializer_class = ArticleSerializer

    # test article creation
    def post(self, request):
        article = request.data.get('article',{})

        # register author
        article['author_id'] = request.user.id
        serializer = self.serializer_class(data=article)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response({'msg':'Article created successfully'}, status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        if pk is not None:
            articles_list = Articles.objects.get(pk=pk)
            # inform our serializer that we will be serializing a single article
            serialized = ArticleSerializer(articles_list)
        else:
            articles_list = Articles.objects.all()
            # inform our serializer that we will be serializing more than a single article
            serialized = ArticleSerializer(articles_list, many=True)

        # return a list of all registered articles
        return Response({'articles':serialized.data})

    def put(self, request, pk):
        data = request.data.get('article')

        article = Articles.objects.get(pk=pk)

        # pass partial to inform serializer that we want to update some fields but not necessarily all at once
        serializer = ArticleSerializer(instance=article, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response({'msg':'Article edited successfully'}, status.HTTP_200_OK)
 
    def delete(self, request, pk):
        # get article
        article = Articles.objects.get(pk=pk)

        # delete article
        article.delete()

        return Response({'msg':'Article deleted successfully'}, status.HTTP_204_NO_CONTENT)

class CommentAPIView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = CommentSerializer

    def post(self, request, pk):
        comment = request.data.get('comment',{})
        comment['author_id'] = request.user.id
        
        serializer = self.serializer_class(data=comment)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        
        return Response({'msg':'Comment added'}, status.HTTP_201_CREATED)

    
    def get(self, request, pk):
        
        # fetch parent article
        parent_article = get_object_or_404(Articles, pk=pk)

        # fetch comments
        comments = get_list_or_404(Comments, article=parent_article)
        
        # serialize objects
        serializer = self.serializer_class(comments, many=True)

        return Response({'comments':serializer.data})