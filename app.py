from flask import Flask
import socket
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Contador de requests con timestamps
request_times = []
lock = threading.Lock()

@app.route('/')
def index():
    hostname = socket.gethostname()
    now = datetime.now()
    with lock:
        request_times.append(now)
    return f'Hola desde el Microservicio {hostname}!'

@app.route('/metrics')
def metrics():
    """Devuelve el número de requests en los últimos 5 segundos"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=5)
    with lock:
        recent_requests = [t for t in request_times if t > cutoff]
        count = len(recent_requests)
    return {"rps_last_5s": count / 5}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
