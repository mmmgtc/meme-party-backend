from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import generics
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Meme, UserProfile, Tag
from .permissions import IsOwnerOrReadOnly
from .serializers import (LoginRequestSerializer, MemeSerializer,
                          TagSerializer, UserProfileSerializer, UserSerializer)
from .utils import verify_message

from collections import defaultdict

import datetime


class CustomAuthToken(ObtainAuthToken):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if verify_message(**serializer.validated_data):
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['address'])

            if created:  # User has been made for the first time
                UserProfile.objects.create(user=user,
                                           display_name=user.username)
            token, created = Token.objects.get_or_create(
                user=user)  # return existing token for now
            return Response({'token': token.key})

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UpvoteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Meme.objects.get(pk=pk)
        except Meme.DoesNotExist:
            raise Http404

    def post(self, request):

        meme = self.get_object(request.data['id'])
        userprofile = meme.poaster.userprofile

        if request.user in meme.upvoters.all():
            # Toggle Scenario
            meme.upvoters.remove(request.user)
            userprofile.karma -= 1

        else:
            # Fresh Upvote
            meme.upvoters.add(request.user)
            userprofile.karma += 1

        meme.upvotes = meme.upvoters.count()
        meme.save()
        userprofile.save()

        serializer = MemeSerializer(meme)

        return Response(serializer.data)


class DownvoteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Meme.objects.get(pk=pk)
        except Meme.DoesNotExist:
            raise Http404

    def post(self, request):

        meme = self.get_object(request.data['id'])
        userprofile = meme.poaster.userprofile

        if request.user in meme.downvoters.all():
            # Toggle Scenario
            meme.downvoters.remove(request.user)
            userprofile.karma += 1

        else:
            # Fresh Downvote
            meme.downvoters.add(request.user)
            userprofile.karma -= 1

        meme.downvotes = meme.downvoters.count()
        meme.save()
        userprofile.save()

        serializer = MemeSerializer(meme)

        return Response(serializer.data)


class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, address, format=None):
        poaster = User.objects.get(username=address)
        serializer = UserSerializer(poaster)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.userprofile
        if 'userprofile' in request.data:
            serializer = UserProfileSerializer(profile,
                                               request.data['userprofile'])
        else:
            serializer = UserProfileSerializer(profile, request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemeView(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Meme.objects.all()
    serializer_class = MemeSerializer


class MemeList(generics.ListCreateAPIView):
    queryset = Meme.objects.all()
    serializer_class = MemeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def list(self, request):
        # change queryset here as per discussion
        queryset = Meme.objects.all().order_by('-id')
        serializer = MemeSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(poaster=self.request.user)


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagMemeList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_tag(self, name):
        try:
            return Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            raise Http404

    def get(self, request, tag, format=None):
        # change queryset here as per discussion
        tag = self.get_tag(tag)
        queryset = tag.meme_set.all().order_by('-id')
        serializer = MemeSerializer(queryset, many=True)
        return Response(serializer.data)


class Search(generics.ListAPIView):
    authentication_classes = []
    serializer_class = MemeSerializer

    def get_queryset(self):
        queryset = Meme.objects.all()
        query = self.request.query_params.get('query')
        if query is not None:
            queryset = queryset.filter(title__search=query) | queryset.filter(
                description__search=query)
        return queryset


class UserMemeList(APIView):
    authentication_classes = []
    permission_classes = []

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, address, format=None):
        user = self.get_user(address)
        queryset = user.meme_set.all().order_by('-id')
        serializer = MemeSerializer(queryset, many=True)
        return Response(serializer.data)


class LeaderBoard(APIView):
    authentication_classes = []
    serializer_class = UserProfileSerializer

    def get_leaders(self, mins, number=10):
        # replace with a real aggregation of group by types
        date_from = datetime.datetime.now() - datetime.timedelta(minutes=mins)
        memes = Meme.objects.filter(created_at__gte=date_from)
        user_profiles = defaultdict(int)

        for meme in memes:
            user_profiles[
                meme.poaster.userprofile] += meme.upvotes - meme.downvotes

        ranked_list = []

        for user, karma in sorted(user_profiles.items(),
                                  key=lambda item: item[1],
                                  reverse=True):
            user.karma = karma
            ranked_list.append(user)

        return ranked_list[:number]

    def get(self, request, mins, format=None):
        queryset = self.get_leaders(mins)
        serializer = UserProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class Pagination(generics.ListAPIView):
    authentication_classes = []
    serializer_class = MemeSerializer

    def get_queryset(self):
        queryset = Meme.objects.all().order_by('-id')
        n = int(self.request.query_params.get('n', 25))
        latest = self.request.query_params.get('latest', None)
        oldest = self.request.query_params.get('oldest', None)

        if latest is None:
            return queryset[:n]

        latest, oldest = int(latest), int(oldest)
        # excluding the boundaries
        new_memes = queryset.filter(id__gt=latest).order_by('id')[:n]

        if len(new_memes) == n:
            return reversed(new_memes)

        num_old_memes_to_fetch = n - len(new_memes)
        old_memes = queryset.filter(
            id__lt=oldest).order_by('-id')[:num_old_memes_to_fetch]
        combined_memes = old_memes | new_memes

        return combined_memes.order_by('-id')
