import whisper
import requests
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json

def transcribe_audio(audio_path):
    try:
        print("Cargando modelo Whisper...")
        model = whisper.load_model("small")
        print(f"Transcribiendo: {audio_path}")
        result = model.transcribe(str(audio_path), language="es")
        return result["text"].strip()
    except Exception as e:
        print(f"Error en transcripción: {e}")
        return None


def generate_ai_analysis(text):
    try:
        prompt = (
            "Eres un asistente educativo experto. Analiza el siguiente texto de una clase o reunión.\n\n"
            "INSTRUCCIONES IMPORTANTES:\n"
            "- Responde ÚNICAMENTE con JSON válido, sin texto extra, sin markdown\n"
            "- Basa TODO el contenido EXCLUSIVAMENTE en lo que dice el texto\n"
            "- El resumen debe tener mínimo 4 oraciones completas y detalladas\n"
            "- Las ideas principales deben ser afirmaciones completas y específicas\n"
            "- El glosario debe contener términos que REALMENTE aparecen en el texto\n"
            "- Las preguntas deben poder responderse con información del texto\n"
            "- El puntaje debe variar según el contenido (entre 40 y 100)\n\n"
            "Responde con este JSON exacto:\n"
            "{\n"
            '  "resumen": "párrafo de mínimo 4 oraciones",\n'
            '  "ideas_principales": ["idea 1", "idea 2", "idea 3", "idea 4", "idea 5"],\n'
            '  "glosario": [\n'
            '    {"termino": "término del texto", "definicion": "definición basada en el texto"},\n'
            '    {"termino": "término 2", "definicion": "definición 2"},\n'
            '    {"termino": "término 3", "definicion": "definición 3"},\n'
            '    {"termino": "término 4", "definicion": "definición 4"}\n'
            '  ],\n'
            '  "preguntas": [\n'
            '    {"pregunta": "pregunta sobre el texto", "respuesta": "respuesta detallada"},\n'
            '    {"pregunta": "pregunta 2", "respuesta": "respuesta 2"},\n'
            '    {"pregunta": "pregunta 3", "respuesta": "respuesta 3"},\n'
            '    {"pregunta": "pregunta 4", "respuesta": "respuesta 4"},\n'
            '    {"pregunta": "pregunta 5", "respuesta": "respuesta 5"}\n'
            '  ],\n'
            '  "completitud": {"puntaje": 75, "justificacion": "explicación del puntaje"}\n'
            "}\n\n"
            f"Texto:\n{text}\n\n"
            "Responde SOLO con el JSON:"
        )

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            },
            timeout=180
        )

        if response.status_code == 200:
            raw = response.json()['response'].strip()
            if '```' in raw:
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start != -1 and end > start:
                raw = raw[start:end]
            data = json.loads(raw)
            return data
        else:
            return None

    except Exception as e:
        print(f"Error en análisis IA: {e}")
        return None


def generate_wordcloud(text):
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
        'grandes', 'distinto', 'distintos', 'fuente', 'principal', 'muchas',
        'poco', 'poca', 'pocos', 'pocas', 'cosa', 'cosas', 'parte',
        'estaba', 'están', 'están', 'estamos', 'estáis', 'están', 'será',
        'sí', 'algo', 'algunos', 'algunas', 'otro', 'otra', 'otros', 'otras',
    }
    try:
        wordcloud = WordCloud(
            width=800,
            height=350,
            background_color='white',
            stopwords=stopwords_es,
            max_words=20,
            colormap='plasma',
            prefer_horizontal=0.85,
            min_font_size=14,
            max_font_size=80,
            collocations=False,
        ).generate(text)

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