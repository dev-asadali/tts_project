from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Frontend page
    path("tts/", views.text_to_speech, name="text_to_speech"),
    path("voice_clone/", views.voice_clone, name="voice_clone"),
    path("models/", views.list_models, name="list_models"),
   ## path('speakers/', views.list_speakers, name='list_speakers'),  # New rout
]