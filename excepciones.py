"""Excepciones personalizadas del sistema Software FJ."""



class SistemaFJError(Exception):
    """Excepcion base para los errores controlados del sistema."""


class ValidacionError(SistemaFJError):
    """Se produce cuando un dato no cumple las reglas de validacion."""


class ClienteInvalidoError(ValidacionError):
    """Error relacionado con los datos de un cliente."""


class ServicioInvalidoError(ValidacionError):
    """Error relacionado con los datos de un servicio."""


class ReservaError(SistemaFJError):
    """Error general relacionado con una reserva."""


class DuracionInvalidaError(ReservaError):
    """La duracion de una reserva no es valida."""


class ReservaNoDisponibleError(ReservaError):
    """El servicio ya esta reservado en ese horario o no esta disponible."""


class EstadoReservaError(ReservaError):
    """La operacion solicitada no corresponde al estado de la reserva."""
