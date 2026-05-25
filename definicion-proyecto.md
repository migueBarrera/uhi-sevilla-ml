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
