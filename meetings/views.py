from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting
from .forms import MeetingForm
from .ai_services import transcribe_audio, generate_summary

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
            # Redirigir INMEDIATAMENTE sin procesar nada
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
    """El navegador llama a este endpoint para arrancar el procesamiento"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    meeting = get_object_or_404(Meeting, pk=pk)
    
    if meeting.status != 'pending':
        return JsonResponse({'status': meeting.status})
    
    meeting.status = 'processing'
    meeting.save()

    transcription = transcribe_audio(meeting.audio_file.path)

    if transcription:
        meeting.transcription = transcription
        summary = generate_summary(transcription)
        meeting.summary = summary if summary else "Ollama no disponible."
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
    return render(request, 'meetings/detail.html', {'meeting': meeting})