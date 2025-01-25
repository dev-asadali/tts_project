import os
import random
import string
import torch
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from TTS.api import TTS

# Paths for uploads and outputs
UPLOAD_FOLDER = os.path.join(settings.BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(settings.BASE_DIR, 'media/audio')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Device for TTS
device = "cuda" if torch.cuda.is_available() else "cpu"

# Available TTS models and cache for loaded models
available_models = TTS().list_models()
loaded_models = {}

# Generate a random filename
def generate_random_name(length=8, extension=".wav"):
    return f"{''.join(random.choices(string.ascii_letters + string.digits, k=length))}{extension}"

# Get or load the TTS model
def get_tts_model(model_name):
    if model_name not in loaded_models:
        if model_name in available_models:
            loaded_models[model_name] = TTS(model_name, progress_bar=True).to(device)
        else:
            raise ValueError(f"Model '{model_name}' not found.")
    return loaded_models[model_name]

# Frontend page
def home(request):
    try:
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        tts_model = get_tts_model(model_name)
        speakers = tts_model.speakers if hasattr(tts_model, "speakers") else []
    except Exception as e:
        speakers = []

    return render(request, 'tts_app/index.html', {"speakers": speakers})

# Text-to-speech API
@csrf_exempt
def text_to_speech(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        speaker = request.POST.get("speaker", "")
        language = request.POST.get("language", "en")
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

        if not text:
            return JsonResponse({"error": "Text is required"}, status=400)

        try:
            tts_model = get_tts_model(model_name)
            output_filename = generate_random_name()
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            tts_model.tts_to_file(text=text, speaker=speaker, language=language, file_path=output_path)

            audio_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}audio/{output_filename}"
            return JsonResponse({"audio_url": audio_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# Voice cloning API
@csrf_exempt
def voice_clone(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        text = request.POST.get("text", "")
        language = request.POST.get("language", "en")

        if not audio_file or not text:
            return JsonResponse({"error": "Both audio file and text are required"}, status=400)

        file_path = os.path.join(UPLOAD_FOLDER, audio_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        try:
            tts_model = get_tts_model("tts_models/multilingual/multi-dataset/xtts_v2")
            output_filename = generate_random_name()
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            tts_model.tts_to_file(text=text, speaker_wav=file_path, language=language, file_path=output_path)

            audio_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}audio/{output_filename}"
            return JsonResponse({"audio_url": audio_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# List available TTS models
def list_models(request):
    return available_models