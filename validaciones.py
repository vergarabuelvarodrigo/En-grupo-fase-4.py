"""Validaciones, identificadores y configuracion del log."""

# logging para escribir el archivo de eventos y errores.
import logging
# math para comprobar que los numeros no sean infinitos ni NaN.
import math
# Path para ubicar el archivo de log junto al programa.
from pathlib import Path
# uuid para generar identificadores unicos.
import uuid

from excepciones import ValidacionError


def generar_id():
    """Genera un identificador corto y unico para cada objeto."""
    # uuid4 es aleatorio; se toman 8 caracteres y se pasan a mayuscula.
    return uuid.uuid4().hex[:8].upper()


def validar_texto(valor, campo, minimo=2, maximo=80):
    """Valida que un dato sea texto no vacio y dentro de la longitud permitida."""
    # Si no es texto (por ejemplo un numero o None) se rechaza de inmediato.
    if not isinstance(valor, str):
        raise ValidacionError(f"{campo} debe ser texto.")

    # strip() quita espacios al inicio y al final.
    valor = valor.strip()
    # Se comprueba que la longitud este entre el minimo y el maximo.
    if not minimo <= len(valor) <= maximo:
        raise ValidacionError(
            f"{campo} debe tener entre {minimo} y {maximo} caracteres."
        )
    return valor


def validar_numero(valor, campo, minimo=None, maximo=None, permitir_cero=True):
    """Valida numeros reales y evita valores infinitos, NaN y booleanos."""
    # En Python True y False cuentan como numeros, por eso se excluyen.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(f"{campo} debe ser un numero.")

    numero = float(valor)
    # isfinite es False para infinito y NaN.
    if not math.isfinite(numero):
        raise ValidacionError(f"{campo} debe ser un numero finito.")
    # Control del limite inferior (con opcion de excluir el propio minimo).
    if minimo is not None and (numero < minimo or (numero == minimo and not permitir_cero)):
        operador = "mayor que" if not permitir_cero else "mayor o igual a"
        raise ValidacionError(f"{campo} debe ser {operador} {minimo}.")
    # Control del limite superior.
    if maximo is not None and numero > maximo:
        raise ValidacionError(f"{campo} no puede ser superior a {maximo}.")
    return numero


def configurar_logger():
    """Crea el archivo software_fj.log y configura el registro de eventos."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Evita agregar el mismo manejador varias veces si se ejecuta desde un IDE.
    if not logger.handlers:
        try:
            # El log se guarda en la misma carpeta del programa.
            carpeta = Path(__file__).resolve().parent
        except NameError:
            # Si __file__ no existe (algunos IDE), se usa la carpeta actual.
            carpeta = Path.cwd()

        ruta_log = carpeta / "software_fj.log"
        manejador = logging.FileHandler(ruta_log, encoding="utf-8")
        # Formato de cada linea: fecha | nivel | mensaje.
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        manejador.setFormatter(formato)
        logger.addHandler(manejador)

    return logger
