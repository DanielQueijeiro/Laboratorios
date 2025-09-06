from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
from datetime import datetime
import requests


app = Flask(__name__)
CORS(app)

# ============ HERRAMIENTA: CALCULADORA ============
def calculator(operation, a, b):
    """Calculadora simple con operaciones básicas"""
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else "Error: División por cero"
    }
    
    if operation in operations:
        return operations[operation](a, b)
    return f"Operación '{operation}' no soportada"

# ============ HERRAMIENTA: CLIMA ============
def weather_tool(city):
    """Simulador de clima (en producción usarías una API real)"""
    # Datos simulados para demostración
    cities_data = {
        'madrid': {'temp': 22, 'condition': 'Soleado', 'humidity': 45},
        'barcelona': {'temp': 24, 'condition': 'Parcialmente nublado', 'humidity': 65},
        'mexico': {'temp': 28, 'condition': 'Lluvioso', 'humidity': 80},
        'new york': {'temp': 18, 'condition': 'Nublado', 'humidity': 70},
        'tokyo': {'temp': 20, 'condition': 'Despejado', 'humidity': 55}
    }
    
    city_lower = city.lower()
    
    # Si la ciudad está en nuestros datos, usarla
    if city_lower in cities_data:
        data = cities_data[city_lower]
    else:
        # Generar datos aleatorios para ciudades desconocidas
        data = {
            'temp': random.randint(15, 35),
            'condition': random.choice(['Soleado', 'Nublado', 'Lluvioso', 'Despejado']),
            'humidity': random.randint(40, 90)
        }
    
    return {
        'city': city,
        'temperature': f"{data['temp']}°C",
        'condition': data['condition'],
        'humidity': f"{data['humidity']}%",
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ============ HERRAMIENTA: PROCESADOR DE TEXTO ============
def text_processor(text, operation):
    """Procesador de texto con varias operaciones"""
    operations = {
        'uppercase': lambda t: t.upper(),
        'lowercase': lambda t: t.lower(),
        'reverse': lambda t: t[::-1],
        'count_words': lambda t: f"{len(t.split())} palabras",
        'count_chars': lambda t: f"{len(t)} caracteres"
    }
    
    if operation in operations:
        return {
            'original': text,
            'result': operations[operation](text),
            'operation': operation
        }
    
    return f"Operación '{operation}' no soportada"

# ============ DECISOR INTELIGENTE ============
def decide_and_execute(message):
    """Decide qué herramienta usar basándose en el mensaje"""
    message_lower = message.lower()
    
    # Patrones para calculadora
    math_keywords = ['suma', 'sumar', 'más', '+', 'resta', 'restar', 'menos', '-',
                    'multiplica', 'multiplicar', 'por', '×', '*',
                    'divide', 'dividir', 'entre', '÷', '/']
    
    # Patrones para clima
    weather_keywords = ['clima', 'tiempo', 'temperatura', 'weather', 'llueve', 'sol']
    
    # Patrones para texto
    text_keywords = ['mayúscula', 'minúscula', 'reversa', 'voltear', 'contar', 'palabras']
    
    # Decidir herramienta
    if any(keyword in message_lower for keyword in math_keywords):
        # Extraer números del mensaje
        import re
        numbers = re.findall(r'-?\d+\.?\d*', message)
        if len(numbers) >= 2:
            a, b = float(numbers[0]), float(numbers[1])
            
            # Determinar operación
            if any(k in message_lower for k in ['suma', 'sumar', 'más', '+']):
                operation = 'add'
            elif any(k in message_lower for k in ['resta', 'restar', 'menos', '-']):
                operation = 'subtract'
            elif any(k in message_lower for k in ['multiplica', 'multiplicar', 'por', '×', '*']):
                operation = 'multiply'
            elif any(k in message_lower for k in ['divide', 'dividir', 'entre', '÷', '/']):
                operation = 'divide'
            else:
                operation = 'add'  # default
            
            result = calculator(operation, a, b)
            return {
                'tool_used': 'calculator',
                'parameters': {'operation': operation, 'a': a, 'b': b},
                'result': result,
                'response': f"He usado la calculadora: {a} {operation} {b} = {result}"
            }
    
    elif any(keyword in message_lower for keyword in weather_keywords):
        # Buscar nombre de ciudad (simplificado)
        cities = ['madrid', 'barcelona', 'mexico', 'new york', 'tokyo', 'paris', 'london']
        city = 'Madrid'  # default
        for c in cities:
            if c in message_lower:
                city = c.title()
                break
        
        result = weather_tool(city)
        return {
            'tool_used': 'weather',
            'parameters': {'city': city},
            'result': result,
            'response': f"El clima en {city}: {result['temperature']}, {result['condition']}, Humedad: {result['humidity']}"
        }
    
    elif any(keyword in message_lower for keyword in text_keywords):
        # Extraer texto entre comillas si existe
        import re
        quoted = re.findall(r'"([^"]*)"', message)
        text = quoted[0] if quoted else message
        
        # Determinar operación
        if 'mayúscula' in message_lower:
            operation = 'uppercase'
        elif 'minúscula' in message_lower:
            operation = 'lowercase'
        elif 'reversa' in message_lower or 'voltear' in message_lower:
            operation = 'reverse'
        elif 'contar' in message_lower and 'palabra' in message_lower:
            operation = 'count_words'
        else:
            operation = 'count_chars'
        
        result = text_processor(text, operation)
        return {
            'tool_used': 'text_processor',
            'parameters': {'text': text, 'operation': operation},
            'result': result,
            'response': f"Texto procesado: {result['result']}"
        }
    
    # Si no se detecta ninguna herramienta
    return {
        'tool_used': None,
        'result': None,
        'response': "No pude identificar qué herramienta usar. Puedo ayudarte con: cálculos matemáticos, información del clima, o procesamiento de texto."
    }

# ============ DECISIÓN CON LLM REAL ============
def decide_with_ollama(message):
    """Usa Ollama para decidir inteligentemente qué herramienta usar"""
    
    # Crear prompt estructurado para el LLM
    system_prompt = """Eres un asistente que decide qué herramienta usar.

HERRAMIENTAS DISPONIBLES:
- calculator: para matemáticas (suma, resta, multiplicación, división)
- weather: para información del clima de ciudades
- text_processor: para procesar texto (mayúsculas, minúsculas, reversa, contar)

INSTRUCCIONES:
- Responde SOLO con el nombre de la herramienta
- Si no necesitas herramienta, responde "none"
- Ejemplos:
  * "¿Cuánto es 5+3?" → calculator
  * "Clima en Madrid" → weather
  * "Convierte a mayúsculas" → text_processor
  * "¿Quién es Shakespeare?" → none

Usuario: """ + message + "\nHerramienta:"

    try:
        # Llamar a Ollama API
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'phi',
                'prompt': system_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,  # Más determinístico
                    'top_p': 0.9,
                    'num_predict': 20    # Respuesta corta
                }
            },
            timeout=150
        )
        
        if response.status_code == 200:
            llm_response = response.json()['response'].strip().lower()
            print(f"🤖 LLM decidió: '{llm_response}'")
            
            # Limpiar respuesta del LLM
            if 'calculator' in llm_response:
                return 'calculator'
            elif 'weather' in llm_response:
                return 'weather'
            elif 'text_processor' in llm_response or 'text' in llm_response:
                return 'text_processor'
            else:
                return None  # No necesita herramientas
        else:
            print(f"❌ Error Ollama: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error conectando a Ollama: {e}")
        return None

