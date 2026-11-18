"""Clase abstracta Servicio y servicios especializados."""

from abc import ABC, abstractmethod

from excepciones import ServicioInvalidoError, ValidacionError
from validaciones import validar_numero, validar_texto
from entidades import EntidadSistema


class Servicio(EntidadSistema, ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, nombre, descripcion, tarifa_base, disponible=True):
        super().__init__()
        try:
            self._nombre = validar_texto(nombre, "El nombre del servicio", 3, 80)
            self._descripcion = validar_texto(descripcion, "La descripcion", 5, 180)
            self._tarifa_base = validar_numero(
                tarifa_base, "La tarifa base", minimo=1, permitir_cero=False
            )
            if not isinstance(disponible, bool):
                raise ValidacionError("La disponibilidad debe ser verdadera o falsa.")
            self._disponible = disponible
        except ValidacionError as exc:
            raise ServicioInvalidoError(f"No fue posible crear el servicio: {exc}") from exc

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = estado

    def _calcular_total(self, duracion_horas, impuesto, descuento, tarifa_hora):
        """Valida parametros y aplica descuento e impuesto al subtotal."""
        duracion = validar_numero(
            duracion_horas, "La duracion", minimo=0, permitir_cero=False
        )
        porcentaje_impuesto = validar_numero(
            impuesto, "El impuesto", minimo=0, maximo=1
        )
        porcentaje_descuento = validar_numero(
            descuento, "El descuento", minimo=0, maximo=1
        )

        subtotal = tarifa_hora * duracion
        valor_descuento = subtotal * porcentaje_descuento
        subtotal_con_descuento = subtotal - valor_descuento
        valor_impuesto = subtotal_con_descuento * porcentaje_impuesto
        total = subtotal_con_descuento + valor_impuesto

        return {
            "tarifa_hora": round(tarifa_hora, 2),
            "duracion_horas": round(duracion, 2),
            "subtotal": round(subtotal, 2),
            "descuento": round(valor_descuento, 2),
            "impuesto": round(valor_impuesto, 2),
            "total": round(total, 2),
        }

    @abstractmethod
    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        """Cada servicio implementa su propia forma de calcular el costo."""
        raise NotImplementedError

    @abstractmethod
    def describir(self):
        """Cada servicio debe describir sus caracteristicas particulares."""
        raise NotImplementedError

    # Variantes de calculo con parametros opcionales (sobrecarga funcional).
    # En Python se usa una misma funcion con argumentos opcionales, no varias
    # funciones identicas con firmas distintas como en otros lenguajes.
    def calcular_costo_basico(self, duracion_horas=1):
        return self.calcular_costo(duracion_horas, impuesto=0, descuento=0)

    def calcular_costo_con_impuesto(self, duracion_horas=1, impuesto=0.19):
        return self.calcular_costo(duracion_horas, impuesto=impuesto, descuento=0)

    def calcular_costo_con_descuento(self, duracion_horas=1, descuento=0.10):
        return self.calcular_costo(duracion_horas, impuesto=0, descuento=descuento)

    def __str__(self):
        return self.describir()


class ServicioSala(Servicio):
    """Servicio de reserva de salas, con capacidad y opcion de proyector."""

    def __init__(self, nombre, descripcion, tarifa_base, capacidad, proyector=False):
        super().__init__(nombre, descripcion, tarifa_base)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        if not isinstance(proyector, bool):
            raise ServicioInvalidoError("La opcion de proyector debe ser verdadera o falsa.")
        self.capacidad = capacidad
        self.proyector = proyector

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        tarifa = self._tarifa_base + (20000 if self.proyector else 0)
        return self._calcular_total(duracion_horas, impuesto, descuento, tarifa)

    def describir(self):
        proyector = "Si" if self.proyector else "No"
        return (
            f"Sala: {self._nombre} | Capacidad: {self.capacidad} personas | "
            f"Proyector: {proyector} | Tarifa base/hora: ${self._tarifa_base:,.0f}"
        )


class ServicioEquipo(Servicio):
    """Servicio de alquiler de equipos por hora y por cantidad de unidades."""

    def __init__(self, nombre, descripcion, tarifa_base, tipo_equipo, cantidad=1):
        super().__init__(nombre, descripcion, tarifa_base)
        self.tipo_equipo = validar_texto(tipo_equipo, "El tipo de equipo", 3, 60)
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioInvalidoError("La cantidad de equipos debe ser un entero positivo.")
        self.cantidad = cantidad

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        tarifa = self._tarifa_base * self.cantidad
        return self._calcular_total(duracion_horas, impuesto, descuento, tarifa)

    def describir(self):
        return (
            f"Alquiler de equipos: {self.tipo_equipo} | Unidades: {self.cantidad} | "
            f"Tarifa por unidad/hora: ${self._tarifa_base:,.0f}"
        )


class ServicioAsesoria(Servicio):
    """Servicio de asesoria especializada virtual o presencial."""

    def __init__(self, nombre, descripcion, tarifa_base, especialidad, modalidad="virtual"):
        super().__init__(nombre, descripcion, tarifa_base)
        self.especialidad = validar_texto(especialidad, "La especialidad", 3, 80)
        modalidad = validar_texto(modalidad, "La modalidad", 6, 12).lower()
        if modalidad not in ("virtual", "presencial"):
            raise ServicioInvalidoError("La modalidad debe ser virtual o presencial.")
        self.modalidad = modalidad

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        # La asesoria presencial incluye un recargo operativo del 10 por ciento.
        tarifa = self._tarifa_base * (1.10 if self.modalidad == "presencial" else 1)
        return self._calcular_total(duracion_horas, impuesto, descuento, tarifa)

    def describir(self):
        return (
            f"Asesoria: {self.especialidad} | Modalidad: {self.modalidad} | "
            f"Tarifa base/hora: ${self._tarifa_base:,.0f}"
        )
