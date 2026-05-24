from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting
from .forms import MeetingForm
from .ai_services import transcribe_audio, generate_ai_analysis, generate_wordcloud
import json

def home(request):
    meetings = Meeting.objects.all().order_by('-created_at')
    return render(request, 'meetings/home.html', {'meetings': meetings})

def upload(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST, request.FILES)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.status = 'pending'
            meeting.save()
            return redirect('processing', pk=meeting.pk)
    else:
        form = MeetingForm()
    return render(request, 'meetings/upload.html', {'form': form})

def processing(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if meeting.status in ['done', 'error']:
        return redirect('detail', pk=pk)
    return render(request, 'meetings/processing.html', {'meeting': meeting})

@csrf_exempt
def process_meeting(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    meeting = get_object_or_404(Meeting, pk=pk)

    if meeting.status != 'pending':
        return JsonResponse({'status': meeting.status})

    meeting.status = 'processing'
    meeting.save()

    # Paso 1: Transcribir
    transcription = transcribe_audio(meeting.audio_file.path)

    if transcription:
        meeting.transcription = transcription

        # Paso 2: Análisis completo con IA
        analysis = generate_ai_analysis(transcription)

        if analysis:
            meeting.summary = analysis.get('resumen', '')
            meeting.ideas_principales = json.dumps(
                analysis.get('ideas_principales', []), ensure_ascii=False
            )
            meeting.glosario = json.dumps(
                analysis.get('glosario', []), ensure_ascii=False
            )
            meeting.preguntas = json.dumps(
                analysis.get('preguntas', []), ensure_ascii=False
            )
            completitud = analysis.get('completitud', {})
            meeting.completitud_puntaje = completitud.get('puntaje', 0)
            meeting.completitud_justificacion = completitud.get('justificacion', '')
        else:
            meeting.summary = "Ollama no disponible."

        # Paso 3: Nube de palabras
        wordcloud_img = generate_wordcloud(transcription)
        meeting.wordcloud_image = wordcloud_img if wordcloud_img else ''

        meeting.status = 'done'
    else:
        meeting.transcription = "Error al transcribir."
        meeting.status = 'error'

    meeting.save()
    return JsonResponse({'status': meeting.status, 'done': True})

def check_status(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return JsonResponse({
        'status': meeting.status,
        'done': meeting.status in ['done', 'error']
    })

def detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)

    # Parsear los campos JSON para el template
    try:
        ideas = json.loads(meeting.ideas_principales) if meeting.ideas_principales else []
    except:
        ideas = []
    try:
        glosario = json.loads(meeting.glosario) if meeting.glosario else []
    except:
        glosario = []
    try:
        preguntas = json.loads(meeting.preguntas) if meeting.preguntas else []
    except:
        preguntas = []

    return render(request, 'meetings/detail.html', {
        'meeting': meeting,
        'ideas': ideas,
        'glosario': glosario,
        'preguntas': preguntas,
    })