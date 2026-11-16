"""Sistema Integral de Gestion de Clientes, Servicios y Reservas - Software FJ.

Proyecto academico de Programacion Orientada a Objetos.
- No utiliza bases de datos: los datos se mantienen en listas y objetos.
- Registra eventos y errores en software_fj.log.
- Incluye una demostracion automatica con operaciones validas e invalidas.

Ejecucion: python software_fj.py
Requisito: Python 3.10 o superior (recomendado Python 3.12).
"""

# Clases base para crear clases abstractas.
from abc import ABC, abstractmethod
# datetime para fechas de reservas y timedelta para sumar horas.
from datetime import datetime, timedelta
# Enum para definir los estados de una reserva.
from enum import Enum
# logging para escribir el archivo de eventos y errores.
import logging
# math para comprobar que los numeros no sean infinitos ni NaN.
import math
# Path para ubicar el archivo de log junto a este programa.
from pathlib import Path
# re para validar correo, telefono y documento con expresiones regulares.
import re
# uuid para generar identificadores unicos.
import uuid


# ============================================================
# 1. EXCEPCIONES PERSONALIZADAS
# ============================================================

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


# ============================================================
# 2. FUNCIONES DE VALIDACION Y CONFIGURACION DEL LOG
# ============================================================

def generar_id():
    """Genera un identificador corto y unico para cada objeto."""
    # uuid4 es aleatorio; se toman 8 caracteres y se pasan a mayuscula.
    return uuid.uuid4().hex[:8].upper()


def validar_texto(valor, campo, minimo=2, maximo=80):
    """Valida que un dato sea texto no vacio y dentro de la longitud permitida."""
    # Si no es texto (por ejemplo un numero o None) se rechaza de inmediato.
    if not isinstance(valor, str):
        raise ValidacionError(f"{campo} debe ser texto.")

    # strip() quita espacios al inicio y al final.
    valor = valor.strip()
    # Se comprueba que la longitud este entre el minimo y el maximo.
    if not minimo <= len(valor) <= maximo:
        raise ValidacionError(
            f"{campo} debe tener entre {minimo} y {maximo} caracteres."
        )
    return valor


def validar_numero(valor, campo, minimo=None, maximo=None, permitir_cero=True):
    """Valida numeros reales y evita valores infinitos, NaN y booleanos."""
    # En Python True y False cuentan como numeros, por eso se excluyen.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidacionError(f"{campo} debe ser un numero.")

    numero = float(valor)
    # isfinite es False para infinito y NaN.
    if not math.isfinite(numero):
        raise ValidacionError(f"{campo} debe ser un numero finito.")
    # Control del limite inferior (con opcion de excluir el propio minimo).
    if minimo is not None and (numero < minimo or (numero == minimo and not permitir_cero)):
        operador = "mayor que" if not permitir_cero else "mayor o igual a"
        raise ValidacionError(f"{campo} debe ser {operador} {minimo}.")
    # Control del limite superior.
    if maximo is not None and numero > maximo:
        raise ValidacionError(f"{campo} no puede ser superior a {maximo}.")
    return numero


def configurar_logger():
    """Crea el archivo software_fj.log y configura el registro de eventos."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Evita agregar el mismo manejador varias veces si se ejecuta desde un IDE.
    if not logger.handlers:
        try:
            # El log se guarda en la misma carpeta del programa.
            carpeta = Path(__file__).resolve().parent
        except NameError:
            # Si __file__ no existe (algunos IDE), se usa la carpeta actual.
            carpeta = Path.cwd()

        ruta_log = carpeta / "software_fj.log"
        manejador = logging.FileHandler(ruta_log, encoding="utf-8")
        # Formato de cada linea: fecha | nivel | mensaje.
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        manejador.setFormatter(formato)
        logger.addHandler(manejador)

    return logger


# ============================================================
# 3. CLASE ABSTRACTA GENERAL: ENTIDAD DEL SISTEMA
# ============================================================

class EntidadSistema(ABC):
    """Clase abstracta de la que heredan las entidades principales."""

    def __init__(self, identificador=None):
        # Si no llega un id, se genera uno automaticamente.
        self._id = identificador or generar_id()

    @property
    def id(self):
        # Solo lectura: el id no se puede cambiar desde fuera.
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe implementar su propia descripcion."""
        raise NotImplementedError


# ============================================================
# 4. CLASE CLIENTE: ENCAPSULACION Y VALIDACIONES
# ============================================================

class Cliente(EntidadSistema):
    """Representa un cliente y protege sus datos mediante atributos privados."""

    def __init__(self, nombre, documento, correo, telefono, activo=True):
        super().__init__()

        try:
            # Atributos privados (doble guion bajo): encapsulacion.
            self.__nombre = validar_texto(nombre, "El nombre", 3, 80)
            self.__documento = validar_texto(documento, "El documento", 5, 20)
            self.__correo = validar_texto(correo, "El correo", 6, 100).lower()
            self.__telefono = validar_texto(telefono, "El telefono", 7, 20)

            # Formato del documento: letras, numeros, punto y guion.
            if not re.fullmatch(r"[A-Za-z0-9.-]{5,20}", self.__documento):
                raise ValidacionError("El documento solo admite letras, numeros, punto y guion.")
            # Formato basico de correo: algo@dominio.ext
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", self.__correo):
                raise ValidacionError("El correo electronico no tiene un formato valido.")
            # Telefono: solo digitos, espacios, parentesis, guion y + inicial.
            if not re.fullmatch(r"\+?[0-9\s()-]{7,20}", self.__telefono):
                raise ValidacionError("El telefono contiene caracteres no permitidos.")
            # Debe tener al menos siete digitos reales.
            if len(re.sub(r"\D", "", self.__telefono)) < 7:
                raise ValidacionError("El telefono debe contener al menos siete digitos.")
            if not isinstance(activo, bool):
                raise ValidacionError("El estado activo debe ser verdadero o falso.")

            self.__activo = activo
        except ValidacionError as exc:
            # Encadenamiento: "from exc" conserva el error original.
            raise ClienteInvalidoError(f"No fue posible crear el cliente: {exc}") from exc

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    @property
    def activo(self):
        return self.__activo

    def desactivar(self):
        """Marca al cliente como inactivo (no podra hacer reservas)."""
        self.__activo = False

    def activar(self):
        """Marca al cliente como activo de nuevo (agregado en la revision)."""
        self.__activo = True

    def describir(self):
        return f"Cliente {self.__nombre} | ID: {self.id} | Activo: {self.__activo}"

    def __str__(self):
        return self.describir()


