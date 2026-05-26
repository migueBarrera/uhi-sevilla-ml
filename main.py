import os

from infraestructura import ejecutar_infraestructura
from descarga_datos import ejecutar_descarga
from procesar_datos import ejecutar_procesamiento


def main():
    raw_dir = os.path.join("outputs", "raw")
    archivo_tiff = os.path.join(raw_dir, "sevilla_dataset.tif")
    archivo_arbolado = os.path.join(raw_dir, "arbolado_sevilla.csv")
    archivo_carreteras = os.path.join(raw_dir, "carreteras_sevilla.csv")
    archivo_edificios = os.path.join(raw_dir, "edificios_sevilla.csv")


    #ejecutar_infraestructura()
    #ejecutar_descarga()
    ejecutar_procesamiento(
        archivo_local_tiff=archivo_tiff,
        arbolado_csv=archivo_arbolado,
        carreteras_csv=archivo_carreteras,
        edificios_csv=archivo_edificios
    )
    print("\n🎉 ¡Pipeline completado! Infraestructura, descarga y procesamiento ejecutados en scripts separados.")


if __name__ == "__main__":
    main()