"""Demostracion automatica de operaciones validas e invalidas."""

# datetime para fechas y timedelta para sumar horas.
from datetime import datetime, timedelta

from excepciones import SistemaFJError
from entidades import Cliente
from servicios import ServicioAsesoria, ServicioEquipo, ServicioSala
from sistema import SistemaFJ


def ejecutar_operacion(numero, nombre, accion, resultados, logger):
    """Ejecuta una operacion aislada para que un fallo no detenga el programa.

    Incluye try/except/else/finally y registra exitos y fallos en el log.
    En "resultados" se guarda "ok", "controlado" o "inesperado".
    """
    print(f"\nOPERACION {numero}: {nombre}")
    try:
        # accion es una funcion sin parametros (lambda) con la operacion a probar.
        resultado = accion()
    except SistemaFJError as exc:
        # Error previsto por el sistema (datos invalidos, estado incorrecto...).
        logger.error("Operacion %s (%s) controlada: %s", numero, nombre, exc)
        print(f"ERROR CONTROLADO ({type(exc).__name__}): {exc}")
        resultados.append("controlado")
        return None
    except Exception as exc:
        # Error no previsto (por ejemplo, un parametro que falta).
        logger.exception("Error inesperado en operacion %s (%s)", numero, nombre)
        print(f"ERROR INESPERADO ({type(exc).__name__}): {exc}")
        resultados.append("inesperado")
        return None
    else:
        logger.info("Operacion %s (%s) ejecutada correctamente.", numero, nombre)
        print(f"OK: {resultado}")
        resultados.append("ok")
        return resultado
    finally:
        print("Fin de la operacion.")
        print("-" * 72)