def execute_with_llm_decision(message):
    """Usa LLM para decidir y luego ejecuta la herramienta"""
    
    # 1. El LLM decide qué herramienta usar
    tool_choice = decide_with_ollama(message)
    print(f"🔧 Herramienta elegida: {tool_choice}")
    
    if tool_choice == 'calculator':
        # 2a. Extraer parámetros para calculadora
        import re
        numbers = re.findall(r'-?\d+\.?\d*', message)
        if len(numbers) >= 2:
            a, b = float(numbers[0]), float(numbers[1])
            
            # Determinar operación
            message_lower = message.lower()
            if any(k in message_lower for k in ['suma', 'sumar', 'más', '+', 'plus']):
                operation = 'add'
            elif any(k in message_lower for k in ['resta', 'restar', 'menos', '-', 'minus']):
                operation = 'subtract'
            elif any(k in message_lower for k in ['multiplica', 'multiplicar', 'por', '×', '*', 'times']):
                operation = 'multiply'
            elif any(k in message_lower for k in ['divide', 'dividir', 'entre', '÷', '/', 'divided']):
                operation = 'divide'
            else:
                operation = 'add'
            
            result = calculator(operation, a, b)
            return {
                'tool_used': 'calculator (LLM)',
                'parameters': {'operation': operation, 'a': a, 'b': b},
                'result': result,
                'response': f"🤖 Usé la calculadora: {a} {operation} {b} = {result}"
            }
    
    elif tool_choice == 'weather':
        # 2b. Extraer ciudad para clima
        cities = ['madrid', 'barcelona', 'mexico', 'new york', 'tokyo', 'paris', 'london', 'berlin', 'rome']
        city = 'Madrid'  # default
        message_lower = message.lower()
        
        for c in cities:
            if c in message_lower:
                city = c.title()
                break
        
        result = weather_tool(city)
        return {
            'tool_used': 'weather (LLM)',
            'parameters': {'city': city},
            'result': result,
            'response': f"🤖 Consulté el clima en {city}: {result['temperature']}, {result['condition']}"
        }
    
    elif tool_choice == 'text_processor':
        # 2c. Procesar texto
        import re
        quoted = re.findall(r'"([^"]*)"', message)
        text = quoted[0] if quoted else message
        
        message_lower = message.lower()
        if 'mayúscula' in message_lower or 'uppercase' in message_lower:
            operation = 'uppercase'
        elif 'minúscula' in message_lower or 'lowercase' in message_lower:
            operation = 'lowercase'
        elif 'reversa' in message_lower or 'reverse' in message_lower:
            operation = 'reverse'
        else:
            operation = 'count_words'
        
        result = text_processor(text, operation)
        return {
            'tool_used': 'text_processor (LLM)',
            'parameters': {'text': text, 'operation': operation},
            'result': result,
            'response': f"🤖 Procesé el texto: {result['result']}"
        }
    
    else:
        # 3. Respuesta directa del LLM sin herramientas
        return generate_llm_response(message)
    
