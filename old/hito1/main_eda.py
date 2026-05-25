import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuración de estilo para visualizaciones
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Crear carpeta para guardar gráficos
OUTPUT_PLOTS_DIR = "outputs/eda_plots"
os.makedirs(OUTPUT_PLOTS_DIR, exist_ok=True)

print("=" * 80)
print("ANÁLISIS EXPLORATORIO DE DATOS (EDA) - URBAN HEAT ISLAND SEVILLA")
print("=" * 80)

# ==========================================
# 1. CARGA DE DATOS
# ==========================================
print("\n📊 FASE 1: Carga de Datos")
print("-" * 80)

CSV_PATH = "outputs/sevilla_pixel_data.csv"
df = pd.read_csv(CSV_PATH)

print(f"✅ Dataset cargado exitosamente desde: {CSV_PATH}")
print(f"   Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas")

# ==========================================
# 2. INSPECCIÓN INICIAL
# ==========================================
print("\n" + "=" * 80)
print("📋 FASE 2: Inspección Inicial")
print("=" * 80)

print("\n--- Primeros 5 Registros ---")
print(df.head())

print("\n--- Información General del Dataset ---")
print(df.info())

print("\n--- Tipos de Datos ---")
print(df.dtypes)

print("\n--- Valores Nulos por Columna ---")
print(df.isnull().sum())

print("\n--- Duplicados ---")
print(f"Filas duplicadas: {df.duplicated().sum()}")

# ==========================================
# 3. ESTADÍSTICAS DESCRIPTIVAS
# ==========================================
print("\n" + "=" * 80)
print("📈 FASE 3: Estadísticas Descriptivas")
print("=" * 80)

# Estadísticas básicas
print("\n--- Estadísticas Generales ---")
print(df.describe())

# Estadísticas adicionales detalladas
print("\n--- Estadísticas Detalladas por Variable ---")
for col in df.columns:
    print(f"\n🔹 {col}:")
    print(f"   Media:              {df[col].mean():.6f}")
    print(f"   Mediana:            {df[col].median():.6f}")
    print(f"   Moda:               {df[col].mode().values[0] if not df[col].mode().empty else 'N/A':.6f}")
    print(f"   Desviación Estándar: {df[col].std():.6f}")
    print(f"   Varianza:           {df[col].var():.6f}")
    print(f"   Mínimo:             {df[col].min():.6f}")
    print(f"   Máximo:             {df[col].max():.6f}")
    print(f"   Rango:              {df[col].max() - df[col].min():.6f}")
    print(f"   Percentil 25:       {df[col].quantile(0.25):.6f}")
    print(f"   Percentil 50:       {df[col].quantile(0.50):.6f}")
    print(f"   Percentil 75:       {df[col].quantile(0.75):.6f}")
    print(f"   Percentil 90:       {df[col].quantile(0.90):.6f}")
    print(f"   Percentil 95:       {df[col].quantile(0.95):.6f}")
    print(f"   Percentil 99:       {df[col].quantile(0.99):.6f}")
    print(f"   Asimetría (Skew):   {df[col].skew():.6f}")
    print(f"   Curtosis:           {df[col].kurtosis():.6f}")

# ==========================================
# 4. IDENTIFICACIÓN DE VALORES ATÍPICOS
# ==========================================
print("\n" + "=" * 80)
print("🔍 FASE 4: Identificación de Valores Atípicos (Outliers)")
print("=" * 80)

for col in df.columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outliers_count = len(outliers)
    outliers_percent = (outliers_count / len(df)) * 100
    
    print(f"\n🔹 {col}:")
    print(f"   Límite Inferior (Q1 - 1.5*IQR): {lower_bound:.6f}")
    print(f"   Límite Superior (Q3 + 1.5*IQR): {upper_bound:.6f}")
    print(f"   Outliers detectados: {outliers_count:,} ({outliers_percent:.2f}%)")
    
    # Z-score para outliers extremos
    z_scores = np.abs(stats.zscore(df[col]))
    extreme_outliers = (z_scores > 3).sum()
    print(f"   Outliers extremos (|Z| > 3): {extreme_outliers:,}")

# ==========================================
# 5. ANÁLISIS DE CORRELACIONES
# ==========================================
print("\n" + "=" * 80)
print("🔗 FASE 5: Análisis de Correlaciones")
print("=" * 80)

correlation_matrix = df.corr()
print("\n--- Matriz de Correlación (Pearson) ---")
print(correlation_matrix)

print("\n--- Correlaciones con Variable Objetivo (LST_Target) ---")
correlations_with_target = correlation_matrix['LST_Target'].sort_values(ascending=False)
print(correlations_with_target)

