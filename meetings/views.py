from django.shortcuts import render, redirect, get_object_or_404
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
            meeting.status = 'processing'
            meeting.save()
            
            audio_path = meeting.audio_file.path
            
            # Paso 1: Transcribir con Whisper
            transcription = transcribe_audio(audio_path)
            
            if transcription:
                meeting.transcription = transcription
                
                # Paso 2: Resumir con Ollama
                summary = generate_summary(transcription)
                if summary:
                    meeting.summary = summary
                    meeting.status = 'done'
                else:
                    meeting.summary = "Ollama no está disponible. Instalalo para obtener resúmenes."
                    meeting.status = 'done'
            else:
                meeting.transcription = "Error al transcribir el audio."
                meeting.status = 'error'
            
            meeting.save()
            return redirect('detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    
    return render(request, 'meetings/upload.html', {'form': form})

def detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings/detail.html', {'meeting': meeting})