# ============ SISTEMA DE WORKFLOWS INTELIGENTES ============
def plan_workflow_with_llm(message):
    """El LLM planifica un workflow de múltiples pasos"""
    
    planning_prompt = f"""Eres un planificador de tareas inteligente. El usuario necesita esto:

"{message}"

HERRAMIENTAS DISPONIBLES:
- calculator: matemáticas básicas
- weather: clima de UNA ciudad
- multi_weather: clima de MÚLTIPLES ciudades
- text_processor: procesar texto
- batch_calculator: múltiples cálculos
- data_summary: resumir y analizar datos

INSTRUCCIONES:
- Si necesitas clima de 2+ ciudades, usa multi_weather
- Si necesitas múltiples cálculos, usa batch_calculator
- Si necesitas comparar o analizar datos, planifica en pasos
- Responde en JSON con este formato:

{{"workflow": [
  {{"step": 1, "action": "herramienta", "params": {{"param": "valor"}}, "description": "qué hace"}},
  {{"step": 2, "action": "analyze", "description": "analizar resultados del paso 1"}}
], "needs_analysis": true/false}}

Usuario: {message}
Planificación:"""

    try:
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': 'phi',
                'prompt': planning_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                    'num_predict': 200
                }
            },
            timeout=150
        )
        
        if response.status_code == 200:
            llm_response = response.json()['response']
            print(f"🤖 Plan generado: {llm_response[:200]}...")
            
            # Intentar extraer JSON
            try:
                import json
                # Buscar JSON en la respuesta
                start = llm_response.find('{')
                end = llm_response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = llm_response[start:end]
                    plan = json.loads(json_str)
                    return plan
            except:
                pass
        
        # Fallback: análisis simple
        return analyze_message_for_workflow(message)
        
    except Exception as e:
        print(f"❌ Error planeando workflow: {e}")
        return analyze_message_for_workflow(message)

