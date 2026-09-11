"""Automatización sencilla de limpieza y validación de datos con Pandas."""

from pathlib import Path
import re

import pandas as pd


CARPETA_PROYECTO = Path(__file__).resolve().parent
ARCHIVO_ENTRADA = CARPETA_PROYECTO / "datos.csv"
ARCHIVO_SALIDA = CARPETA_PROYECTO / "datos_limpios.csv"

DATOS_EJEMPLO = [
    {
        "nombre": "Ana López",
        "email": " ANA@EXAMPLE.COM ",
        "edad": 28,
        "ciudad": "Tegucigalpa ",
        "fecha_registro": "2026-01-05",
    },
    {
        "nombre": " Carlos Pérez ",
        "email": "carlos@example.com",
        "edad": "treinta",
        "ciudad": "san pedro sula",
        "fecha_registro": "15/01/2026",
    },
    {
        "nombre": "María Gómez",
        "email": "maria@example.com",
        "edad": "",
        "ciudad": " tegucigalpa",
        "fecha_registro": "2026/01/07",
    },
    {
        "nombre": "José Martínez",
        "email": "jose@example.com",
        "edad": 35,
        "ciudad": "Tegucigalpa",
        "fecha_registro": "2026-01-08",
    },
    {
        "nombre": " José Martínez ",
        "email": " JOSE@EXAMPLE.COM ",
        "edad": "35 años",
        "ciudad": "Tegucigalpa ",
        "fecha_registro": "08-01-2026",
    },
    {
        "nombre": "Lucía Reyes",
        "email": "lucia@example.com",
        "edad": 31,
        "ciudad": "San Pedro Sula",
        "fecha_registro": "2026-01-09",
    },
    {
        "nombre": "Pedro Castillo",
        "email": "pedro@example.com",
        "edad": 42,
        "ciudad": "",
        "fecha_registro": "2026-01-10",
    },
]


def convertir_fecha(valor: object) -> pd.Timestamp:
    """Convierte fechas ISO y fechas día/mes/año sin intercambiar sus partes."""
    if pd.isna(valor):
        return pd.NaT

    texto = str(valor).strip()
    if re.fullmatch(r"\d{4}[-/]\d{2}[-/]\d{2}", texto):
        formato = "%Y-%m-%d" if "-" in texto else "%Y/%m/%d"
        return pd.to_datetime(texto, format=formato, errors="coerce")

    return pd.to_datetime(texto, dayfirst=True, errors="coerce")


def crear_datos_ejemplo_si_no_existen() -> None:
    """Crea el CSV inicial solo si todavía no existe."""
    if not ARCHIVO_ENTRADA.exists():
        pd.DataFrame(DATOS_EJEMPLO).to_csv(ARCHIVO_ENTRADA, index=False)


def contar_cambios(datos_originales: pd.DataFrame, datos_limpios: pd.DataFrame) -> int:
    """Cuenta las celdas cuyo valor cambió durante la limpieza."""
    originales = datos_originales.fillna("<NULO>").astype(str)
    limpios = datos_limpios.fillna("<NULO>").astype(str)
    return int((originales != limpios).sum().sum())


def limpiar_datos(datos: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    """Normaliza texto, edades y fechas, y elimina duplicados."""
    datos_limpios = datos.copy()

    columnas_texto = ["nombre", "email", "ciudad"]
    for columna in columnas_texto:
        datos_limpios[columna] = datos_limpios[columna].astype("string").str.strip()

    datos_limpios["nombre"] = datos_limpios["nombre"].str.replace(
        r"\s+", " ", regex=True
    )
    datos_limpios["email"] = datos_limpios["email"].str.lower()
    datos_limpios["ciudad"] = datos_limpios["ciudad"].str.title()
    datos_limpios["ciudad"] = datos_limpios["ciudad"].fillna("Desconocida")

    edades = (
        datos_limpios["edad"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace({"treinta": "30"})
        .str.extract(r"(\d+)", expand=False)
    )
    datos_limpios["edad"] = pd.to_numeric(edades, errors="coerce")
    edad_mediana = datos_limpios["edad"].median()
    datos_limpios["edad"] = datos_limpios["edad"].fillna(edad_mediana).astype(int)

    fechas = datos_limpios["fecha_registro"].apply(convertir_fecha)
    datos_limpios["fecha_registro"] = fechas.dt.strftime("%Y-%m-%d")

    valores_corregidos = contar_cambios(datos, datos_limpios)
    duplicados_eliminados = int(datos_limpios.duplicated().sum())
    datos_limpios = datos_limpios.drop_duplicates().reset_index(drop=True)

    return datos_limpios, duplicados_eliminados, valores_corregidos


def validar_datos(datos: pd.DataFrame) -> list[str]:
    """Aplica validaciones básicas y devuelve los errores encontrados."""
    errores: list[str] = []
    columnas_requeridas = {"nombre", "email", "edad", "ciudad", "fecha_registro"}

    if not columnas_requeridas.issubset(datos.columns):
        faltantes = columnas_requeridas.difference(datos.columns)
        errores.append(f"Faltan columnas requeridas: {', '.join(sorted(faltantes))}")
        return errores

    if datos.empty:
        errores.append("El archivo no contiene registros.")
        return errores

    if datos[list(columnas_requeridas)].isna().any().any():
        errores.append("Existen valores nulos en las columnas requeridas.")

    emails_validos = datos["email"].astype("string").str.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        na=False,
    )
    if not emails_validos.all():
        errores.append("Existen correos electrónicos con formato inválido.")

    if not datos["edad"].between(18, 100).all():
        errores.append("Existen edades fuera del rango permitido (18 a 100).")

    fechas_validas = pd.to_datetime(
        datos["fecha_registro"],
        format="%Y-%m-%d",
        errors="coerce",
    )
    if fechas_validas.isna().any():
        errores.append("Existen fechas con formato inválido.")

    return errores


def imprimir_resumen(
    registros_iniciales: int,
    duplicados_eliminados: int,
    valores_corregidos: int,
    registros_finales: int,
    errores: list[str],
) -> None:
    """Muestra el resultado del proceso en consola."""
    print("\n=== Automatización de limpieza de datos ===")
    print(f"Registros iniciales: {registros_iniciales}")
    print(f"Duplicados eliminados: {duplicados_eliminados}")
    print(f"Valores corregidos: {valores_corregidos}")
    print(f"Registros finales: {registros_finales}")
    if errores:
        print("Validación: ERROR")
        for error in errores:
            print(f"- {error}")
    else:
        print("Validación: OK")
    print(f"Archivo generado: {ARCHIVO_SALIDA.name}")


def main() -> None:
    crear_datos_ejemplo_si_no_existen()
    datos_originales = pd.read_csv(ARCHIVO_ENTRADA)
    datos_limpios, duplicados, correcciones = limpiar_datos(datos_originales)
    errores = validar_datos(datos_limpios)

    if errores:
        raise ValueError("La validación de los datos falló: " + "; ".join(errores))

    datos_limpios.to_csv(ARCHIVO_SALIDA, index=False)
    imprimir_resumen(
        registros_iniciales=len(datos_originales),
        duplicados_eliminados=duplicados,
        valores_corregidos=correcciones,
        registros_finales=len(datos_limpios),
        errores=errores,
    )


if __name__ == "__main__":
    main()