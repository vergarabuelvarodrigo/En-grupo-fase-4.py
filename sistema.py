"""Gestor principal SistemaFJ (listas en memoria)."""

# datetime para fechas y timedelta para sumar horas.
from datetime import datetime, timedelta

from excepciones import (
    ClienteInvalidoError,
    DuracionInvalidaError,
    ReservaError,
    ReservaNoDisponibleError,
    ServicioInvalidoError,
    ValidacionError,
)
from entidades import Cliente
from servicios import Servicio
from reserva import EstadoReserva, Reserva


class SistemaFJ:
    """Administra clientes, servicios y reservas usando listas de Python."""

    def __init__(self, logger):
        # Las "bases de datos" del sistema son simples listas en memoria.
        self.clientes = []
        self.servicios = []
        self.reservas = []
        self.logger = logger

    def registrar_cliente(self, cliente):
        """Agrega un cliente a la lista si es valido y no esta repetido."""
        if not isinstance(cliente, Cliente):
            raise ClienteInvalidoError("El objeto que intenta registrar no es un cliente.")
        # any() es True si algun cliente existente tiene el mismo documento.
        if any(c.documento.lower() == cliente.documento.lower() for c in self.clientes):
            raise ClienteInvalidoError("Ya existe un cliente con ese documento.")
        self.clientes.append(cliente)
        self.logger.info("Cliente registrado. ID: %s", cliente.id)
        return f"Cliente registrado: {cliente.describir()}"

    def registrar_servicio(self, servicio):
        """Agrega un servicio a la lista si es valido y no esta repetido."""
        if not isinstance(servicio, Servicio):
            raise ServicioInvalidoError("El objeto que intenta registrar no es un servicio.")
        if any(s.id == servicio.id for s in self.servicios):
            raise ServicioInvalidoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        self.logger.info("Servicio registrado. ID: %s | Nombre: %s", servicio.id, servicio.nombre)
        return f"Servicio registrado: {servicio.describir()}"

    def buscar_cliente(self, documento):
        """Busca un cliente por su documento."""
        for cliente in self.clientes:
            if cliente.documento.lower() == str(documento).strip().lower():
                return cliente
        raise ClienteInvalidoError("No se encontro un cliente con ese documento.")

    def buscar_servicio(self, identificador):
        """Busca un servicio por su id."""
        for servicio in self.servicios:
            if servicio.id == identificador:
                return servicio
        raise ServicioInvalidoError("No se encontro el servicio solicitado.")

    def crear_reserva(self, documento_cliente, id_servicio, duracion_horas, fecha_inicio):
        """Crea una reserva verificando datos, disponibilidad y cruces de horario."""
        cliente = self.buscar_cliente(documento_cliente)
        servicio = self.buscar_servicio(id_servicio)

        if not servicio.disponible:
            raise ReservaNoDisponibleError("El servicio esta marcado como no disponible.")
        if not isinstance(fecha_inicio, datetime) or fecha_inicio.tzinfo is not None:
            raise ReservaError("La fecha de inicio debe ser un datetime sin zona horaria.")

        try:
            # MEJORA: se usan los limites propios de cada servicio.
            duracion_validada = servicio.validar_parametros(duracion_horas)
        except (TypeError, ValueError, ValidacionError) as exc:
            raise DuracionInvalidaError(
                f"No se puede crear la reserva: {exc}"
            ) from exc

        # Hora en la que terminaria la nueva reserva.
        nueva_fecha_fin = fecha_inicio + timedelta(hours=duracion_validada)
        for reserva_existente in self.reservas:
            # Solo importan las reservas del mismo servicio.
            if reserva_existente.servicio.id != servicio.id:
                continue
            # Las reservas canceladas ya no ocupan el horario.
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

        # Si todo es valido, se crea la reserva y se guarda en la lista.
        reserva = Reserva(cliente, servicio, duracion_validada, fecha_inicio, self.logger)
        self.reservas.append(reserva)
        self.logger.info("Reserva creada. ID: %s", reserva.id)
        return reserva

    def confirmar_reserva(self, id_reserva):
        return self._buscar_reserva(id_reserva).confirmar()

    def cancelar_reserva(self, id_reserva, motivo="Sin motivo"):
        return self._buscar_reserva(id_reserva).cancelar(motivo)

    def procesar_reserva(self, id_reserva, impuesto=0.19, descuento=0):
        return self._buscar_reserva(id_reserva).procesar(impuesto, descuento)

    def _buscar_reserva(self, id_reserva):
        """Busca una reserva por su id (metodo interno)."""
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