def analyze_message_for_workflow(message):
    """Fallback: análisis basado en patrones para workflows"""
    message_lower = message.lower()
    
    # Detectar necesidad de múltiples ciudades
    if any(word in message_lower for word in ['compara', 'versus', 'vs', 'mejor', 'peor']) and 'clima' in message_lower:
        # Extraer nombres de ciudades
        cities = []
        common_cities = ['madrid', 'barcelona', 'sevilla', 'valencia', 'paris', 'london', 'berlin', 'rome', 'tokyo']
        for city in common_cities:
            if city in message_lower:
                cities.append(city.title())
        
        if len(cities) >= 2:
            return {
                "workflow": [
                    {"step": 1, "action": "multi_weather", "params": {"cities": cities}, "description": f"Obtener clima de {len(cities)} ciudades"},
                    {"step": 2, "action": "analyze", "description": "Comparar y recomendar"}
                ],
                "needs_analysis": True
            }
    
    # Detectar múltiples cálculos
    import re
    numbers = re.findall(r'\d+', message)
    if len(numbers) >= 4 and any(op in message_lower for op in ['suma', 'resta', 'calcula', 'operaciones']):
        return {
            "workflow": [
                {"step": 1, "action": "batch_calculator", "params": {"operations": "multiple"}, "description": "Múltiples cálculos"},
                {"step": 2, "action": "analyze", "description": "Sumar y analizar resultados"}
            ],
            "needs_analysis": True
        }
    
    # Workflow simple (como antes)
    return {
        "workflow": [
            {"step": 1, "action": "simple", "params": {}, "description": "Tarea simple"}
        ],
        "needs_analysis": False
    }

def execute_workflow(message, plan):
    """Ejecuta el workflow planificado paso a paso"""
    results = []
    
    for step in plan.get("workflow", []):
        step_num = step.get("step", 0)
        action = step.get("action", "")
        params = step.get("params", {})
        description = step.get("description", "")
        
        print(f"🔄 Ejecutando paso {step_num}: {description}")
        
        if action == "multi_weather":
            cities = params.get("cities", [])
            result = multi_weather_tool(cities)
            results.append({"step": step_num, "action": action, "result": result})
            
        elif action == "batch_calculator":
            # Extraer operaciones del mensaje
            operations = extract_operations_from_message(message)
            result = batch_calculator_tool(operations)
            results.append({"step": step_num, "action": action, "result": result})
            
        elif action == "weather":
            city = params.get("city", "Madrid")
            result = weather_tool(city)
            results.append({"step": step_num, "action": action, "result": result})
            
        elif action == "calculator":
            result = calculator(
                params.get("operation", "add"),
                params.get("a", 0),
                params.get("b", 0)
            )
            results.append({"step": step_num, "action": action, "result": result})
            
        elif action == "analyze":
            # Este paso se maneja en synthesize_results
            continue
            
        elif action == "simple":
            # Ejecutar como antes (modo simple)
            return execute_with_llm_decision(message)
    
    # Si necesita análisis, sintetizar resultados
    if plan.get("needs_analysis", False):
        return synthesize_results(message, results)
    else:
        return results[-1] if results else {"response": "No se ejecutó ninguna acción"}

def extract_operations_from_message(message):
    """Extrae operaciones matemáticas del mensaje"""
    import re
    
    # Buscar patrones como "5+3, 10-2, 8*4"
    patterns = re.findall(r'(\d+)\s*([+\-*/])\s*(\d+)', message)
    operations = []
    
    for match in patterns:
        a, op, b = match
        operation_map = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide'}
        operations.append({
            'a': int(a),
            'b': int(b),
            'operation': operation_map.get(op, 'add')
        })
    
    # Si no encuentra patrones, crear operaciones ejemplo
    if not operations:
        import re
        numbers = re.findall(r'\d+', message)
        if len(numbers) >= 2:
            for i in range(0, len(numbers)-1, 2):
                operations.append({
                    'a': int(numbers[i]),
                    'b': int(numbers[i+1]),
                    'operation': 'add'
                })
    
    return operations[:5]  # Máximo 5 operaciones

