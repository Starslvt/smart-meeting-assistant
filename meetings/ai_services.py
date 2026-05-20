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