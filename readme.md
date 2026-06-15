# Urban Heat Island Predictor Sevilla (UHI-Predictor Sevilla)

# Definición del Proyecto de Machine Learning: Predicción de Temperatura Superficial Terrestre en Sevilla

## 1. Definición del Problema de Machine Learning
El problema a resolver es de **regresión**. El algoritmo tendrá la tarea de estimar y predecir un valor numérico continuo absoluto, correspondiente a los grados centígrados de la temperatura del suelo en un punto geográfico concreto, basándose en las características espaciales y de los materiales de dicho punto.

## 2. Descripción del Contexto del Problema y su Utilidad Real
La ciudad de Sevilla soporta episodios de calor extremo durante el periodo estival. Este riesgo climático se ve drásticamente agravado por el fenómeno de la **Isla de Calor Urbano (ICU)**, provocado por la alta densidad constructiva, la impermeabilización con asfalto y la escasez de cubiertas vegetales. Estos factores hacen que el tejido urbano retenga y emita mucha más radiación térmica que las zonas rurales periféricas.

La utilidad real de este proyecto radica en el desarrollo de una herramienta prescriptiva para planificadores urbanos y la administración pública, asi como el público en general. El modelo predictivo alimentará un simulador interactivo que permitirá evaluar intervenciones de urbanismo sostenible (como reforestar un barrio o modificar los materiales de las cubiertas) y cuantificar de manera exacta cuántos grados centígrados se lograría enfriar el entorno gracias a dicha intervención.

## 3. Identificación y Justificación de las Variables Relevantes
Para garantizar la fiabilidad del modelo y su capacidad de generalización (evitando el sobreajuste a la topología estricta de Sevilla), se ha descartado el uso de coordenadas espaciales absolutas (latitud y longitud). En su lugar, se han identificado variables que representan el comportamiento físico de los materiales y variables espaciales relativas.

Se justifica el uso de índices de vegetación y edificación porque representan los principales promotores y mitigadores de la absorción de calor, y el uso de la distancia a masas de agua porque modela el "efecto oasis" que refrigera las zonas adyacentes al río.

## 4. Definición de Variables

### Variable Objetivo (Target)
* **LST (Land Surface Temperature - Temperatura Superficial Terrestre):** Representa el calor radiante real del suelo y los elementos urbanos medido en grados Celsius (°C), obtenido a partir de las bandas térmicas del satélite Landsat 8.

### Variables Independientes (Features)
* **NDVI (Normalized Difference Vegetation Index):** Mide la densidad y salud de la masa vegetal. Actúa como factor de refrigeración (sombra y evapotranspiración).
* **NDBI (Normalized Difference Built-up Index):** Cuantifica la densidad de materiales constructivos e impermeables (hormigón, asfalto, ladrillo). Actúa como motor principal de acumulación térmica.
* **D2W (Distance to Water):** Distancia euclídea medida en metros desde el punto evaluado hasta la masa de agua (río Guadalquivir) más cercana.

## 5. Tipo de Problema
* **Aprendizaje Supervisado (Supervised Learning):** Se trata de un problema de Aprendizaje Supervisado, ya que el modelo se entrenará utilizando un conjunto de datos históricos donde la respuesta correcta (la variable target LST captada por el satélite) ya es conocida para cada combinación de las variables independientes.

# Instrucciones para Levantar el Proyecto
El proyecto se compone de diferentes partes:
* Modelo: La parte de descarga de datos, analisis, preparación y entrenamiento del modelo, se realiza dentro de la carpeta `notebooks`, dividido en diferentes hitos.
* Web: Una web para visualizar los datos y poder probar el modelo se encuentra dentro de la carpeta `web`. Es una app react que se desplegara en Firebase Hosting.
* Functions: Serverless para desplegar un endpoint junto con el modelo para poder ejecutarlo via api, se desplegará en Firebase Functions. Se encuentra en `firebase_functions`

## Modelo

