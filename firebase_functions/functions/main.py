from firebase_functions import https_fn, options
from firebase_admin import initialize_app
import joblib
import numpy as np
import os
import json
import pandas as pd

# Inicializar la app de Firebase
initialize_app()

# Variables globales para cachear el modelo en memoria, pero las iniciamos vacías
modelo = None
scaler = None

def load_models():
    """Carga los modelos en memoria solo si no han sido cargados antes (Lazy Loading)"""
    global modelo, scaler
    if modelo is None or scaler is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "models", "xgboost_sevilla_temperatura_v1.pkl")
        SCALER_PATH = os.path.join(BASE_DIR, "models", "xgboost_sevilla_temperatura_v1_scaler.pkl")
        
        modelo = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

@https_fn.on_request(
    cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"]),
    memory=options.MemoryOption.MB_512,  # 512 MB de RAM
    region="europe-west1",               # Desplegamos en Europa
    timeout_sec=15                       # Damos 15 segundos a la función para responder
)
def predict_temperature(req: https_fn.Request) -> https_fn.Response:
    # 1. Validación del Request
    if req.method != "POST":
        return https_fn.Response("Método no permitido. Usa POST.", status=405)
        
    try:
        data = req.get_json()
    except Exception:
        return https_fn.Response("Formato JSON inválido", status=400)

    # 2. CARGAMOS LOS MODELOS AQUÍ (Solo se ejecutará una vez por contenedor)
    try:
        load_models()
    except Exception as e:
        return https_fn.Response(f"Error cargando modelos: {str(e)}", status=500)

    # 3. Extracción y ordenamiento de las 9 variables del TFM
    try:
        input_features = pd.DataFrame([{
            'NDVI': float(data["NDVI"]),
            'NDBI': float(data["NDBI"]),
            'Albedo': float(data["Albedo"]),
            'D2W_meters': float(data["D2W_meters"]),
            'D2R_HighCapacity_m': float(data["D2R_HighCapacity_m"]),
            'D2R_Urban_m': float(data["D2R_Urban_m"]),
            'Tree_Density_50m': int(data["Tree_Density_50m"]),
            'Building_Density_100m': int(data["Building_Density_100m"]),
            'Avg_Building_Height_100m': float(data["Avg_Building_Height_100m"])
        }])
        
        # Forzamos el orden exacto de las columnas de entrenamiento por seguridad
        columnas_ordenadas = [
            'NDVI', 'NDBI', 'Albedo', 'D2W_meters', 'D2R_HighCapacity_m', 
            'D2R_Urban_m', 'Tree_Density_50m', 'Building_Density_100m', 'Avg_Building_Height_100m'
        ]
        input_features = input_features[columnas_ordenadas]
        
    except (KeyError, TypeError, ValueError) as e:
        return https_fn.Response(f"Error en los datos de entrada: {str(e)}", status=400)

    # 4. Procesamiento
    input_scaled = scaler.transform(input_features)
    prediccion = modelo.predict(input_scaled)

    # 5. Construir la respuesta con el CHIVATO DEBUG
    resultado = {
        "temperatura_predicha_lst": round(float(prediccion[0]), 2),
        "unidad": "Celsius",
        "status": "success",
        "debug_scaled_array": input_scaled[0].tolist() 
    }

    return https_fn.Response(
        json.dumps(resultado),
        mimetype="application/json",
        status=200
    )