"""Entidades generales: clase abstracta Entidad, Cliente y Servicio abstracto."""
# Demuestra abstracción, encapsulación y validaciones estrictas.
from abc import ABC, abstractmethod  # ABC permite definir clases abstractas.
from datetime import datetime  # Para registrar la fecha de creación.
from .excepciones import (  # Excepciones propias del dominio.
    ClienteInvalidoError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)


class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    def __init__(self, identificador):
        """Inicializa la entidad con identificador y fecha de creación."""
        # Se valida que el identificador no sea vacío (validación estricta).
        if identificador is None or str(identificador).strip() == "":
            # Se exige el parámetro faltante con excepción personalizada.
            raise ParametroFaltanteError("El identificador de la entidad es obligatorio.")
        # Se guarda el identificador como cadena sin espacios extremos.
        self._id = str(identificador).strip()
        # Se registra la fecha/hora de creación automáticamente.
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        """Retorna el identificador de la entidad (solo lectura)."""
        return self._id

    @property
    def fecha_creacion(self):
        """Retorna la fecha de creación de la entidad (solo lectura)."""
        return self._fecha_creacion

    @abstractmethod
    def describir(self):
        """Describe la entidad (debe implementarse en cada derivada)."""
        pass

    @abstractmethod
    def validar(self):
        """Valida los datos internos (debe implementarse en cada derivada)."""
        pass


class Cliente(Entidad):
    """Cliente de Software FJ con encapsulación de datos personales."""

    def __init__(self, identificador, nombre, documento, email, telefono=""):
        """Crea el cliente validando cada dato personal."""
        # Se llama al constructor padre para fijar id y fecha.
        super().__init__(identificador)
        # Se inicializan los campos privados en vacío antes de usar los setters.
        self._nombre = ""
        self._documento = ""
        self._email = ""
        self._telefono = ""
        # Se asignan vía propiedades (disparan validación automáticamente).
        self.nombre = nombre
        self.documento = documento
        self.email = email
        self.telefono = telefono
        # Validación final integral del objeto construido.
        self.validar()

    @property
    def nombre(self):
        """Retorna el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Valida y asigna el nombre (mínimo 3 letras)."""
        # Se verifica que no sea nulo ni vacío.
        if valor is None or str(valor).strip() == "":
            raise ClienteInvalidoError("El nombre del cliente es obligatorio.")
        # Se exige longitud mínima para evitar registros inválidos.
        if len(str(valor).strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = str(valor).strip()

    @property
    def documento(self):
        """Retorna el documento del cliente."""
        return self._documento

    @documento.setter
    def documento(self, valor):
        """Valida y asigna el documento (solo dígitos, mínimo 5)."""
        # Se verifica obligatoriedad del documento.
        if valor is None or str(valor).strip() == "":
            raise ClienteInvalidoError("El documento del cliente es obligatorio.")
        # Se normaliza quitando espacios.
        texto = str(valor).strip()
        # Debe ser numérico para un registro válido.
        if not texto.isdigit():
            raise ClienteInvalidoError("El documento debe contener solo dígitos.")
        # Longitud mínima de 5 dígitos.
        if len(texto) < 5:
            raise ClienteInvalidoError("El documento debe tener al menos 5 dígitos.")
        self._documento = texto

    @property
    def email(self):
        """Retorna el correo del cliente."""
        return self._email

    @email.setter
    def email(self, valor):
        """Valida y asigna el email (formato básico con @ y punto)."""
        # Se verifica obligatoriedad.
        if valor is None or str(valor).strip() == "":
            raise ClienteInvalidoError("El email del cliente es obligatorio.")
        texto = str(valor).strip()
        # Validación básica de formato: debe tener @ y un punto posterior.
        if "@" not in texto or "." not in texto.split("@")[-1]:
            raise ClienteInvalidoError(f"Email inválido: '{valor}'.")
        self._email = texto

    @property
    def telefono(self):
        """Retorna el teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        """Valida y asigna el teléfono (opcional, solo dígitos y guiones)."""
        # El teléfono es opcional: vacío se acepta.
        if valor is None or str(valor).strip() == "":
            self._telefono = ""
            return
        texto = str(valor).strip()
        # Se permiten dígitos, espacios, + y - únicamente.
        permitido = set("0123456789+ -")
        if any(c not in permitido for c in texto):
            raise ClienteInvalidoError("El teléfono contiene caracteres inválidos.")
        self._telefono = texto

    def validar(self):
        """Valida integralmente el cliente (lanza ClienteInvalidoError si falla)."""
        # Re-verifica nombre, documento y email ya validados por setters.
        if not self._nombre or not self._documento or not self._email:
            raise ClienteInvalidoError("Faltan datos obligatorios del cliente.")
        return True

    def describir(self):
        """Retorna una descripción legible del cliente."""
        return f"Cliente[{self._id}] {self._nombre} doc={self._documento} email={self._email}"


class Servicio(Entidad):
    """Clase abstracta que representa un servicio ofrecido por Software FJ."""

    def __init__(self, identificador, nombre, precio_base, disponible=True):
        """Inicializa el servicio con nombre, precio base y disponibilidad."""
        # Constructor padre para id y fecha.
        super().__init__(identificador)
        # Nombre obligatorio.
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        self._nombre = str(nombre).strip()
        # El precio base debe ser numérico y mayor que cero.
        try:
            precio = float(precio_base)
        except (TypeError, ValueError) as exc:
            # Encadenamiento: se conserva la causa original del error.
            raise ParametroFaltanteError("El precio base debe ser numérico.") from exc
        if precio <= 0:
            raise CalculoInconsistenteError("El precio base debe ser mayor que cero.")
        self._precio_base = precio
        # Disponibilidad como booleano.
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def precio_base(self):
        """Retorna el precio base del servicio."""
        return self._precio_base

    @property
    def disponible(self):
        """Indica si el servicio está disponible."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        """Asigna la disponibilidad del servicio."""
        self._disponible = bool(valor)

    @abstractmethod
    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0):
        """Calcula el costo (polimórfico: cada servicio implementa su fórmula)."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida los parámetros de uso del servicio (ej. duración)."""
        pass

    def _aplicar_impuesto_descuento(self, subtotal, impuesto, descuento):
        """Aplica impuesto y descuento con validaciones estrictas (sobrecarga base)."""
        # Impuesto entre 0 y 1 (0% a 100%).
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError("El impuesto debe estar entre 0 y 1.")
        # Descuento entre 0 y 0.9 (máximo 90% para evitar cálculos inconsistentes).
        if not 0 <= descuento <= 0.9:
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 0.9 (máx 90%).")
        # Fórmula: subtotal * (1 + impuesto) * (1 - descuento).
        return round(subtotal * (1 + impuesto) * (1 - descuento), 2)

    # ---- Métodos sobrecargados (variantes del cálculo de costos) ----
    def calcular_costo_base(self, duracion=1):
        """Variante 1 (sobrecarga): costo sin impuesto ni descuento."""
        return self.calcular_costo(duracion=duracion, impuesto=0.0, descuento=0.0)

    def calcular_costo_con_impuesto(self, duracion=1, impuesto=0.19):
        """Variante 2 (sobrecarga): costo solo con impuesto."""
        return self.calcular_costo(duracion=duracion, impuesto=impuesto, descuento=0.0)

    def calcular_costo_con_descuento(self, duracion=1, impuesto=0.19, descuento=0.1):
        """Variante 3 (sobrecarga): costo con impuesto y descuento."""
        return self.calcular_costo(duracion=duracion, impuesto=impuesto, descuento=descuento)
