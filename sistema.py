"""Gestor principal SistemaFJ (listas en memoria)."""

from datetime import datetime, timedelta

from excepciones import (
    ClienteInvalidoError,
    DuracionInvalidaError,
    ReservaError,
    ReservaNoDisponibleError,
    ServicioInvalidoError,
    ValidacionError,
)
from validaciones import validar_numero
from entidades import Cliente
from servicios import Servicio
from reserva import EstadoReserva, Reserva


class SistemaFJ:
    """Administra clientes, servicios y reservas usando listas de Python."""

    def __init__(self, logger):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self.logger = logger

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ClienteInvalidoError("El objeto que intenta registrar no es un cliente.")
        if any(c.documento.lower() == cliente.documento.lower() for c in self.clientes):
            raise ClienteInvalidoError("Ya existe un cliente con ese documento.")
        self.clientes.append(cliente)
        self.logger.info("Cliente registrado. ID: %s", cliente.id)
        return f"Cliente registrado: {cliente.describir()}"

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ServicioInvalidoError("El objeto que intenta registrar no es un servicio.")
        if any(s.id == servicio.id for s in self.servicios):
            raise ServicioInvalidoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        self.logger.info("Servicio registrado. ID: %s | Nombre: %s", servicio.id, servicio.nombre)
        return f"Servicio registrado: {servicio.describir()}"

    def buscar_cliente(self, documento):
        for cliente in self.clientes:
            if cliente.documento.lower() == str(documento).strip().lower():
                return cliente
        raise ClienteInvalidoError("No se encontro un cliente con ese documento.")

    def buscar_servicio(self, identificador):
        for servicio in self.servicios:
            if servicio.id == identificador:
                return servicio
        raise ServicioInvalidoError("No se encontro el servicio solicitado.")

    def crear_reserva(self, documento_cliente, id_servicio, duracion_horas, fecha_inicio):
        cliente = self.buscar_cliente(documento_cliente)
        servicio = self.buscar_servicio(id_servicio)

        if not servicio.disponible:
            raise ReservaNoDisponibleError("El servicio esta marcado como no disponible.")
        if not isinstance(fecha_inicio, datetime) or fecha_inicio.tzinfo is not None:
            raise ReservaError("La fecha de inicio debe ser un datetime sin zona horaria.")

        try:
            duracion_validada = validar_numero(
                duracion_horas, "La duracion de la reserva", minimo=0, permitir_cero=False
            )
        except (TypeError, ValueError, ValidacionError) as exc:
            raise DuracionInvalidaError(
                "No se puede crear la reserva: la duracion debe ser un numero positivo."
            ) from exc

        nueva_fecha_fin = fecha_inicio + timedelta(hours=duracion_validada)
        for reserva_existente in self.reservas:
            if reserva_existente.servicio.id != servicio.id:
                continue
            if reserva_existente.estado == EstadoReserva.CANCELADA:
                continue
            # Dos intervalos se cruzan si cada uno empieza antes de que termine el otro.
            hay_cruce = (
                fecha_inicio < reserva_existente.fecha_fin
                and nueva_fecha_fin > reserva_existente.fecha_inicio
            )
            if hay_cruce:
                raise ReservaNoDisponibleError(
                    "El servicio ya tiene una reserva en ese horario."
                )

        reserva = Reserva(cliente, servicio, duracion_validada, fecha_inicio, self.logger)
        self.reservas.append(reserva)
        self.logger.info("Reserva creada. ID: %s", reserva.id)
        return reserva

    def confirmar_reserva(self, id_reserva):
        return self._buscar_reserva(id_reserva).confirmar()

    def cancelar_reserva(self, id_reserva):
        return self._buscar_reserva(id_reserva).cancelar()

    def procesar_reserva(self, id_reserva, impuesto=0.19, descuento=0):
        return self._buscar_reserva(id_reserva).procesar(impuesto, descuento)

    def _buscar_reserva(self, id_reserva):
        for reserva in self.reservas:
            if reserva.id == id_reserva:
                return reserva
        raise ReservaError("No se encontro la reserva solicitada.")

    def listar_clientes(self):
        return [cliente.describir() for cliente in self.clientes]

    def listar_servicios(self):
        return [servicio.describir() for servicio in self.servicios]

    def listar_reservas(self):
        return [reserva.describir() for reserva in self.reservas]
