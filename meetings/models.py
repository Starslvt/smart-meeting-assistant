from django.db import models

# Create your models here.


class Meeting(models.Model):
    # Información básica
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='audios/')
    created_at = models.DateTimeField(auto_now_add=True)

    # Resultados de la IA
    transcription = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')

    #status del procesamiento obviamente duh
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('done', 'Completado'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title