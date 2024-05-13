from django.contrib import admin
from .models import Anime, UserAnime, UserFeature, AnimeRecommendation

admin.site.register(UserFeature)
admin.site.register(Anime)
admin.site.register(UserAnime)
admin.site.register(AnimeRecommendation)
