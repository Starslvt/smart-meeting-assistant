from django.db import models

class Meeting(models.Model):
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='audios/')
    created_at = models.DateTimeField(auto_now_add=True)

    transcription = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    wordcloud_image = models.TextField(blank=True, default='')

    # Nuevos campos
    ideas_principales = models.TextField(blank=True, default='')
    glosario = models.TextField(blank=True, default='')
    preguntas = models.TextField(blank=True, default='')
    completitud_puntaje = models.IntegerField(default=0)
    completitud_justificacion = models.TextField(blank=True, default='')

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('done', 'Completado'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title