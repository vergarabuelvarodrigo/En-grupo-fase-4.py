"""Demostracion automatica de operaciones validas e invalidas."""

from datetime import datetime, timedelta

from excepciones import SistemaFJError
from entidades import Cliente
from servicios import ServicioAsesoria, ServicioEquipo, ServicioSala
from sistema import SistemaFJ


def ejecutar_operacion(numero, nombre, accion, resultados, logger):
    """Ejecuta una operacion aislada para que un fallo no detenga el programa.

    Incluye try/except/else/finally y registra exitos y fallos en el log.
    """
    print(f"\nOPERACION {numero}: {nombre}")
    try:
        resultado = accion()
    except SistemaFJError as exc:
        logger.error("Operacion %s (%s) controlada: %s", numero, nombre, exc)
        print(f"ERROR CONTROLADO: {exc}")
        resultados.append(False)
        return None
    except Exception as exc:
        logger.exception("Error inesperado en operacion %s (%s)", numero, nombre)
        print(f"ERROR INESPERADO: {exc}")
        resultados.append(False)
        return None
    else:
        logger.info("Operacion %s (%s) ejecutada correctamente.", numero, nombre)
        print(f"OK: {resultado}")
        resultados.append(True)
        return resultado
    finally:
        print("Fin de la operacion.")
        print("-" * 72)


