from django.contrib import admin
from .models import Anime, UserAnime, UserFeature

admin.site.register(UserFeature)
admin.site.register(Anime)
admin.site.register(UserAnime)

