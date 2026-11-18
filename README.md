f# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

Proyecto del curso **Programacion (213023)** - UNAD. Ejercicio 1 de la Fase 4.
Sistema orientado a objetos, sin bases de datos, con manejo avanzado de excepciones y archivo de log.

## Como ejecutarlo

Requisito: Python 3.10 o superior (recomendado 3.12). Todos los archivos `.py` deben estar en la misma carpeta.

```bash
python software_fj.py
```

Se ejecuta una demostracion automatica de **30 operaciones**: 16 exitosas, 13 errores controlados y 1 error inesperado provocado a proposito. El programa no se detiene y registra todo en `software_fj.log`, que se crea junto al programa. Al final espera un Enter para que la ventana no se cierre sola.

## Modulos

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquia de excepciones personalizadas (`SistemaFJError` y derivadas) |
| `validaciones.py` | `validar_texto`, `validar_numero`, generador de id y configuracion del log |
| `entidades.py` | `EntidadSistema` (abstracta) y `Cliente` con atributos privados |
| `servicios.py` | `Servicio` (abstracta), `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria` |
| `reserva.py` | `EstadoReserva` y `Reserva` (confirmar, cancelar, procesar) |
| `sistema.py` | `SistemaFJ`: listas en memoria, documentos unicos y cruces de horario |
| `demo.py` | Demostracion de 30 operaciones y manejo de errores por operacion |
| `software_fj.py` | Punto de entrada del programa |

## Aportes por integrante

### Rodrigo Jose Vergara Buelvas - version base

Yo desarrollé la base del sistema. Empecé desde cero con la estructura del proyecto en Python.

Mi aporte fue:
- Crear las excepciones personalizadas en excepciones.py, para que el programa no se caiga y muestre errores claros, y configurar el archivo de log donde queda guardado todo.
- Crear las validaciones en validaciones.py, para revisar que los textos, los números y los id estén bien escritos antes de guardarlos.
- Crear las clases principales: EntidadSistema, Cliente y Servicio, con sus atributos privados y sus validaciones.
- Crear los tres servicios especializados: Sala, Equipo y Asesoría, cada uno con sus propias reglas.
- Crear la clase Reserva con sus estados, el gestor SistemaFJ que une a los clientes, servicios y reservas, y la demostración inicial de 17 operaciones.

Lo hice de esta forma para que el sistema quedará ordenado por modulo, fuera fácil de entender y cumpliera con lo que pide la fase 4: poo, sin base de dato y con manejo avanzado de excepciones. 

### Liseth Johana Guillin Medina - revision, correcciones y mejoras
Trabajo hecho en su propia rama, con un issue y un pull request hacia `main`.

**Correcciones**
1. `servicios.py`: la tarifa base rechazaba exactamente 1 (`minimo=1` con `permitir_cero=False`); ahora acepta cualquier valor mayor que 0.
2. `servicios.py`: los atributos de los servicios eran publicos; ahora son privados con propiedades de solo lectura.
3. `servicios.py`: los errores de validacion salian como `ValidacionError` generico; ahora son `ServicioInvalidoError` con `raise ... from`.

**Mejoras**
1. `servicios.py`: metodo abstracto `validar_parametros`, sobrescrito en cada servicio con su limite de duracion (sala 12 h, equipo 72 h, asesoria 8 h).
2. `reserva.py` y `sistema.py`: la duracion se valida con las reglas del servicio concreto (polimorfismo).
3. `reserva.py`: `procesar` usa `try/except/else/finally` completo y `cancelar` recibe un motivo.
4. `entidades.py`: metodo `activar` y parametro `disponible` en los servicios.
5. `demo.py`: demostracion ampliada de 17 a 30 operaciones; el resumen separa errores controlados de inesperados.
6. `software_fj.py`: pausa final para que la ventana no se cierre sola.
7. Comentarios explicativos en todos los modulos.

## Requisitos del enunciado cubiertos

| Requisito | Donde |
|---|---|
| Clase abstracta de entidades | `EntidadSistema` |
| Cliente con validaciones y encapsulacion | `Cliente` |
| Clase abstracta `Servicio` y 3 servicios | `servicios.py` |
| Metodos sobrescritos (costo, descripcion, validacion) | `calcular_costo`, `describir`, `validar_parametros` |
| Reserva con cliente, servicio, duracion y estado | `Reserva`, `EstadoReserva` |
| Metodos sobrecargados | `calcular_costo_basico`, `calcular_costo_con_impuesto`, `calcular_costo_con_descuento` |
| try/except, else, finally y encadenamiento | `Reserva.procesar`, `ejecutar_operacion`, `Cliente.__init__` |
| Archivo de logs | `software_fj.log` |
| Al menos 10 operaciones completas | `demo.py` (30 operaciones) |
