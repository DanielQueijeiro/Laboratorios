from flask import Flask, render_template, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

API_URL = os.environ.get('API_URL', 'http://nginx')

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Obtiene estadísticas del sistema"""
    try:
        # Stats del sistema
        response = requests.get(f"{API_URL}/stats", timeout=5)
        stats = response.json()
        
        # Health de cada worker
        health_status = []
        for worker_id in range(1, 4):
            try:
                health_response = requests.get(
                    f"{API_URL}/health", 
                    timeout=2
                )
                health_status.append({
                    'worker': f'worker-{worker_id}',
                    'status': 'healthy' if health_response.status_code == 200 else 'unhealthy'
                })
            except:
                health_status.append({
                    'worker': f'worker-{worker_id}',
                    'status': 'unknown'
                })
        
        return jsonify({
            **stats,
            'health_status': health_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_analysis():
    """Endpoint para probar análisis"""
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={'text': 'This is a test message for sentiment analysis'},
            timeout=10
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)