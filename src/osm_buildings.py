import requests
import pandas as pd
import re

def estimar_altura(tags):
    """
    Intenta extraer la altura en metros. Si no existe, usa el número de plantas.
    Si no hay datos, asume un edificio promedio de 2 plantas (6 metros).
    """
    # 1. Intentar sacar la altura exacta ('height')
    if 'height' in tags:
        try:
            # Limpiamos letras por si alguien escribió "15m" en lugar de "15"
            altura_limpia = re.sub(r'[^\d.]', '', str(tags['height']))
            return float(altura_limpia)
        except ValueError:
            pass
            
    # 2. Intentar sacar las plantas ('building:levels') y multiplicar por 3m/planta
    if 'building:levels' in tags:
        try:
            plantas_limpias = re.sub(r'[^\d.]', '', str(tags['building:levels']))
            return float(plantas_limpias) * 3.0
        except ValueError:
            pass
            
    # 3. Valor por defecto para ciudad (2 plantas)
    return 6.0

def descargar_edificios_csv(bbox="37.33,-6.03,37.45,-5.90", output_file="edificios_sevilla.csv"):
    """
    Se conecta a la API de OpenStreetMap, descarga los polígonos de edificios,
    calcula su centro y estima su altura.
    """
    print("🏢 Conectando a OpenStreetMap para descargar edificios (Esto puede tardar varios minutos)...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Aumentamos el timeout a 900 segundos porque son muchísimos datos
    overpass_query = f"""
    [out:json][timeout:900];
    (
      way["building"]({bbox});
      relation["building"]({bbox});
    );
    out center; 
    """
    
    headers = {
        'User-Agent': 'ThermoSevilla_TFM_Project/1.0',
        'Accept': 'application/json'
    }
    
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    edificios_data = []
    
    for element in data['elements']:
        # Solo guardamos si Overpass pudo calcular el centro geométrico del edificio
        if 'center' in element:
            altura = estimar_altura(element.get('tags', {}))
            
            edificios_data.append({
                'id_edificio': element['id'],
                'latitud': element['center']['lat'],
                'longitud': element['center']['lon'],
                'altura_estimada': altura
            })
            
    if not edificios_data:
        raise ValueError("No se encontraron edificios en las coordenadas indicadas.")

    # Guardar en CSV
    df_edificios = pd.DataFrame(edificios_data)
    df_edificios.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Descarga completada: {output_file} ({len(df_edificios)} edificios registrados)")
    return output_file

if __name__ == "__main__":
    descargar_edificios_csv()