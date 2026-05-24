import whisper
import requests


def transcribe_audio(audio_path):
    """
    Transcribe un archivo de audio usando Whisper local.
    """
    try:
        print(f"Cargando modelo Whisper...")
        model = whisper.load_model("small")
        
        print(f"Transcribiendo: {audio_path}")
        result = model.transcribe(str(audio_path), language="es")
        
        return result["text"].strip()
    
    except Exception as e:
        print(f"Error en transcripción: {e}")
        return None


def generate_summary(text):
    """
    Genera un resumen usando Ollama local.
    """
    try:
        prompt = f"""Eres un asistente que resume reuniones y clases.
        
Analiza el siguiente texto y genera:
1. Un resumen conciso (3-5 oraciones)
2. Los puntos más importantes (máximo 5)
3. Si hay tareas o acciones mencionadas, listarlas

Texto:
{text}

Responde en español, de forma clara y organizada."""

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            result = result.replace('**', '')
            return result
        else:
            return None
            
    except Exception as e:
        print(f"Error generando resumen: {e}")
        return None

from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Importante: evita que matplotlib abra ventanas
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re

def generate_wordcloud(text):
    """
    Genera una nube de palabras y la devuelve como imagen base64
    para mostrarla directo en el HTML sin guardar archivos.
    """
    # Palabras vacías en español que no aportan valor visual
    stopwords_es = {
        'de', 'la', 'el', 'en', 'y', 'a', 'que', 'es', 'se', 'no',
        'un', 'una', 'los', 'las', 'del', 'al', 'lo', 'por', 'con',
        'para', 'su', 'sus', 'fue', 'son', 'pero', 'más', 'este',
        'esta', 'como', 'si', 'muy', 'ya', 'me', 'mi', 'te', 'le',
        'nos', 'les', 'hay', 'ser', 'has', 'han', 'era', 'uno',
        'eso', 'esto', 'esa', 'ese', 'también', 'después', 'donde',
        'cuando', 'sobre', 'entre', 'durante', 'todo', 'todos',
        'muchos', 'cada', 'vez', 'así', 'tan', 'bien', 'aquí', 
        'sino', 'vamos', 'hoy', 'casi', 'viene', 'cumple', 'sabe',
        'gente', 'mucha', 'tipo', 'rol', 'usa', 'hablar', 'buenas',
        'tardes', 'días', 'alguien', 'exacto', 'ejemplo', 'grande',
        'grandes', 'distinto', 'distintos', 'fuente', 'principal',
    }

    try:
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=stopwords_es,
            max_words=20,
            colormap='plasma',       # Colores vibrantes morado/naranja
            prefer_horizontal=0.8,
            min_font_size=14,
            max_font_size=90,   
            collocations=False,
        ).generate(text)

        # Convertir a imagen base64 para el template
        buffer = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
        plt.close()
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error generando nube de palabras: {e}")
        return None