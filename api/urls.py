from django.urls import path
from . import views

urlpatterns = [
    path('anime/', views.AnimesAPI.as_view()),
    path('auth/register/',views.UserRegister.as_view()),
    path('auth/login/', views.UserLogin.as_view()),
    path('get/user/', views.UserView.as_view()),
    path('auth/logout/', views.UserLogout.as_view()),
    path('authenticate/',views.IsAuthenticated.as_view()),
    path('anime/<int:id>/', views.AnimeDetail.as_view()),
    path('anime/add-collection/', views.AddUserAnime.as_view()),
    path('user/collection/', views.AddUserAnime.as_view()),
    path('anime-search/', views.AnimesSearchAPI.as_view()),
    path('anime/similar/', views.SimilarAnimes.as_view()),
    path('user/recommendations/', views.AnimeRecommendation.as_view()),
   ]