# ============================================================
# 5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# ============================================================

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


# ============================================================
# 6. CLASE RESERVA: CLIENTE + SERVICIO + DURACION + ESTADO
# ============================================================

class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(EntidadSistema):
    """Integra cliente, servicio, fecha, duracion, estado y costo."""

    def __init__(self, cliente, servicio, duracion_horas, fecha_inicio, logger):
        super().__init__()

        # Verificaciones de los datos que recibe la reserva.
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
            # MEJORA: la duracion se valida con las reglas del servicio concreto
            # (polimorfismo), no solo con "mayor que cero".
            self.__duracion_horas = servicio.validar_parametros(duracion_horas)
        except (TypeError, ValueError, ValidacionError) as exc:
            # Encadenamiento: la excepcion original queda disponible en __cause__.
            raise DuracionInvalidaError(
                f"No se pudo crear la reserva porque la duracion no es valida: {exc}"
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
        # La fecha de fin se calcula sumando las horas a la fecha de inicio.
        return self.__fecha_inicio + timedelta(hours=self.__duracion_horas)

    @property
    def estado(self):
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    def confirmar(self):
        """Pasa la reserva de PENDIENTE a CONFIRMADA."""
        if self.__estado != EstadoReserva.PENDIENTE:
            raise EstadoReservaError("Solo se pueden confirmar reservas pendientes.")
        if not self.__cliente.activo:
            raise ReservaError("No se puede confirmar: el cliente esta inactivo.")
        if not self.__servicio.disponible:
            raise ReservaNoDisponibleError("No se puede confirmar: el servicio no esta disponible.")

        self.__estado = EstadoReserva.CONFIRMADA
        self._logger.info("Reserva %s confirmada.", self.id)
        return f"Reserva {self.id} confirmada correctamente."

    def cancelar(self, motivo="Sin motivo"):
        """Cancela una reserva pendiente o confirmada (motivo agregado en la revision)."""
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise EstadoReservaError(
                f"No se puede cancelar una reserva {self.__estado.value.lower()}."
            )
        self.__estado = EstadoReserva.CANCELADA
        self._logger.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)
        return f"Reserva {self.id} cancelada correctamente."

    def procesar(self, impuesto=0.19, descuento=0):
        """Calcula el costo final y deja la reserva PROCESADA.

        MEJORA: ahora usa try/except/else/finally completo, como pide el
        enunciado.
        """
        if self.__estado != EstadoReserva.CONFIRMADA:
            raise EstadoReservaError("Solo se pueden procesar reservas confirmadas.")
        try:
            # Polimorfismo: se ejecuta el calculo propio del tipo de servicio.
            resultado = self.__servicio.calcular_costo(
                self.__duracion_horas, impuesto=impuesto, descuento=descuento
            )
        except ValidacionError as exc:
            # Error de calculo (por ejemplo, descuento fuera de rango).
            raise ReservaError(f"No se pudo calcular el costo de la reserva: {exc}") from exc
        else:
            # Solo se ejecuta si el try no produjo errores.
            self.__costo = resultado
            self.__estado = EstadoReserva.PROCESADA
            self._logger.info("Reserva %s procesada. Total: $%.2f", self.id, resultado["total"])
            return resultado
        finally:
            # Se ejecuta siempre, haya o no error.
            self._logger.info("Intento de procesar la reserva %s finalizado.", self.id)

    def describir(self):
        return (
            f"Reserva {self.id} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | Inicio: "
            f"{self.__fecha_inicio:%Y-%m-%d %H:%M} | "
            f"Duracion: {self.__duracion_horas:g} h | Estado: {self.__estado.value}"
        )

    def __str__(self):
        return self.describir()


# ============================================================
# 7. GESTOR PRINCIPAL: LISTAS EN MEMORIA, SIN BASE DE DATOS
# ============================================================

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


# ============================================================
# 8. DEMOSTRACION DE OPERACIONES Y MANEJO ROBUSTO DE ERRORES
# ============================================================

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


# ============================================================
# 9. PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

if __name__ == "__main__":
    registro = configurar_logger()
    try:
        ejecutar_demo(registro)
    except KeyboardInterrupt:
        registro.warning("Ejecucion interrumpida manualmente por el usuario.")
        print("\nLa ejecucion fue interrumpida por el usuario.")
    except Exception:
        registro.exception("Fallo no controlado en el punto de entrada.")
        print("Ocurrio un error inesperado. Revise software_fj.log para mas detalles.")
    finally:
        # Pausa final: evita que la ventana se cierre sola al abrir el archivo
        # con doble clic. EOFError cubre el caso de ejecutarlo sin teclado.
        try:
            input("\nPresione Enter para cerrar el programa...")
        except EOFError:
            pass
