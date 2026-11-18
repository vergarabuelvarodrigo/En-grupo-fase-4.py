"""Estados y clase Reserva."""

from datetime import datetime, timedelta
from enum import Enum

from excepciones import (
    DuracionInvalidaError,
    EstadoReservaError,
    ReservaError,
    ReservaNoDisponibleError,
    ValidacionError,
)
from validaciones import validar_numero
from entidades import Cliente, EntidadSistema
from servicios import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(EntidadSistema):
    """Integra cliente, servicio, fecha, duracion, estado y costo."""

    def __init__(self, cliente, servicio, duracion_horas, fecha_inicio, logger):
        super().__init__()

        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva debe estar asociada a un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva debe estar asociada a un servicio valido.")
        if not cliente.activo:
            raise ReservaError("No se puede reservar con un cliente inactivo.")
        if not servicio.disponible:
            raise ReservaNoDisponibleError("El servicio no se encuentra disponible.")
        if not isinstance(fecha_inicio, datetime):
            raise ReservaError("La fecha de inicio debe ser un objeto datetime.")
        if fecha_inicio.tzinfo is not None:
            raise ReservaError("Use una fecha sin zona horaria para esta demostracion.")
        if fecha_inicio <= datetime.now():
            raise ReservaError("La fecha de la reserva debe ser futura.")

        try:
            self.__duracion_horas = validar_numero(
                duracion_horas, "La duracion de la reserva", minimo=0, permitir_cero=False
            )
        except (TypeError, ValueError, ValidacionError) as exc:
            # Encadenamiento: la excepcion original queda disponible en __cause__.
            raise DuracionInvalidaError(
                "No se pudo crear la reserva porque la duracion no es valida."
            ) from exc

        self.__cliente = cliente
        self.__servicio = servicio
        self.__fecha_inicio = fecha_inicio
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo = None
        self._logger = logger

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion_horas(self):
        return self.__duracion_horas

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @property
    def fecha_fin(self):
        return self.__fecha_inicio + timedelta(hours=self.__duracion_horas)

    @property
    def estado(self):
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    def confirmar(self):
        if self.__estado != EstadoReserva.PENDIENTE:
            raise EstadoReservaError("Solo se pueden confirmar reservas pendientes.")
        if not self.__cliente.activo:
            raise ReservaError("No se puede confirmar: el cliente esta inactivo.")
        if not self.__servicio.disponible:
            raise ReservaNoDisponibleError("No se puede confirmar: el servicio no esta disponible.")

        self.__estado = EstadoReserva.CONFIRMADA
        self._logger.info("Reserva %s confirmada.", self.id)
        return f"Reserva {self.id} confirmada correctamente."

    def cancelar(self):
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise EstadoReservaError(
                f"No se puede cancelar una reserva {self.__estado.value.lower()}."
            )
        self.__estado = EstadoReserva.CANCELADA
        self._logger.info("Reserva %s cancelada.", self.id)
        return f"Reserva {self.id} cancelada correctamente."

    def procesar(self, impuesto=0.19, descuento=0):
        if self.__estado != EstadoReserva.CONFIRMADA:
            raise EstadoReservaError("Solo se pueden procesar reservas confirmadas.")
        try:
            # Polimorfismo: se ejecuta el calculo propio del tipo de servicio.
            resultado = self.__servicio.calcular_costo(
                self.__duracion_horas, impuesto=impuesto, descuento=descuento
            )
        except ValidacionError as exc:
            raise ReservaError("No se pudo calcular el costo de la reserva.") from exc

        self.__costo = resultado
        self.__estado = EstadoReserva.PROCESADA
        self._logger.info("Reserva %s procesada. Total: $%.2f", self.id, resultado["total"])
        return resultado

    def describir(self):
        return (
            f"Reserva {self.id} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | Inicio: "
            f"{self.__fecha_inicio:%Y-%m-%d %H:%M} | "
            f"Duracion: {self.__duracion_horas:g} h | Estado: {self.__estado.value}"
        )

    def __str__(self):
        return self.describir()