Para ejcutar los distintos notebooks, sera necesario activar un entorno virtual en python, activarlo, descargar dependencias y ya se podra ejecutar. Se recomienda ejecutarlos en orden, ya que algunos dependen de los anteriores. (ej: la descarga de los datos)

1. Crea un entorno virtual:
   ```bash
     python -m venv venv
   ```

2. Activa el entorno virtual:
   - En macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - En Windows:
     ```bash
     venv\Scripts\activate
     ```

3. Instala las dependencias dentro del entorno virtual:
   ```bash
   pip install -r requirements.txt
   ```

4. Autentícate en Google Earth Engine (solo la primera vez):
   ```bash
   earthengine authenticate
   ```

5. Crea un archivo `.env` en el directorio `notebooks` con el siguiente contenido:
   ```env
   AWS_ACCESS_KEY=TU_AWS_ACCESS_KEY
   AWS_SECRET_KEY=TU_AWS_SECRET_KEY
   AWS_SESSION_TOKEN=TU_AWS_SESSION_TOKEN
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=tfm-thermo-sevilla-raw-data
   MONGO_URI=TU_URI_DE_MONGODB_ATLAS
   DB_NAME=clima_sevilla
   COLLECTION_NAME=pixeles_termicos
   GEE_PROJECT=TU_ID_PROYECTO_GEE
   ```
   > Las credenciales de AWS (`AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_SESSION_TOKEN`) son temporales (STS). Cuando expiren deberás actualizarlas.
   > `GEE_PROJECT` es el ID del proyecto de Google Earth Engine habilitado con la API de Earth Engine.
   https://awsacademy.instructure.com/courses/173937/modules/items/17058285


6. Ejecuta cada cuaderno

## Web

### Url de la web desplegada
https://testworkflows-830d7.web.app/

### Para desplegar la web en firebase, sera necesario una cuenta de Firebase activa.

1. Navegar hacia 'web/frontend-sevilla:
   ```bash
     cd web/frontend-sevilla
   ```

2. Compilar el proyecto:
     ```bash
      npm run build 
     ```

3. Desplegar la web:
   ```bash
    firebase deploy --only hosting 
   ```

## Functions
Para desplegar la function en firebase, sera necesario una cuenta de Firebase activa.

1. Navegar hacia 'firebase_functions:
   ```bash
     cd firebase_functions
   ```

2. Desplegar la functions:
   ```bash
    firebase deploy --only functions 
   ```

### Ejecutar el modelo via api
   ejemplo de curl para ejecutar el modelo

   ```bash
   curl -s -w "\n⏱️ Tiempo total de respuesta: %{time_total} segundos\n" \
      -X POST "https://predict-temperature-bzqfrud2ua-ew.a.run.app" \
      -H "Content-Type: application/json" \
      -d '[
               {
                  "NDVI": 0.15,
                  "NDBI": 0.25,
                  "Albedo": 0.18,
                  "D2W_meters": 1200.5,
                  "D2R_HighCapacity_m": 350.0,
                  "D2R_Urban_m": 15.0,
                  "Tree_Density_50m": 3,
                  "Building_Density_100m": 45,
                  "Avg_Building_Height_100m": 12.0
               },
               {
                  "NDVI": 0.05,
                  "NDBI": 0.10,
                  "Albedo": 0.22,
                  "D2W_meters": 800.0,
                  "D2R_HighCapacity_m": 150.0,
                  "D2R_Urban_m": 8.0,
                  "Tree_Density_50m": 1,
                  "Building_Density_100m": 20,
                  "Avg_Building_Height_100m": 6.0
               }
            ]'
   ```

* Ejemplo de respuesta: {"temperaturas_predichas": [46.21, 47.79], "unidad": "Celsius", "status": "success"}

> La primera ejecución puede tardar un poco ya que levanta el servidor

### El modelo se ha subido a Huggin Face Hub: https://huggingface.co/MiguelBarrera/testtfmmigue/tree/main


### Presentacion
https://docs.google.com/presentation/d/1hGu0jvKiqEuj3C7AutHoLEBcZL3e_DdKZwc3ZS06LOo/edit?usp=sharing