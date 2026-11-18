"""Clase abstracta EntidadSistema y clase Cliente."""

# Clases base para crear clases abstractas.
from abc import ABC, abstractmethod
# re para validar correo, telefono y documento con expresiones regulares.
import re

from excepciones import ClienteInvalidoError, ValidacionError
from validaciones import generar_id, validar_texto


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
