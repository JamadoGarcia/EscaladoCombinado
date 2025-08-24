import time
import subprocess
from datetime import datetime, timedelta
import psutil
import requests

ACCESS_LOG = "logs/access.log"
SERVICE_NAME = "web"

MIN_INSTANCES = 1 #límites de escalamiento de 1 a 5 instancias
MAX_INSTANCES = 6 # Maximo de instancias a escalar 

RPS_THRESHOLD = 50 #Umbral de request por segundo para activar el escalamiento 
CHECK_INTERVAL = 5 #tiempo de verificación para verificar instancias 

# Umbrales de memoria
# dividir 1000/150 para ver las instancias permitidas
MEMORY_THRESHOLD_MB = 1200 # Mínimo de memoria libre para escalar horizontalmente
MEMORY_USAGE_PER_INSTANCE_MB = 150  # Memoria estimada por instancia


SERVICE_URL = "http://localhost:8080/metrics"

def get_rps_from_service():
    try:
        response = requests.get(SERVICE_URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get("rps_last_5s", 0)
    except Exception as e:
        print(f"Error obteniendo métricas:{e}  🚓")
    return 0

def scale_service(service, instances):
    print(f"➡️ Escalando {service} a {instances} instancias...")
    subprocess.run(["docker", "compose", "up", "-d", "--scale", f"{service}={instances}"])

def main():
    current_instances = MIN_INSTANCES
    while True:
        print("\nVerificando tráfico entrante 📚")
        rps_per_sec = get_rps_from_service()
        print(f"RPS promedio: 🗝️ {rps_per_sec:.2f} req/s | Instancias actuales: {current_instances}")

        mem = psutil.virtual_memory()
        mem_available_mb = mem.available // (1024 * 1024)
        max_possible_instances = mem_available_mb // MEMORY_USAGE_PER_INSTANCE_MB

        if rps_per_sec > RPS_THRESHOLD:
            if current_instances < MAX_INSTANCES and mem_available_mb >= MEMORY_THRESHOLD_MB:
                current_instances += 1
                print("✅ Memoria suficiente, escalando horizontalmente...")
                scale_service(SERVICE_NAME, current_instances)
            elif current_instances < max_possible_instances:
                # Escalado vertical: solo una instancia más por ciclo
                current_instances += 1
                print("🚩 Escalando verticalmente (más recursos por instancia)...")
                print(f"Memoria disponible: {mem_available_mb} MB")
                print(f"Podrías crear hasta {max_possible_instances} instancias con la memoria actual.")
                scale_service(SERVICE_NAME, current_instances)
            else:
                print("⚠️ No hay suficiente memoria para escalar más instancias.")
        elif rps_per_sec < (RPS_THRESHOLD / 2) and current_instances > MIN_INSTANCES:
            current_instances -= 1
            print("⬇️ Reducción de instancias por baja demanda...")
            scale_service(SERVICE_NAME, current_instances)
        else:
            print("No se requiere escalado en este momento. 💢")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()