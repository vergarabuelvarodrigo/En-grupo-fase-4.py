# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

Proyecto del curso **Programacion (213023)** - UNAD, Ingenieria de Sistemas.
Ejercicio 1 (Fase 4): sistema orientado a objetos, sin bases de datos, con manejo avanzado de excepciones.

## Como ejecutarlo

Requisito: Python 3.10 o superior (recomendado 3.12).

```bash
python software_fj.py
```

Se ejecuta una demostracion automatica de **30 operaciones** (16 exitosas, 13 errores controlados y 1 error inesperado provocado a proposito). El programa no se detiene en ningun caso y registra todo en `software_fj.log`, que se crea solo junto al programa.

## Estructura del codigo (`software_fj.py`)

| Seccion | Contenido |
|---|---|
| 1 | Excepciones personalizadas (jerarquia desde `SistemaFJError`) |
| 2 | Funciones de validacion (`validar_texto`, `validar_numero`) y configuracion del log |
| 3 | Clase abstracta `EntidadSistema` |
| 4 | Clase `Cliente` (atributos privados y validaciones) |
| 5 | Clase abstracta `Servicio` y servicios `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria` |
| 6 | Clase `Reserva` y enumeracion `EstadoReserva` |
| 7 | Clase `SistemaFJ` (listas internas de clientes, servicios y reservas) |
| 8 | Demostracion de operaciones (`ejecutar_operacion`, `ejecutar_demo`) |
| 9 | Punto de entrada del programa |

## Aportes por integrante

### Integrante 1 (companero) - Desarrollo de la base del sistema
- Jerarquia de excepciones personalizadas y funciones de validacion.
- Configuracion del archivo de logs.
- Clases `EntidadSistema`, `Cliente`, `Servicio` y los tres servicios especializados.
- Clase `Reserva` con estados, confirmacion, cancelacion y procesamiento.
- Gestor `SistemaFJ` con listas en memoria, validacion de documentos duplicados y deteccion de cruces de horario.
- Demostracion inicial de 17 operaciones.

### Liseth - Revision, correcciones y mejoras
**Correcciones**
1. La tarifa base rechazaba un valor de exactamente 1 (`minimo=1` con `permitir_cero=False`); ahora acepta cualquier valor mayor que 0.
2. Los atributos de los servicios (`capacidad`, `proyector`, `tipo_equipo`, `cantidad`, `especialidad`, `modalidad`) eran publicos y se podian modificar sin validar; ahora son privados con propiedades de solo lectura.
3. Algunos errores de validacion de los servicios salian como `ValidacionError` generico; ahora se convierten en `ServicioInvalidoError` con encadenamiento (`raise ... from`).

**Mejoras e implementaciones nuevas**
1. Metodo abstracto `validar_parametros` en `Servicio`, sobrescrito en cada servicio con su propio limite de duracion (sala 12 h, equipo 72 h, asesoria 8 h). El enunciado pide sobrescribir calcular costos, describir y validar parametros.
2. `Reserva` y `SistemaFJ.crear_reserva` validan la duracion con las reglas del servicio concreto (polimorfismo).
3. `Reserva.procesar` ahora usa `try/except/else/finally` completo.
4. Parametro `disponible` en los servicios, para poder probar el caso de servicio no disponible.
5. `Reserva.cancelar` recibe un motivo que queda en el log, y `Cliente.activar` complementa a `desactivar`.
6. Demostracion ampliada de 17 a 30 operaciones: duracion fuera de limite, servicio no disponible, cliente no registrado, fecha pasada, cliente inactivo, descuento fuera de rango (calculo inconsistente), parametros faltantes y comparacion polimorfica.
7. El resumen final separa errores controlados de errores inesperados.
8. Comentarios en el codigo explicando cada bloque, como pide la guia de la actividad.

## Requisitos del enunciado cubiertos

| Requisito | Donde |
|---|---|
| Clase abstracta de entidades | `EntidadSistema` |
| Cliente con validaciones y encapsulacion | `Cliente` |
| Clase abstracta `Servicio` + 3 servicios | `Servicio`, `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria` |
| Polimorfismo y metodos sobrescritos (costo, descripcion, validacion) | `calcular_costo`, `describir`, `validar_parametros` |
| Reserva con cliente, servicio, duracion y estado | `Reserva`, `EstadoReserva` |
| Metodos sobrecargados | `calcular_costo_basico`, `calcular_costo_con_impuesto`, `calcular_costo_con_descuento`, `calcular_costo` |
| try/except, else, finally y encadenamiento | `Reserva.procesar`, `ejecutar_operacion`, `Cliente.__init__` |
| Archivo de logs | `software_fj.log` |
| Al menos 10 operaciones completas | `ejecutar_demo` (30 operaciones) |
