from flask import Flask, jsonify, request
import redis
import psycopg2
import json
import os
import hashlib
from textblob import TextBlob
from datetime import datetime
import time

app = Flask(__name__)

# Configuración de Redis
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

# Configuración de PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        database=os.environ.get('DB_NAME', 'sentiments'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'secret')
    )

# ID único del worker
WORKER_ID = os.environ.get('WORKER_ID', 'worker-1')

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Verificar Redis
        redis_client.ping()
        # Verificar PostgreSQL
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'worker_id': WORKER_ID,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """Analiza el sentimiento de un texto"""
    start_time = time.time()
    
    # Obtener texto del request
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    
    # Crear hash del texto para cache
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    # Verificar cache
    cached_result = redis_client.get(f"sentiment:{text_hash}")
    if cached_result:
        result = json.loads(cached_result)
        result['cached'] = True
        result['worker_id'] = WORKER_ID
        return jsonify(result)
    
    # Análisis de sentimiento con TextBlob
    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Clasificar sentimiento
        if sentiment.polarity > 0.1:
            label = 'positive'
        elif sentiment.polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        result = {
            'text': text[:100],  # Primeros 100 caracteres
            'sentiment': label,
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'worker_id': WORKER_ID,
            'cached': False,
            'processing_time': time.time() - start_time
        }
        
        # Guardar en cache (TTL 1 hora)
        redis_client.setex(
            f"sentiment:{text_hash}",
            3600,
            json.dumps(result)
        )
        
        # Guardar en base de datos
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO analyses 
                   (text_hash, text, sentiment, polarity, subjectivity, worker_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (text_hash, text[:500], label, sentiment.polarity, 
                 sentiment.subjectivity, WORKER_ID)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            app.logger.error(f"Database error: {e}")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'worker_id': WORKER_ID
        }), 500

@app.route('/stats')
def get_stats():
    """Obtiene estadísticas del sistema"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total de análisis
        cur.execute("SELECT COUNT(*) FROM analyses")
        total = cur.fetchone()[0]
        
        # Distribución de sentimientos
        cur.execute("""
            SELECT sentiment, COUNT(*) 
            FROM analyses 
            GROUP BY sentiment
        """)
        distribution = dict(cur.fetchall())
        
        # Análisis por worker
        cur.execute("""
            SELECT worker_id, COUNT(*) 
            FROM analyses 
            GROUP BY worker_id
        """)
        by_worker = dict(cur.fetchall())
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_analyses': total,
            'sentiment_distribution': distribution,
            'analyses_by_worker': by_worker,
            'cache_keys': redis_client.dbsize()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)