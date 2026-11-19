"""Clase abstracta Servicio y servicios especializados."""

# Clases base para crear clases abstractas.
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
            # CORRECCION: antes era minimo=1, lo que rechazaba una tarifa de
            # exactamente 1. Ahora se acepta cualquier tarifa mayor que 0.
            self._tarifa_base = validar_numero(
                tarifa_base, "La tarifa base", minimo=0, permitir_cero=False
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
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):
        """Activa o desactiva el servicio (por ejemplo, por mantenimiento)."""
        if not isinstance(estado, bool):
            raise ServicioInvalidoError("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = estado

    def _calcular_total(self, duracion_horas, impuesto, descuento, tarifa_hora):
        """Valida parametros y aplica descuento e impuesto al subtotal."""
        # Se validan los tres datos numericos antes de calcular.
        duracion = validar_numero(
            duracion_horas, "La duracion", minimo=0, permitir_cero=False
        )
        porcentaje_impuesto = validar_numero(
            impuesto, "El impuesto", minimo=0, maximo=1
        )
        porcentaje_descuento = validar_numero(
            descuento, "El descuento", minimo=0, maximo=1
        )

        # Calculo paso a paso: subtotal -> descuento -> impuesto -> total.
        subtotal = tarifa_hora * duracion
        valor_descuento = subtotal * porcentaje_descuento
        subtotal_con_descuento = subtotal - valor_descuento
        valor_impuesto = subtotal_con_descuento * porcentaje_impuesto
        total = subtotal_con_descuento + valor_impuesto

        # Se devuelve un diccionario con el detalle del costo.
        return {
            "tarifa_hora": round(tarifa_hora, 2),
            "duracion_horas": round(duracion, 2),
            "subtotal": round(subtotal, 2),
            "descuento": round(valor_descuento, 2),
            "impuesto": round(valor_impuesto, 2),
            "total": round(total, 2),
        }

    @abstractmethod
    def validar_parametros(self, duracion_horas):
        """Cada servicio valida la duracion segun sus propios limites.

        AGREGADO en la revision: el enunciado pide metodos sobrescritos para
        calcular costos, describir servicios Y validar parametros.
        """
        raise NotImplementedError

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
        """Variante 1: solo duracion, sin impuesto ni descuento."""
        return self.calcular_costo(duracion_horas, impuesto=0, descuento=0)

    def calcular_costo_con_impuesto(self, duracion_horas=1, impuesto=0.19):
        """Variante 2: duracion e impuesto, sin descuento."""
        return self.calcular_costo(duracion_horas, impuesto=impuesto, descuento=0)

    def calcular_costo_con_descuento(self, duracion_horas=1, descuento=0.10):
        """Variante 3: duracion y descuento, sin impuesto."""
        return self.calcular_costo(duracion_horas, impuesto=0, descuento=descuento)

    def __str__(self):
        return self.describir()


class ServicioSala(Servicio):
    """Servicio de reserva de salas, con capacidad y opcion de proyector."""

    DURACION_MAXIMA = 12  # una sala se reserva maximo 12 horas seguidas
    EXTRA_PROYECTOR = 20000  # valor adicional por hora si incluye proyector

    def __init__(self, nombre, descripcion, tarifa_base, capacidad, proyector=False,
                 disponible=True):
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        # CORRECCION: antes los atributos eran publicos y se podian cambiar
        # sin validar. Ahora son privados y se leen con propiedades.
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        if not isinstance(proyector, bool):
            raise ServicioInvalidoError("La opcion de proyector debe ser verdadera o falsa.")
        self.__capacidad = capacidad
        self.__proyector = proyector

    @property
    def capacidad(self):
        return self.__capacidad

    @property
    def proyector(self):
        return self.__proyector

    def validar_parametros(self, duracion_horas):
        # Metodo sobrescrito: limite propio de las salas.
        return validar_numero(
            duracion_horas, "La duracion de la sala",
            minimo=0, maximo=self.DURACION_MAXIMA, permitir_cero=False,
        )

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        duracion = self.validar_parametros(duracion_horas)
        # Si tiene proyector se suma un valor fijo a la tarifa por hora.
        tarifa = self._tarifa_base + (self.EXTRA_PROYECTOR if self.__proyector else 0)
        return self._calcular_total(duracion, impuesto, descuento, tarifa)

    def describir(self):
        proyector = "Si" if self.__proyector else "No"
        return (
            f"Sala: {self._nombre} | Capacidad: {self.__capacidad} personas | "
            f"Proyector: {proyector} | Tarifa base/hora: ${self._tarifa_base:,.0f}"
        )


class ServicioEquipo(Servicio):
    """Servicio de alquiler de equipos por hora y por cantidad de unidades."""

    DURACION_MAXIMA = 72  # un equipo se alquila maximo 72 horas (3 dias)

    def __init__(self, nombre, descripcion, tarifa_base, tipo_equipo, cantidad=1,
                 disponible=True):
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        try:
            self.__tipo_equipo = validar_texto(tipo_equipo, "El tipo de equipo", 3, 60)
        except ValidacionError as exc:
            # CORRECCION: el error ahora es de servicio, no un error generico.
            raise ServicioInvalidoError(f"No fue posible crear el servicio: {exc}") from exc
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioInvalidoError("La cantidad de equipos debe ser un entero positivo.")
        self.__cantidad = cantidad

    @property
    def tipo_equipo(self):
        return self.__tipo_equipo

    @property
    def cantidad(self):
        return self.__cantidad

    def validar_parametros(self, duracion_horas):
        # Metodo sobrescrito: limite propio de los alquileres.
        return validar_numero(
            duracion_horas, "La duracion del alquiler",
            minimo=0, maximo=self.DURACION_MAXIMA, permitir_cero=False,
        )

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        duracion = self.validar_parametros(duracion_horas)
        # La tarifa por hora se multiplica por la cantidad de equipos.
        tarifa = self._tarifa_base * self.__cantidad
        return self._calcular_total(duracion, impuesto, descuento, tarifa)

    def describir(self):
        return (
            f"Alquiler de equipos: {self.__tipo_equipo} | Unidades: {self.__cantidad} | "
            f"Tarifa por unidad/hora: ${self._tarifa_base:,.0f}"
        )


class ServicioAsesoria(Servicio):
    """Servicio de asesoria especializada virtual o presencial."""

    DURACION_MAXIMA = 8  # una asesoria dura maximo 8 horas

    def __init__(self, nombre, descripcion, tarifa_base, especialidad, modalidad="virtual",
                 disponible=True):
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        try:
            self.__especialidad = validar_texto(especialidad, "La especialidad", 3, 80)
            modalidad = validar_texto(modalidad, "La modalidad", 6, 12).lower()
        except ValidacionError as exc:
            raise ServicioInvalidoError(f"No fue posible crear el servicio: {exc}") from exc
        # Solo se aceptan dos modalidades.
        if modalidad not in ("virtual", "presencial"):
            raise ServicioInvalidoError("La modalidad debe ser virtual o presencial.")
        self.__modalidad = modalidad

    @property
    def especialidad(self):
        return self.__especialidad

    @property
    def modalidad(self):
        return self.__modalidad

    def validar_parametros(self, duracion_horas):
        # Metodo sobrescrito: limite propio de las asesorias.
        return validar_numero(
            duracion_horas, "La duracion de la asesoria",
            minimo=0, maximo=self.DURACION_MAXIMA, permitir_cero=False,
        )

    def calcular_costo(self, duracion_horas=1, impuesto=0.19, descuento=0):
        duracion = self.validar_parametros(duracion_horas)
        # La asesoria presencial incluye un recargo operativo del 10 por ciento.
        tarifa = self._tarifa_base * (1.10 if self.__modalidad == "presencial" else 1)
        return self._calcular_total(duracion, impuesto, descuento, tarifa)

    def describir(self):
        return (
            f"Asesoria: {self.__especialidad} | Modalidad: {self.__modalidad} | "
            f"Tarifa base/hora: ${self._tarifa_base:,.0f}"
        )
        Revisado por Rodrigo Jose Vergara Buelvas - 19/11/2026
# Revisión colaborativa: se verificó que los servicios y reser
