from base.models import Anime, AnimeRecommendation, UserAnime
from fuzzywuzzy import fuzz
from surprise.prediction_algorithms import SVD
from surprise import Reader
from surprise import Dataset
import pandas as pd

from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()
def UserRecommendationsAnalysis(user):
    # Load the dataset
    reader = Reader(rating_scale=(1, 10))
    user_rating_file = THIS_FOLDER / "user_rating.csv"

    collectedData = pd.read_csv(user_rating_file)
    currentUser = GetUserAnimesCollection(user, "watchlist")

    currentUser = currentUser.filter(rating__isnull=False)
    currentUser = currentUser.values_list('user', 'anime_id', 'rating')
    currentUser = pd.DataFrame(currentUser, columns=['user_id', 'anime_uid', 'User_rating'])
    collectedData = pd.concat([collectedData, currentUser], ignore_index=True)
    dataset = Dataset.load_from_df(collectedData, reader)
    trainset = dataset.build_full_trainset()
    # Train the model
    algo = SVD()
    algo.fit(trainset)
    predictions = []
    popular_animes = GetPopularunWatchedAnimes(user)
    for anime in popular_animes:
        pred = algo.predict(user.id, anime.id)
        predictions.append((anime, pred.est))
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:10]

def GetSimilarAnimes(animeId: str):
    selectedAnime = Anime.objects.get(id=animeId)
    # Check if AnimeRecommendation exists
    try:
        animeRecommendation = AnimeRecommendation.objects.get(anime=selectedAnime)
        considerated_animes = animeRecommendation.recommended_animes.all()
        available_recommendations = True
    except AnimeRecommendation.DoesNotExist:
        considerated_animes = list(Anime.objects.exclude(id=animeId))
        available_recommendations = False

    
    similar_animes = []

    for anime in considerated_animes:
        title_similarity_scores = fuzz.ratio(selectedAnime.title, anime.title)

        genre_similarity_scores = fuzz.token_sort_ratio(selectedAnime.genre, anime.genre)

        similar_animes.append((anime, title_similarity_scores + genre_similarity_scores))

    similar_animes.sort(key=lambda x: x[1], reverse=True)
    recommendations = similar_animes[:12]
    
    if not available_recommendations:
        # Store AnimeRecommendation
        animeRecommendation = AnimeRecommendation.objects.create(anime=selectedAnime)
        animeRecommendation.recommended_animes.set([anime[0] for anime in recommendations])
        animeRecommendation.save()
    return recommendations

def GetUserAnimesCollection(user, typeOfCollection="favourite"):
    userAnimeCollection = UserAnime.objects.filter(user=user, is_favorite=True) if typeOfCollection == "favourite" else UserAnime.objects.filter(user=user, is_watchlist=True)
    return userAnimeCollection

def GetUserCollectionStatus(user, animeId):
    try:
        userAnime = UserAnime.objects.get(user=user, anime=animeId)
        return {"is_favorite": userAnime.is_favorite, "is_watchlist": userAnime.is_watchlist}
    except:
        return {"is_favorite": False, "is_watchlist": False}
    
def GetPopularunWatchedAnimes(user):
    return Anime.objects.exclude(useranime__user=user).order_by('popularity')[:5000]