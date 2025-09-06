from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Configuración de Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi"  # Cambia según tu modelo

# Personalidades predefinidas
PERSONALITIES = {
    "ada": {
        "name": "Ada",
        "prompt": """Eres Ada, una asistente de laboratorio amigable y motivadora. 
        Hablas de manera informal pero profesional. 
        Siempre alientas a los estudiantes cuando tienen dudas.
        Usas analogías simples para explicar conceptos complejos."""
    },
    "dr_smith": {
        "name": "Dr. Smith",
        "prompt": """Eres el Dr. Smith, un profesor universitario riguroso pero justo.
        Hablas de manera formal y precisa.
        Corriges errores pero también reconoces el esfuerzo.
        Usas vocabulario académico apropiado."""
    },
    "luna": {
        "name": "Luna", 
        "prompt": """Eres Luna, una compañera de clase súper relajada.
        Usas mucho slang juvenil y emojis en tus respuestas.
        Haces bromas pero también te tomas en serio ayudar.
        A veces divagas pero siempre vuelves al tema."""
    },
    "mentor": {
        "name": "Mentor",
        "prompt": """Eres Mentor, un coach de desarrollo profesional.
        Te enfocas en objetivos y resultados medibles.
        Haces preguntas poderosas para guiar el aprendizaje.
        Siempre buscas el crecimiento del estudiante."""
    },
    "sofia": {
        "name": "Sofía",
        "prompt": """Eres Sofía, una filósofa práctica que conecta ideas profundas con la vida cotidiana.
        Hablas con calma y profundidad, pero siempre aterrizas los conceptos.
        A menudo citas a filósofos pero los explicas de forma accesible.
        Usas preguntas socráticas para guiar el pensamiento.
        Tu frase favorita es "Pero, ¿qué significa esto para ti?"
        Crees que la filosofía debe ser útil, no solo teórica."""
    }
}

# Historial de conversación (en memoria)
conversation_history = []

@app.route('/')
def index():
    """Sirve la página principal"""
    return render_template('index.html', personalities=PERSONALITIES)

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    try:
        data = request.json
        user_message = data.get('message', '')
        personality = data.get('personality', 'ada')
        
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Agregar mensaje del usuario al historial
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Construir el prompt con personalidad y contexto
        system_prompt = PERSONALITIES[personality]['prompt']
        
        # Crear el prompt completo con historial
        full_prompt = f"{system_prompt}\n\n"
        
        # Agregar historial reciente (últimos 10 mensajes)
        for msg in conversation_history[-10:]:
            role = "Usuario" if msg['role'] == 'user' else PERSONALITIES[personality]['name']
            full_prompt += f"{role}: {msg['content']}\n"
        
        full_prompt += f"{PERSONALITIES[personality]['name']}:"
        
        # Llamar a Ollama API
        response = requests.post(OLLAMA_API_URL, 
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            bot_response = response.json()['response']
            
            # Agregar respuesta del bot al historial
            conversation_history.append({
                'role': 'assistant',
                'content': bot_response
            })
            
            return jsonify({
                'response': bot_response,
                'personality_name': PERSONALITIES[personality]['name']
            })
        else:
            return jsonify({'error': 'Error al comunicarse con Ollama'}), 500
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """Limpia el historial de conversación"""
    global conversation_history
    conversation_history = []
    return jsonify({'message': 'Historial limpiado'})

if __name__ == '__main__':
    print("=== Chatbot Local con Personalidad ===")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Personalidades disponibles: {', '.join(PERSONALITIES.keys())}")
    print("\nAsegúrate de que Ollama esté ejecutándose (ollama serve)")
    print("\nIniciando servidor en http://localhost:5000")
    app.run(debug=True, port=5000)