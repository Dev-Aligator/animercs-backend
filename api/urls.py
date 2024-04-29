from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/',views.UserRegister.as_view()),
    path('auth/login/', views.UserLogin.as_view()),
    path('get/user/', views.UserView.as_view()),
    path('auth/logout/', views.UserLogout.as_view()),
    path('authenticate/',views.IsAuthenticated.as_view()),
   ]
