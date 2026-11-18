"""Sistema Integral de Gestion de Clientes, Servicios y Reservas - Software FJ.

Proyecto academico de Programacion Orientada a Objetos.
- No utiliza bases de datos: los datos se mantienen en listas y objetos.
- Registra eventos y errores en software_fj.log.
- Incluye una demostracion automatica con operaciones validas e invalidas.

Estructura: excepciones, validaciones, entidades, servicios, reserva,
sistema y demo (un modulo por archivo).

Ejecucion: python software_fj.py
Requisito: Python 3.10 o superior (recomendado Python 3.12).
"""

from demo import ejecutar_demo
from validaciones import configurar_logger


if __name__ == "__main__":
    registro = configurar_logger()
    try:
        ejecutar_demo(registro)
    except KeyboardInterrupt:
        registro.warning("Ejecucion interrumpida manualmente por el usuario.")
        print("\nLa ejecucion fue interrumpida por el usuario.")
    except Exception:
        registro.exception("Fallo no controlado en el punto de entrada.")
        print("Ocurrio un error inesperado. Revise software_fj.log para mas detalles.")