# ==========================================
# 6. VISUALIZACIONES
# ==========================================
print("\n" + "=" * 80)
print("📊 FASE 6: Generación de Visualizaciones")
print("=" * 80)

# 6.1 Histogramas de todas las variables
print("\n📈 Generando histogramas...")
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for idx, col in enumerate(df.columns):
    axes[idx].hist(df[col], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    axes[idx].set_title(f'Distribución de {col}', fontsize=12, fontweight='bold')
    axes[idx].set_xlabel(col)
    axes[idx].set_ylabel('Frecuencia')
    axes[idx].grid(True, alpha=0.3)
    
    # Añadir líneas de media y mediana
    axes[idx].axvline(df[col].mean(), color='red', linestyle='--', linewidth=2, label='Media')
    axes[idx].axvline(df[col].median(), color='green', linestyle='--', linewidth=2, label='Mediana')
    axes[idx].legend()

# Eliminar subplot vacío
fig.delaxes(axes[-1])

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/1_histogramas.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/1_histogramas.png")
plt.close()

# 6.2 Boxplots para detectar outliers
print("\n📦 Generando boxplots...")
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for idx, col in enumerate(df.columns):
    axes[idx].boxplot(df[col], vert=True, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', alpha=0.7),
                     medianprops=dict(color='red', linewidth=2),
                     whiskerprops=dict(linewidth=1.5),
                     capprops=dict(linewidth=1.5))
    axes[idx].set_title(f'Boxplot de {col}', fontsize=12, fontweight='bold')
    axes[idx].set_ylabel(col)
    axes[idx].grid(True, alpha=0.3)

# Eliminar subplot vacío
fig.delaxes(axes[-1])

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/2_boxplots.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/2_boxplots.png")
plt.close()

# 6.3 Matriz de correlación (Heatmap)
print("\n🔥 Generando mapa de calor de correlaciones...")
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
plt.title('Matriz de Correlación entre Variables', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/3_correlacion_heatmap.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/3_correlacion_heatmap.png")
plt.close()

# 6.4 Pairplot / Diagramas de dispersión
print("\n🔵 Generando diagramas de dispersión (Pairplot)...")
# Solo tomamos una muestra para que sea más rápido (si el dataset es muy grande)
sample_size = min(10000, len(df))
df_sample = df.sample(n=sample_size, random_state=42)

pairplot = sns.pairplot(df_sample, diag_kind='kde', plot_kws={'alpha': 0.6, 's': 10})
pairplot.fig.suptitle('Diagramas de Dispersión entre Variables', y=1.01, fontsize=14, fontweight='bold')
plt.savefig(f"{OUTPUT_PLOTS_DIR}/4_pairplot.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/4_pairplot.png")
plt.close()

# 6.5 Scatter plots específicos (Features vs Target)
print("\n📍 Generando scatter plots de Features vs LST_Target...")
features = [col for col in df.columns if col != 'LST_Target']

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for idx, feature in enumerate(features):
    # Usar muestra para gráficos más rápidos si el dataset es muy grande
    sample = df_sample if len(df) > 10000 else df
    
    scatter = axes[idx].scatter(sample[feature], sample['LST_Target'], 
                               c=sample['LST_Target'], cmap='YlOrRd', 
                               alpha=0.5, s=5, edgecolors='none')
    axes[idx].set_xlabel(feature, fontsize=11)
    axes[idx].set_ylabel('LST_Target (°C)', fontsize=11)
    axes[idx].set_title(f'{feature} vs LST_Target\n(Correlación: {correlation_matrix.loc[feature, "LST_Target"]:.3f})',
                       fontsize=11, fontweight='bold')
    axes[idx].grid(True, alpha=0.3)
    
    # Añadir línea de tendencia
    z = np.polyfit(sample[feature], sample['LST_Target'], 1)
    p = np.poly1d(z)
    axes[idx].plot(sample[feature], p(sample[feature]), "r--", alpha=0.8, linewidth=2)
    
    plt.colorbar(scatter, ax=axes[idx], label='LST °C')

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/5_scatter_features_vs_target.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/5_scatter_features_vs_target.png")
plt.close()

# 6.6 Distribución espacial de LST
print("\n🗺️ Generando mapa de distribución espacial de LST...")
fig, ax = plt.subplots(figsize=(14, 10))

# Usar muestra si el dataset es muy grande
spatial_sample = df.sample(n=min(50000, len(df)), random_state=42)

scatter = ax.scatter(spatial_sample['Longitude'], spatial_sample['Latitude'], 
                    c=spatial_sample['LST_Target'], cmap='hot', 
                    s=1, alpha=0.6, edgecolors='none')
ax.set_xlabel('Longitud', fontsize=12)
ax.set_ylabel('Latitud', fontsize=12)
ax.set_title('Distribución Espacial de la Temperatura Superficial (LST)', 
             fontsize=14, fontweight='bold')
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Temperatura (°C)', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/6_mapa_espacial_lst.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/6_mapa_espacial_lst.png")
plt.close()

# 6.7 Violin plots para comparación de distribuciones
print("\n🎻 Generando violin plots...")
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for idx, col in enumerate(df.columns):
    # Usar muestra para violin plots
    sample = df_sample if len(df) > 10000 else df
    
    parts = axes[idx].violinplot([sample[col]], positions=[0], widths=0.7,
                                showmeans=True, showmedians=True)
    
    # Personalizar colores
    for pc in parts['bodies']:
        pc.set_facecolor('lightcoral')
        pc.set_alpha(0.7)
    
    axes[idx].set_title(f'Violin Plot de {col}', fontsize=12, fontweight='bold')
    axes[idx].set_ylabel(col)
    axes[idx].set_xticks([])
    axes[idx].grid(True, alpha=0.3, axis='y')

# Eliminar subplot vacío
fig.delaxes(axes[-1])

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/7_violin_plots.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/7_violin_plots.png")
plt.close()

# 6.8 Análisis de densidad 2D (NDVI vs NDBI)
print("\n🌈 Generando gráfico de densidad 2D (NDVI vs NDBI)...")
fig, ax = plt.subplots(figsize=(12, 10))

# Usar muestra para gráficos de densidad
density_sample = df.sample(n=min(20000, len(df)), random_state=42)

hexbin = ax.hexbin(density_sample['NDVI'], density_sample['NDBI'], 
                   gridsize=50, cmap='YlGnBu', mincnt=1)
ax.set_xlabel('NDVI (Índice de Vegetación)', fontsize=12)
ax.set_ylabel('NDBI (Índice de Construcción)', fontsize=12)
ax.set_title('Densidad 2D: NDVI vs NDBI', fontsize=14, fontweight='bold')
cbar = plt.colorbar(hexbin, ax=ax)
cbar.set_label('Densidad de píxeles', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PLOTS_DIR}/8_densidad_2d_ndvi_ndbi.png", dpi=300, bbox_inches='tight')
print(f"✅ Guardado: {OUTPUT_PLOTS_DIR}/8_densidad_2d_ndvi_ndbi.png")
plt.close()

# ==========================================
# 7. RESUMEN EJECUTIVO
# ==========================================
print("\n" + "=" * 80)
print("📝 FASE 7: Resumen Ejecutivo del EDA")
print("=" * 80)

print(f"""
RESUMEN DEL ANÁLISIS EXPLORATORIO DE DATOS
{'=' * 80}

1. INFORMACIÓN GENERAL:
   - Total de píxeles analizados: {len(df):,}
   - Variables: {', '.join(df.columns)}
   - Valores nulos: {df.isnull().sum().sum()}
   - Duplicados: {df.duplicated().sum()}

2. VARIABLE OBJETIVO (LST_Target):
   - Temperatura media: {df['LST_Target'].mean():.2f}°C
   - Temperatura mínima: {df['LST_Target'].min():.2f}°C
   - Temperatura máxima: {df['LST_Target'].max():.2f}°C
   - Desviación estándar: {df['LST_Target'].std():.2f}°C
   - Rango térmico: {df['LST_Target'].max() - df['LST_Target'].min():.2f}°C

3. CORRELACIONES MÁS FUERTES CON LST:
{correlations_with_target.to_string()}

4. PATRONES IDENTIFICADOS:
   - NDVI: Rango desde {df['NDVI'].min():.3f} hasta {df['NDVI'].max():.3f}
   - NDBI: Rango desde {df['NDBI'].min():.3f} hasta {df['NDBI'].max():.3f}
   - Distancia al agua: De {df['D2W_meters'].min():.0f}m a {df['D2W_meters'].max():.0f}m

5. GRÁFICOS GENERADOS:
   ✓ Histogramas de distribución
   ✓ Boxplots para detección de outliers
   ✓ Mapa de calor de correlaciones
   ✓ Pairplot de relaciones multivariadas
   ✓ Scatter plots de features vs target
   ✓ Mapa espacial de LST
   ✓ Violin plots
   ✓ Gráfico de densidad 2D

Todos los gráficos han sido guardados en: {OUTPUT_PLOTS_DIR}/

{'=' * 80}
""")

print("\n✅ Análisis Exploratorio de Datos completado exitosamente.")
print(f"📁 Todos los gráficos guardados en: {OUTPUT_PLOTS_DIR}/")
print("=" * 80)
