import pandas as pd
import numpy as np

def descargar_arbolado_csv(output_file="arbolado_sevilla.csv"):
    """
    Extrae el inventario de arbolado urbano y lo guarda directamente en formato CSV.
    """
    print("🌳 Extrayendo datos del Inventario Municipal de Arbolado...")
    
    # Simulación de la descarga de datos del portal municipal
    # (Para el proyecto final, aquí podrías hacer un pd.read_csv() desde la URL pública)
    np.random.seed(42)
    num_arboles = 10000
    
    # Generamos los datos con la estructura tabular clásica de un Open Data
    df_arboles = pd.DataFrame({
        'id_arbol': range(1, num_arboles + 1),
        'especie': np.random.choice(
            ['Naranjo amargo', 'Plátano de sombra', 'Jacaranda', 'Palmera datilera', 'Olmo'], 
            num_arboles, 
            p=[0.35, 0.25, 0.20, 0.10, 0.10] # Probabilidades ajustadas a la realidad botánica
        ),
        'latitud': np.random.uniform(low=37.33, high=37.45, size=num_arboles),
        'longitud': np.random.uniform(low=-6.03, high=-5.90, size=num_arboles)
    })
    
    # Guardar en CSV
    df_arboles.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Descarga completada: {output_file} ({num_arboles} árboles registrados)")
    return output_file

if __name__ == "__main__":
    descargar_arbolado_csv()