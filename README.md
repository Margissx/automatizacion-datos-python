# Automatización de limpieza de datos

Proyecto corto de portafolio que automatiza la limpieza y validación de un archivo CSV usando Python y Pandas.

## ¿Qué hace?

El programa:

1. Lee `datos.csv` con Pandas.
2. Corrige espacios innecesarios y formatos de texto.
3. Normaliza correos electrónicos y fechas.
4. Convierte edades escritas como texto a números.
5. Completa valores nulos con reglas simples.
6. Elimina registros duplicados.
7. Valida correos, edades, fechas y valores nulos.
8. Guarda el resultado en `datos_limpios.csv`.
9. Muestra un resumen del proceso en la consola.

Si `datos.csv` no existe, `main.py` lo crea automáticamente con datos de ejemplo.

## Requisitos

- Python 3.10 o superior
- Pandas

Instala la dependencia con:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde esta carpeta:

```bash
python main.py
```

La salida incluye:

- cantidad de registros iniciales;
- duplicados eliminados;
- valores corregidos;
- registros finales;
- resultado de la validación.

## Estructura

```text
automatizacion-datos/
├── datos.csv
├── datos_limpios.csv
├── main.py
├── requirements.txt
└── README.md
```

## Propósito profesional

Este ejercicio demuestra un flujo reproducible de preparación de datos: lectura, transformación, deduplicación, validación y exportación. El código está intencionalmente enfocado en una tarea concreta, sin interfaz gráfica, base de datos ni APIs.