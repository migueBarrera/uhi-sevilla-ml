# Urban Heat Island Predictor Sevilla (UHI-Predictor Sevilla)

## Definición del Proyecto
Para más detalles, consulta el archivo [definicion-proyecto.md](hito0/definicion-proyecto.md).

## Instrucciones para Levantar el Proyecto (Hito 0)

Estas instrucciones aplican únicamente al **Hito 0**.

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

5. Crea un archivo `.env` en el directorio `hito0` con el siguiente contenido:
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

6. Ejecuta el script principal:
   ```bash
   python main.py
   ```



   Firebase

   PAra levantar el firebase service 
   //TODO

   para ejecutar via curl:
   curl -s -w "\n⏱️ Tiempo total de respuesta: %{time_total} segundos\n" \
     -X POST "https://predict-temperature-bzqfrud2ua-ew.a.run.app" \
     -H "Content-Type: application/json" \
     -d '{
           "NDVI": 0.15,
           "NDBI": 0.25,
           "Albedo": 0.18,
           "D2W_meters": 1200.5,
           "D2R_HighCapacity_m": 350.0,
           "D2R_Urban_m": 15.0,
           "Tree_Density_50m": 3,
           "Building_Density_100m": 45,
           "Avg_Building_Height_100m": 12.0
         }'