def synthesize_results(original_message, workflow_results):
    """El LLM analiza todos los resultados y genera una respuesta inteligente"""
    
    # Preparar contexto de resultados
    context = f"El usuario preguntó: '{original_message}'\n\nResultados obtenidos:\n"
    
    for result in workflow_results:
        action = result.get("action", "unknown")
        data = result.get("result", {})
        context += f"\n{action.upper()}:\n{str(data)[:500]}\n"
    
    synthesis_prompt = f"""{context}

INSTRUCCIONES:
- Analiza TODOS los resultados anteriores
- Crea una respuesta coherente y útil
- Si es comparación de clima, da recomendaciones específicas
- Si son cálculos, proporciona totales y análisis
- Sé conciso pero informativo
- Usa formato amigable, no JSON

Respuesta analizada:"""

    try:
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': 'phi',
                'prompt': synthesis_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 250
                }
            },
            timeout=150
        )
        
        if response.status_code == 200:
            analysis = response.json()['response']
            return {
                'tool_used': 'workflow_composition',
                'workflow_steps': len(workflow_results),
                'result': workflow_results,
                'response': f"🔗 Análisis compuesto: {analysis}"
            }
    except Exception as e:
        print(f"❌ Error en síntesis: {e}")
    
    # Fallback: respuesta simple
    return {
        'tool_used': 'workflow_basic',
        'workflow_steps': len(workflow_results),
        'result': workflow_results,
        'response': f"Ejecuté {len(workflow_results)} pasos. Resultados disponibles."
    }

def generate_llm_response(message):
    """Genera respuesta directa con el LLM sin usar herramientas"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'phi',
                'prompt': f"Eres un asistente amigable. Responde de forma concisa.\n\nUsuario: {message}\nAsistente:",
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 100
                }
            },
            timeout=150
        )
        
        if response.status_code == 200:
            llm_text = response.json()['response']
            return {
                'tool_used': 'direct_llm',
                'result': llm_text,
                'response': f"🤖 {llm_text}"
            }
        else:
            return {
                'tool_used': None,
                'result': None,
                'response': "❌ Error al generar respuesta con LLM"
            }
    except Exception as e:
        return {
            'tool_used': None,
            'result': None,
            'response': "❌ Error de conexión con Ollama. ¿Está iniciado?"
        }
    
# ============ HERRAMIENTAS DE AGREGACIÓN ============
def multi_weather_tool(cities):
    """Obtiene clima de múltiples ciudades para análisis comparativo"""
    results = {}
    
    if isinstance(cities, str):
        cities = [cities]
    
    for city in cities[:5]:  # Máximo 5 ciudades para no sobrecargar
        try:
            weather_data = weather_tool(city)
            results[city] = weather_data
        except Exception as e:
            results[city] = {"error": f"No se pudo obtener clima de {city}"}
    
    return {
        "cities_count": len(results),
        "weather_data": results,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def batch_calculator_tool(operations):
    """Ejecuta múltiples operaciones matemáticas"""
    results = []
    
    for op in operations[:10]:  # Máximo 10 operaciones
        try:
            result = calculator(
                op.get('operation', 'add'),
                op.get('a', 0),
                op.get('b', 0)
            )
            results.append({
                "operation": f"{op.get('a')} {op.get('operation')} {op.get('b')}",
                "result": result
            })
        except Exception as e:
            results.append({
                "operation": f"{op.get('a')} {op.get('operation')} {op.get('b')}",
                "error": str(e)
            })
    
    return {
        "calculations": results,
        "total_operations": len(results)
    }

def data_summary_tool(data_type, data):
    """Resume y estructura datos para análisis"""
    if data_type == "weather_comparison":
        cities = []
        temps = []
        conditions = []
        
        for city, weather in data.items():
            if "error" not in weather:
                cities.append(city)
                # Extraer temperatura numérica
                temp_str = weather.get('temperature', '0°C')
                temp_num = int(temp_str.replace('°C', ''))
                temps.append(temp_num)
                conditions.append(weather.get('condition', 'Unknown'))
        
        if temps:
            return {
                "summary_type": "weather_comparison",
                "cities": cities,
                "temperature_range": f"{min(temps)}°C - {max(temps)}°C",
                "average_temp": f"{sum(temps)/len(temps):.1f}°C",
                "conditions": conditions,
                "best_weather_city": cities[temps.index(max(temps))],
                "coolest_city": cities[temps.index(min(temps))]
            }
    
    elif data_type == "calculations":
        total = sum(calc.get('result', 0) for calc in data if isinstance(calc.get('result'), (int, float)))
        return {
            "summary_type": "calculations",
            "total_sum": total,
            "operations_count": len(data),
            "average": total / len(data) if data else 0
        }
    
    return {"summary_type": "unknown", "raw_data": data}

# ============ ENDPOINTS MCP ============
@app.route('/tools', methods=['GET'])
def list_tools():
    """Lista todas las herramientas disponibles"""
    return jsonify({
        "tools": [
            {
                "name": "calculator",
                "description": "Realiza operaciones matemáticas básicas",
                "parameters": {
                    "operation": "add, subtract, multiply, divide",
                    "a": "primer número",
                    "b": "segundo número"
                }
            },
            {
                "name": "weather",
                "description": "Obtiene información del clima de una ciudad",
                "parameters": {
                    "city": "nombre de la ciudad"
                }
            },
            {
                "name": "text_processor",
                "description": "Procesa texto con varias operaciones",
                "parameters": {
                    "text": "texto a procesar",
                    "operation": "uppercase, lowercase, reverse, count_words, count_chars"
                }
            }
        ]
    })

@app.route('/execute', methods=['POST'])
def execute_tool():
    """Ejecuta una herramienta específica"""
    data = request.json
    tool = data.get('tool')
    params = data.get('parameters', {})
    
    try:
        if tool == 'calculator':
            result = calculator(
                params.get('operation'),
                params.get('a', 0),
                params.get('b', 0)
            )
        elif tool == 'weather':
            result = weather_tool(params.get('city', 'Madrid'))
        elif tool == 'text_processor':
            result = text_processor(
                params.get('text', ''),
                params.get('operation', 'uppercase')
            )
        else:
            return jsonify({"error": f"Herramienta '{tool}' no encontrada"}), 404
            
        return jsonify({"result": result, "tool": tool})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint de chat que decide automáticamente qué herramienta usar"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No se proporcionó mensaje"}), 400
    
    # Decidir y ejecutar
    result = decide_and_execute(message)
    
    # Log para debugging
    print(f"\n📝 Mensaje: {message}")
    print(f"🔧 Herramienta usada: {result['tool_used']}")
    print(f"📊 Resultado: {result['result']}")
    
    return jsonify(result)

@app.route('/chat-llm', methods=['POST'])
def chat_with_llm():
    """Endpoint de chat que usa LLM para decisiones inteligentes"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No se proporcionó mensaje"}), 400
    
    # Usar LLM para decidir y ejecutar
    result = execute_with_llm_decision(message)
    
    # Log detallado
    print(f"\n📝 Mensaje: {message}")
    print(f"🧠 Procesado con LLM")
    print(f"🔧 Herramienta: {result.get('tool_used', 'ninguna')}")
    print(f"📊 Resultado: {str(result.get('result', 'N/A'))[:100]}...")
    
    return jsonify(result)

