from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import Anime, UserFeature, User
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserFeatureSerializer, AnimeSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from .csrfDessionAuthentication import CsrfExemptSessionAuthentication, BasicAuthentication
import numpy as np
import random



class AnimesAPI(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        all_animes_sorted_by_popularity = list(Anime.objects.order_by('popularity'))
        random_animes = random.sample(all_animes_sorted_by_popularity[:1000], 10)
        # Access anime entries using the random indices (converted to list)

        serializer = AnimeSerializer(random_animes, many=True)
        response_data = {
            'animes': serializer.data,
        }

        return Response(response_data)


class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	##
	def post(self, request):
		data = request.data
		assert validate_email(data)
		assert validate_password(data)
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.check_user(data)
			login(request, user)
			return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
	##g
    def get(self, request):
        serializer = UserSerializer(request.user)
        user = User.objects.get(username=request.user)
        userFeature = UserFeature.objects.get(user=user.id)
        userFeatureSerializer = UserFeatureSerializer(userFeature)
        return Response({'user': serializer.data, 'user_details' : userFeatureSerializer.data}, status=status.HTTP_200_OK)

class UpdateUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        try:
            userFeature = UserFeature.objects.get(user=request.user)
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        userFeature.firstName = data['firstName']
        userFeature.lastName = data['lastName']
        userFeature.photoUrl = data['photoUrl']
        userFeature.save()
        return Response(status=status.HTTP_200_OK)


class IsAuthenticated(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    def get(self, request):
        return Response({'authenticated': True}, status=status.HTTP_200_OK)


