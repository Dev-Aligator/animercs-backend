from rest_framework.response import Response, responses
from rest_framework.decorators import api_view
from base.models import Anime, UserFeature, User, UserAnime
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserFeatureSerializer, AnimeSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from .csrfDessionAuthentication import CsrfExemptSessionAuthentication, BasicAuthentication
import numpy as np
import random
from fuzzywuzzy import fuzz


all_animes_sorted_by_popularity = list(Anime.objects.order_by('popularity'))
top_1000_animes = all_animes_sorted_by_popularity[:1000]
rest_of_animes = all_animes_sorted_by_popularity[1000:]
random.shuffle(top_1000_animes)
random_animes = top_1000_animes + rest_of_animes
class AnimesAPI(APIView):
    global random_animes
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        pageIndex = 24*(page - 1)
        if request.user.is_anonymous or UserAnime.objects.filter(user=request.user, is_favorite=True).count() == 0:
            returned_animes = random_animes[pageIndex:pageIndex+24]
            serializer = AnimeSerializer(returned_animes, many=True)
            response_data = {
                'animes': serializer.data,
            }
            return Response(response_data)

        user_favorite_anime = UserAnime.objects.filter(user=request.user, is_favorite=True)
        user_favorite_titles = [entry.anime.title for entry in user_favorite_anime]
        user_favorite_genres = [entry.anime.genre for entry in user_favorite_anime]

        all_animes = Anime.objects.all()
        similar_animes = []

        for anime in all_animes:
            title_similarity_scores = [fuzz.ratio(title, anime.title) for title in user_favorite_titles]
            title_average_similarity = sum(title_similarity_scores) / ( len(title_similarity_scores) + 0.01)

            genre_similarity_scores = [fuzz.token_sort_ratio(genre, anime.genre) for genre in user_favorite_genres]
            genre_average_similarity = sum(genre_similarity_scores) / ( len(genre_similarity_scores) + 0.01 )
            # Add a small noise to the average similarity
            noise = random.uniform(-0.5, 0.5)  # Adjust the range of noise as needed
            similar_animes.append((anime, title_average_similarity + genre_average_similarity + noise))

        similar_animes.sort(key=lambda x: x[1], reverse=True)
        returned_similar_animes = similar_animes[pageIndex:pageIndex+24]

        serializer = AnimeSerializer([anime[0] for anime in returned_similar_animes], many=True)
        response_data = {
            'animes': serializer.data,
        }

        return Response(response_data)

class AnimeDetail(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        anime = Anime.objects.get(id=id)
        serializer = AnimeSerializer(anime)
        response_data = {
            'anime': serializer.data,
        }

        return Response(response_data)

class AnimesSearchAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        search_text = request.query_params.get('keyword', '')

        all_animes = Anime.objects.all()
        similar_animes = []

        min_similarity_threshold = 70  # Adjust as needed

        for anime in all_animes:
            similarity_score = fuzz.partial_ratio(anime.title.lower(), search_text.lower())
            if similarity_score >= min_similarity_threshold:
                similar_animes.append((anime, similarity_score))

        similar_animes.sort(key=lambda x: x[1], reverse=True)
        top_similar_animes = similar_animes[:20]

        serializer = AnimeSerializer([anime[0] for anime in top_similar_animes if anime[1] > min_similarity_threshold], many=True)
        response_data = {
            'animes': serializer.data,
        }

        return Response(response_data)
    
def getSimilarAnimes(animeId: str):
    selectedAnime = Anime.objects.get(id=animeId)
 
    all_animes = Anime.objects.exclude(id=animeId)
    similar_animes = []

    for anime in all_animes:
        title_similarity_scores = fuzz.ratio(selectedAnime.title, anime.title)

        genre_similarity_scores = fuzz.token_sort_ratio(selectedAnime.genre, anime.genre)

        similar_animes.append((anime, title_similarity_scores + genre_similarity_scores))

    similar_animes.sort(key=lambda x: x[1], reverse=True)
    return similar_animes[:12]

class SimilarAnimes(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        id = request.query_params.get('id', '')
        similarAnimeSerializer = AnimeSerializer([anime[0] for anime in getSimilarAnimes(id) if anime[1] > 90], many=True)
        response_data = {
            'similar_animes': similarAnimeSerializer.data,
        }

        return Response(response_data)

class AddUserAnime(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


    def post(self, request):
        data = request.data
        selectedAnime = Anime.objects.get(id=data["animeId"])
        try:
            userAnimeCollection = UserAnime.objects.get(user=request.user, anime=selectedAnime)
        except:
            userAnimeCollection = UserAnime.objects.create(user=request.user, anime=selectedAnime)
        typeOfCollection = data['typeOfCollection']
        if typeOfCollection == "favorite":
            userAnimeCollection.is_favorite = True
        elif typeOfCollection == "watchlist":
            userAnimeCollection.is_watchlist = True
        userAnimeCollection.save()

        return Response(status=status.HTTP_200_OK)

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


