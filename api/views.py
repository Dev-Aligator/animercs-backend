from rest_framework.response import Response, responses
from rest_framework.decorators import api_view
from base.models import Anime, UserFeature, User, UserAnime, UserAnimeRecommendation, AnimeScore
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserFeatureSerializer, AnimeSerializer
from .services import GetSimilarAnimes, GetUserAnimesCollection, GetUserCollectionStatus
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
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        shuffle = int(request.query_params.get('shuffle', 1))
        pageIndex = 24*(page - 1)

        # If user is anonymous or has no favorite animes, return random animes
        if request.user.is_anonymous or not UserAnime.objects.filter(user=request.user, is_favorite=True).exists():
            returned_animes = Anime.objects.order_by('?')[pageIndex:pageIndex+24]
            serializer = AnimeSerializer(returned_animes, many=True)
            return Response({'animes': serializer.data})

        # Check if UserAnimeRecommendation exists for the user
        user_recommendations = UserAnimeRecommendation.objects.filter(user=request.user).first()
        if user_recommendations:
            # If recommendations exist, use them
            recommended_animes = AnimeScore.objects.filter(user_anime_recommendation=user_recommendations)
            if shuffle:
                for anime_score in recommended_animes:
                    anime_score.score += random.uniform(-30, 30)
            similar_animes = [(anime_score.anime, anime_score.score) for anime_score in recommended_animes]
            remaining_animes = Anime.objects.exclude(id__in=[anime_score.anime.id for anime_score in recommended_animes])
        else:
            # If recommendations do not exist, calculate them
            user_favorite_anime = GetUserAnimesCollection(request.user)
            user_favorite_titles = [entry.anime.title for entry in user_favorite_anime]
            user_favorite_genres = [entry.anime.genre for entry in user_favorite_anime]

            all_animes = list(Anime.objects.order_by('popularity'))
            similar_animes = self.calculate_similarity(all_animes[:1000], user_favorite_titles, user_favorite_genres)

            # Create a new UserAnimeRecommendation instance and save it to the database
            new_recommendation = UserAnimeRecommendation.objects.create(user=request.user)

            for anime, score in similar_animes[:100]:
                AnimeScore.objects.create(anime=anime, score=score, user_anime_recommendation=new_recommendation)
                new_recommendation.recommended_animes.add(anime)

            remaining_animes = all_animes[1000:]

        similar_animes.sort(key=lambda x: x[1], reverse=True)
        similar_animes = [anime[0] for anime in similar_animes]
        similar_animes += remaining_animes
        returned_similar_animes = similar_animes[pageIndex:pageIndex+24]

        serializer = AnimeSerializer(returned_similar_animes, many=True)
        return Response({'animes': serializer.data})

    def calculate_similarity(self, animes, user_favorite_titles, user_favorite_genres):
        similar_animes = []
        for anime in animes:
            title_similarity_scores = [fuzz.ratio(title, anime.title) for title in user_favorite_titles]
            title_average_similarity = sum(title_similarity_scores) / ( len(title_similarity_scores) + 0.01)

            genre_similarity_scores = [fuzz.token_sort_ratio(genre, anime.genre) for genre in user_favorite_genres]
            genre_average_similarity = sum(genre_similarity_scores) / ( len(genre_similarity_scores) + 0.01 )

            similar_animes.append((anime, title_average_similarity + genre_average_similarity))

        return similar_animes
    
    

class AnimeDetail(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        anime = Anime.objects.get(id=id)
        serializer = AnimeSerializer(anime)
        is_favorite, is_watchlist = GetUserCollectionStatus(request.user, id).values()
        response_data = {
            'anime': serializer.data,
            'is_favorite': is_favorite,
            'is_watchlist': is_watchlist
        }
        print(is_watchlist)
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
    
class SimilarAnimes(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        id = request.query_params.get('id', '')
        similarAnimeSerializer = AnimeSerializer([anime[0] for anime in GetSimilarAnimes(id) if anime[1] > 90], many=True)
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
            userAnimeCollection.is_favorite = not userAnimeCollection.is_favorite 
            action = "Adding" if userAnimeCollection.is_favorite else "Removing"
        elif typeOfCollection == "watchlist":
            userAnimeCollection.is_watchlist = not userAnimeCollection.is_watchlist
            action = "Adding" if userAnimeCollection.is_watchlist else "Removing"
        userAnimeCollection.save()

        response_data = {
            'action': action,
        }
        return Response(response_data, status=status.HTTP_200_OK)

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


