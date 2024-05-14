from django.contrib import admin
from .models import Anime, UserAnime, UserFeature, AnimeRecommendation, UserAnimeRecommendation, AnimeScore

admin.site.register(UserFeature)
admin.site.register(Anime)
admin.site.register(UserAnime)
admin.site.register(AnimeRecommendation)
admin.site.register(UserAnimeRecommendation)
admin.site.register(AnimeScore)
