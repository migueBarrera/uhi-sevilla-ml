import requests
import pandas as pd

def descargar_carreteras_csv(bbox="37.33,-6.03,37.45,-5.90", output_file="carreteras_sevilla.csv"):
    """
    Se conecta a la API de OpenStreetMap, descarga las vías principales
    y las guarda en un archivo CSV.
    """
    print("🚗 Conectando a OpenStreetMap (Overpass API)...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      way["highway"~"motorway|trunk|primary|secondary"]({bbox});
    );
    out center; 
    """
    
    # Añadimos cabeceras para evitar el bloqueo 406 Not Acceptable de Overpass
    headers = {
        'User-Agent': 'ThermoSevilla_TFM_Project/1.0',
        'Accept': 'application/json'
    }
    
    # Pasamos los headers en la petición
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    carreteras_data = []
    
    for element in data['elements']:
        if element['type'] == 'way' and 'center' in element:
            carreteras_data.append({
                'id_via': element['id'],
                'tipo': element['tags'].get('highway', 'desconocido'),
                'nombre': element['tags'].get('name', 'Sin nombre'),
                'latitud': element['center']['lat'],
                'longitud': element['center']['lon']
            })
            
    if not carreteras_data:
        raise ValueError("No se encontraron carreteras en las coordenadas indicadas.")

    # Guardar en CSV
    df_carreteras = pd.DataFrame(carreteras_data)
    df_carreteras.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Descarga completada: {output_file} ({len(df_carreteras)} tramos viales registrados)")
    return output_file

if __name__ == "__main__":
    descargar_carreteras_csv()