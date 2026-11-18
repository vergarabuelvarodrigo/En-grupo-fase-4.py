# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

Proyecto del curso **Programacion (213023)** - UNAD. Ejercicio 1 de la Fase 4.
Sistema orientado a objetos, sin bases de datos, con manejo de excepciones y archivo de log.

## Como ejecutarlo

Requisito: Python 3.10 o superior.

```bash
python software_fj.py
```

Se ejecuta una demostracion de 17 operaciones (validas e invalidas) y se crea el archivo `software_fj.log`.

## Modulos

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Excepciones personalizadas |
| `validaciones.py` | Validaciones, generador de id y configuracion del log |
| `entidades.py` | `EntidadSistema` (abstracta) y `Cliente` |
| `servicios.py` | `Servicio` (abstracta), `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria` |
| `reserva.py` | `EstadoReserva` y `Reserva` |
| `sistema.py` | `SistemaFJ`, gestor con listas en memoria |
| `demo.py` | Demostracion de operaciones |
| `software_fj.py` | Punto de entrada |

## Integrantes
- Rodrigo Jose Vergara Buelvas: version base del sistema.
- Liseth Johana Guillin Medina: revision y mejoras (en su rama, ver pull requests).