def ejecutar_demo(logger):
    """Ejecuta mas de diez operaciones, incluyendo pruebas validas e invalidas."""
    sistema = SistemaFJ(logger)
    resultados = []

    # Fechas futuras para que la demostracion funcione cualquier dia.
    manana = (datetime.now() + timedelta(days=1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    pasado_manana = (datetime.now() + timedelta(days=2)).replace(
        hour=14, minute=0, second=0, microsecond=0
    )

    print("=" * 72)
    print("SOFTWARE FJ - SISTEMA INTEGRAL DE CLIENTES, SERVICIOS Y RESERVAS")
    print("Demostracion academica: POO, validaciones, excepciones y archivo LOG")
    print("=" * 72)

    # 1. Registro correcto de cliente.
    cliente = ejecutar_operacion(
        1, "Registrar cliente valido",
        lambda: sistema.registrar_cliente(
            Cliente("Natalia Ejemplo", "CC1234567", "natalia@example.com", "3001234567")
        ), resultados, logger
    )
    cliente_obj = sistema.clientes[0] if sistema.clientes else None

    # 2. Registro incorrecto de cliente: correo no valido.
    ejecutar_operacion(
        2, "Rechazar cliente con correo invalido",
        lambda: sistema.registrar_cliente(
            Cliente("Carlos Prueba", "CC7654321", "correo-no-valido", "3017654321")
        ), resultados, logger
    )

    # 3. Evitar documentos duplicados.
    ejecutar_operacion(
        3, "Rechazar documento de cliente duplicado",
        lambda: sistema.registrar_cliente(
            Cliente("Otra Persona", "CC1234567", "otra@example.com", "3021234567")
        ), resultados, logger
    )

    # 4. Registrar una sala.
    ejecutar_operacion(
        4, "Registrar servicio de sala",
        lambda: sistema.registrar_servicio(
            ServicioSala("Sala Ejecutiva", "Sala para reuniones y capacitaciones", 80000, 20, True)
        ), resultados, logger
    )
    sala = sistema.servicios[-1] if sistema.servicios else None

    # 5. Registrar equipos.
    ejecutar_operacion(
        5, "Registrar servicio de alquiler de equipos",
        lambda: sistema.registrar_servicio(
            ServicioEquipo("Portatiles", "Alquiler de computadores portatiles", 25000, "Portatil", 2)
        ), resultados, logger
    )
    equipo = sistema.servicios[-1] if len(sistema.servicios) >= 2 else None

    # 6. Registrar asesoria.
    ejecutar_operacion(
        6, "Registrar servicio de asesoria especializada",
        lambda: sistema.registrar_servicio(
            ServicioAsesoria(
                "Asesoria Python", "Acompanamiento en programacion y desarrollo", 90000,
                "Programacion", "virtual"
            )
        ), resultados, logger
    )

    # 7. Rechazar un servicio mal formado (tarifa negativa).
    ejecutar_operacion(
        7, "Rechazar servicio con tarifa negativa",
        lambda: sistema.registrar_servicio(
            ServicioSala("Sala Incorrecta", "Servicio de prueba invalido", -5000, 10)
        ), resultados, logger
    )

    # 8. Crear una reserva correcta.
    reserva = None
    if cliente_obj is not None and sala is not None:
        reserva = ejecutar_operacion(
            8, "Crear reserva valida de sala",
            lambda: sistema.crear_reserva("CC1234567", sala.id, 2, manana),
            resultados, logger
        )

    # 9. Intentar reservar el mismo servicio en el mismo horario.
    if sala is not None:
        ejecutar_operacion(
            9, "Rechazar cruce de horario",
            lambda: sistema.crear_reserva("CC1234567", sala.id, 1, manana),
            resultados, logger
        )

    # 10. Confirmar la reserva.
    if reserva is not None:
        ejecutar_operacion(
            10, "Confirmar reserva",
            lambda: sistema.confirmar_reserva(reserva.id), resultados, logger
        )

        # 11. Procesar con impuesto y descuento.
        ejecutar_operacion(
            11, "Procesar reserva con impuesto del 19% y descuento del 10%",
            lambda: sistema.procesar_reserva(reserva.id, impuesto=0.19, descuento=0.10),
            resultados, logger
        )

        # 12. No permitir cancelar una reserva que ya fue procesada.
        ejecutar_operacion(
            12, "Rechazar cancelacion de reserva procesada",
            lambda: sistema.cancelar_reserva(reserva.id), resultados, logger
        )

    # 13. Crear una reserva de equipos en otra fecha.
    reserva_equipo = None
    if equipo is not None:
        reserva_equipo = ejecutar_operacion(
            13, "Crear reserva de equipos",
            lambda: sistema.crear_reserva("CC1234567", equipo.id, 3, pasado_manana),
            resultados, logger
        )

    # 14. Cancelar una reserva pendiente.
    if reserva_equipo is not None:
        ejecutar_operacion(
            14, "Cancelar reserva pendiente",
            lambda: sistema.cancelar_reserva(reserva_equipo.id), resultados, logger
        )

        # 15. No permitir confirmar una reserva cancelada.
        ejecutar_operacion(
            15, "Rechazar confirmacion de reserva cancelada",
            lambda: sistema.confirmar_reserva(reserva_equipo.id), resultados, logger
        )

    # 16. Probar duracion no valida y encadenamiento de excepciones.
    if equipo is not None:
        ejecutar_operacion(
            16, "Rechazar reserva con duracion cero",
            lambda: sistema.crear_reserva("CC1234567", equipo.id, 0, pasado_manana),
            resultados, logger
        )

    # 17. Probar las variantes de calculo con parametros opcionales.
    if sala is not None:
        ejecutar_operacion(
            17, "Calcular costo basico usando metodo opcional",
            lambda: sala.calcular_costo_basico(2), resultados, logger
        )

    print("\n" + "=" * 72)
    print("RESUMEN FINAL DE LA DEMOSTRACION")
    exitos = sum(resultados)
    fallidas = len(resultados) - exitos
    print(f"Operaciones ejecutadas: {len(resultados)}")
    print(f"Operaciones exitosas:   {exitos}")
    print(f"Operaciones con error controlado: {fallidas}")
    print(f"Clientes registrados:   {len(sistema.clientes)}")
    print(f"Servicios registrados:  {len(sistema.servicios)}")
    print(f"Reservas creadas:       {len(sistema.reservas)}")
    print("Archivo de eventos y errores: software_fj.log")
    print("El sistema termino la demostracion sin detenerse por los errores esperados.")
    print("=" * 72)

    logger.info(
        "Demostracion finalizada. Operaciones: %s | Exitos: %s | Fallidas: %s",
        len(resultados), exitos, fallidas
    )