def ejecutar_demo(logger):
    """Ejecuta mas de diez operaciones, incluyendo pruebas validas e invalidas."""
    sistema = SistemaFJ(logger)
    resultados = []
    logger.info("===== INICIO DE LA DEMOSTRACION =====")

    # Fechas futuras para que la demostracion funcione cualquier dia.
    manana = (datetime.now() + timedelta(days=1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    pasado_manana = (datetime.now() + timedelta(days=2)).replace(
        hour=14, minute=0, second=0, microsecond=0
    )
    en_tres_dias = (datetime.now() + timedelta(days=3)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    print("=" * 72)
    print("SOFTWARE FJ - SISTEMA INTEGRAL DE CLIENTES, SERVICIOS Y RESERVAS")
    print("Demostracion academica: POO, validaciones, excepciones y archivo LOG")
    print("=" * 72)

    # 1. Registro correcto de cliente.
    ejecutar_operacion(
        1, "Registrar cliente valido",
        lambda: sistema.registrar_cliente(
            Cliente("Natalia Ejemplo", "CC1234567", "natalia@example.com", "3001234567")
        ), resultados, logger
    )

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
                "Programacion", "presencial"
            )
        ), resultados, logger
    )
    asesoria = sistema.servicios[-1] if len(sistema.servicios) >= 3 else None

    # 7. Rechazar un servicio mal formado (tarifa negativa).
    ejecutar_operacion(
        7, "Rechazar servicio con tarifa negativa",
        lambda: sistema.registrar_servicio(
            ServicioSala("Sala Incorrecta", "Servicio de prueba invalido", -5000, 10)
        ), resultados, logger
    )

    # 8. Crear una reserva correcta.
    reserva = None
    if sala is not None:
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
            lambda: sistema.cancelar_reserva(reserva_equipo.id, "El cliente ya no la necesita"),
            resultados, logger
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

    # --- Operaciones agregadas en la revision ---

    # 18. Duracion que supera el limite propio de la sala (12 h).
    if sala is not None:
        ejecutar_operacion(
            18, "Rechazar reserva de sala por 20 horas (limite 12 h)",
            lambda: sistema.crear_reserva("CC1234567", sala.id, 20, en_tres_dias),
            resultados, logger
        )

    # 19. Servicio marcado como no disponible.
    ejecutar_operacion(
        19, "Registrar sala en mantenimiento (no disponible)",
        lambda: sistema.registrar_servicio(
            ServicioSala("Sala Mantenimiento", "Sala cerrada por remodelacion", 60000, 8,
                         False, disponible=False)
        ), resultados, logger
    )
    sala_cerrada = sistema.servicios[-1] if len(sistema.servicios) >= 4 else None
    if sala_cerrada is not None:
        ejecutar_operacion(
            20, "Rechazar reserva de un servicio no disponible",
            lambda: sistema.crear_reserva("CC1234567", sala_cerrada.id, 2, en_tres_dias),
            resultados, logger
        )

    # 21. Cliente que no existe en el sistema.
    if sala is not None:
        ejecutar_operacion(
            21, "Rechazar reserva de un cliente no registrado",
            lambda: sistema.crear_reserva("CC0000000", sala.id, 2, en_tres_dias),
            resultados, logger
        )

    # 22. Fecha en el pasado.
    if sala is not None:
        ejecutar_operacion(
            22, "Rechazar reserva con fecha pasada",
            lambda: sistema.crear_reserva(
                "CC1234567", sala.id, 2, datetime.now() - timedelta(days=1)
            ), resultados, logger
        )

    # 23. Cliente inactivo.
    def registrar_y_desactivar():
        # Se registra el cliente y luego se desactiva para probar la regla.
        sistema.registrar_cliente(
            Cliente("Pedro Inactivo", "CC9999999", "pedro@example.com", "3205550000")
        )
        cliente_nuevo = sistema.buscar_cliente("CC9999999")
        cliente_nuevo.desactivar()
        return cliente_nuevo.describir()

    ejecutar_operacion(
        23, "Registrar un segundo cliente y desactivarlo",
        registrar_y_desactivar, resultados, logger
    )
    if sala is not None:
        ejecutar_operacion(
            24, "Rechazar reserva de un cliente inactivo",
            lambda: sistema.crear_reserva("CC9999999", sala.id, 2, en_tres_dias),
            resultados, logger
        )

    # 25-27. Calculo inconsistente: descuento fuera de rango y luego correcto.
    reserva_asesoria = None
    if asesoria is not None:
        reserva_asesoria = ejecutar_operacion(
            25, "Crear reserva de asesoria presencial (2 h)",
            lambda: sistema.crear_reserva("CC1234567", asesoria.id, 2, en_tres_dias),
            resultados, logger
        )
    if reserva_asesoria is not None:
        ejecutar_operacion(
            26, "Confirmar reserva de asesoria",
            lambda: sistema.confirmar_reserva(reserva_asesoria.id), resultados, logger
        )
        ejecutar_operacion(
            27, "Rechazar procesamiento con descuento del 150% (calculo inconsistente)",
            lambda: sistema.procesar_reserva(reserva_asesoria.id, descuento=1.5),
            resultados, logger
        )
        ejecutar_operacion(
            28, "Procesar la misma reserva con datos correctos",
            lambda: sistema.procesar_reserva(reserva_asesoria.id, descuento=0.05),
            resultados, logger
        )

    # 29. Parametros faltantes: error inesperado que no detiene el programa.
    ejecutar_operacion(
        29, "Llamar a crear_reserva sin los parametros obligatorios",
        lambda: sistema.crear_reserva("CC1234567"), resultados, logger
    )

    # 30. Polimorfismo: el mismo metodo da resultados distintos segun el servicio.
    def comparar_servicios():
        lineas = []
        for servicio in (sala, equipo, asesoria):
            costo = servicio.calcular_costo_con_impuesto(2)
            lineas.append(f"{servicio.nombre}: ${costo['total']:,.2f}")
        return " | ".join(lineas)

    if sala is not None and equipo is not None and asesoria is not None:
        ejecutar_operacion(
            30, "Polimorfismo: costo de 2 horas con impuesto en cada servicio",
            comparar_servicios, resultados, logger
        )

    # Resumen final.
    print("\n" + "=" * 72)
    print("RESUMEN FINAL DE LA DEMOSTRACION")
    exitos = resultados.count("ok")
    controlados = resultados.count("controlado")
    inesperados = resultados.count("inesperado")
    print(f"Operaciones ejecutadas: {len(resultados)}")
    print(f"Operaciones exitosas:   {exitos}")
    print(f"Errores controlados:    {controlados}")
    print(f"Errores inesperados:    {inesperados}")
    print(f"Clientes registrados:   {len(sistema.clientes)}")
    print(f"Servicios registrados:  {len(sistema.servicios)}")
    print(f"Reservas creadas:       {len(sistema.reservas)}")
    print("=" * 72)

    logger.info(
        "Demostracion finalizada. Operaciones: %s | Exitos: %s | Controlados: %s | Inesperados: %s",
        len(resultados), exitos, controlados, inesperados
    )