@app.route('/chat-compose', methods=['POST'])
def chat_compose():
    """Endpoint avanzado que maneja workflows complejos"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No se proporcionó mensaje"}), 400
    
    # Planificar workflow
    print(f"\n🎯 Planificando workflow para: {message}")
    plan = plan_workflow_with_llm(message)
    
    # Ejecutar workflow
    print(f"📋 Plan: {plan.get('workflow', [])}")
    result = execute_workflow(message, plan)
    
    # Log detallado
    print(f"🔧 Workflow completado")
    print(f"📊 Pasos ejecutados: {result.get('workflow_steps', 0)}")
    
    return jsonify(result)

@app.route('/health-compose', methods=['GET'])
def health_compose():
    """Verificar capacidades de composición"""
    return jsonify({
        "composition_features": [
            "multi_weather: Clima de múltiples ciudades",
            "batch_calculator: Múltiples cálculos",
            "workflow_planning: Planificación automática",
            "llm_synthesis: Análisis inteligente de resultados"
        ],
        "status": "disponible"
    })

@app.route('/health-ollama', methods=['GET'])
def health_ollama():
    """Verificar si Ollama está disponible"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=150)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                "ollama_status": "disponible",
                "models": [m['name'] for m in models]
            })
    except:
        pass
    
    return jsonify({"ollama_status": "no disponible"}), 503

@app.route('/')
def home():
    """Sirve la interfaz web"""
    return render_template('index.html')

if __name__ == '__main__':
    print("\n🚀 Servidor MCP iniciando...")
    print("📊 Herramientas disponibles: calculator")
    print("🌐 Visita: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)