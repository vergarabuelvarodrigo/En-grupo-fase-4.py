"""Clase abstracta EntidadSistema y clase Cliente."""

from abc import ABC, abstractmethod
import re

from excepciones import ClienteInvalidoError, ValidacionError
from validaciones import generar_id, validar_texto


class EntidadSistema(ABC):
    """Clase abstracta de la que heredan las entidades principales."""

    def __init__(self, identificador=None):
        self._id = identificador or generar_id()

    @property
    def id(self):
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
            self.__nombre = validar_texto(nombre, "El nombre", 3, 80)
            self.__documento = validar_texto(documento, "El documento", 5, 20)
            self.__correo = validar_texto(correo, "El correo", 6, 100).lower()
            self.__telefono = validar_texto(telefono, "El telefono", 7, 20)

            if not re.fullmatch(r"[A-Za-z0-9.-]{5,20}", self.__documento):
                raise ValidacionError("El documento solo admite letras, numeros, punto y guion.")
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", self.__correo):
                raise ValidacionError("El correo electronico no tiene un formato valido.")
            if not re.fullmatch(r"\+?[0-9\s()-]{7,20}", self.__telefono):
                raise ValidacionError("El telefono contiene caracteres no permitidos.")
            if len(re.sub(r"\D", "", self.__telefono)) < 7:
                raise ValidacionError("El telefono debe contener al menos siete digitos.")
            if not isinstance(activo, bool):
                raise ValidacionError("El estado activo debe ser verdadero o falso.")

            self.__activo = activo
        except ValidacionError as exc:
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
        self.__activo = False

    def describir(self):
        return f"Cliente {self.__nombre} | ID: {self.id} | Activo: {self.__activo}"

    def __str__(self):
        return self.describir()
