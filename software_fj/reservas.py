"""Módulo de reservas: clase Reserva y gestor con listas internas (sin BD)."""
# Toda la persistencia es en memoria (listas); solo los logs van a archivo.
from .entidades import Entidad, Cliente, Servicio  # Tipos del dominio.
from .excepciones import (  # Errores personalizados.
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ServicioNoDisponibleError,
    ParametroFaltanteError,
)
from .logger_config import obtener_logger  # Logger centralizado.

# Logger del módulo para registrar eventos y errores.
logger = obtener_logger()

# Estados permitidos de una reserva.
ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")


class Reserva(Entidad):
    """Integra cliente + servicio + duración + estado."""

    def __init__(self, identificador, cliente, servicio, duracion):
        """Crea la reserva en estado PENDIENTE validando cliente y servicio."""
        # Constructor padre para id y fecha.
        super().__init__(identificador)
        # El cliente debe ser instancia de Cliente.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido.")
        # El servicio debe ser instancia de Servicio.
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido.")
        self._cliente = cliente
        self._servicio = servicio
        # Duración numérica mayor que cero (validación delegada al servicio).
        try:
            d = float(duracion)
        except (TypeError, ValueError) as exc:
            raise ReservaInvalidaError("La duración debe ser numérica.") from exc
        if d <= 0:
            raise ReservaInvalidaError("La duración debe ser mayor que cero.")
        # Se delega la validación fina al servicio (polimorfismo).
        try:
            servicio.validar_parametros(d)
        except Exception as exc:
            # Encadenamiento: se explica el contexto de reserva.
            raise ReservaInvalidaError(f"Parámetros inválidos para {servicio.nombre}.") from exc
        self._duracion = d
        # Toda reserva nace pendiente.
        self._estado = "PENDIENTE"
        # Costo calculado al crear (sin impuesto por defecto).
        self._costo = servicio.calcular_costo(duracion=d)

    @property
    def estado(self):
        """Retorna el estado actual."""
        return self._estado

    @property
    def costo(self):
        """Retorna el costo calculado."""
        return self._costo

    def validar(self):
        """Valida que cliente, servicio y duración sigan siendo coherentes."""
        if self._duracion <= 0:
            raise ReservaInvalidaError("Duración inválida en la reserva.")
        return True

    def describir(self):
        """Descripción legible de la reserva."""
        return (f"Reserva[{self._id}] {self._estado} "
                f"cliente={self._cliente.nombre} servicio={self._servicio.nombre} "
                f"dur={self._duracion} costo={self._costo}")

    def confirmar(self):
        """Confirma una reserva pendiente si el servicio está disponible."""
        # Solo se puede confirmar desde PENDIENTE.
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar en estado {self._estado}.")
        # El servicio debe estar disponible.
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"Servicio '{self._servicio.nombre}' no disponible.")
        # Cambio de estado y registro en log.
        self._estado = "CONFIRMADA"
        logger.info("Reserva %s CONFIRMADA.", self._id)
        return True

    def cancelar(self):
        """Cancela una reserva pendiente o confirmada (no procesada/cancelada)."""
        # No se puede cancelar dos veces ni tras procesar.
        if self._estado in ("CANCELADA", "PROCESADA"):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar en estado {self._estado}.")
        self._estado = "CANCELADA"
        logger.info("Reserva %s CANCELADA.", self._id)
        return True

    def procesar(self):
        """Procesa (ejecuta) una reserva confirmada y recalcula el costo final."""
        # Solo una reserva confirmada puede procesarse.
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se procesa desde CONFIRMADA, actual: {self._estado}.")
        # Recalcula con impuesto del 19% como costo final profesional.
        self._costo = self._servicio.calcular_costo(
            duracion=self._duracion, impuesto=0.19, descuento=0.0)
        self._estado = "PROCESADA"
        logger.info("Reserva %s PROCESADA con costo %s.", self._id, self._costo)
        return self._costo


class SistemaGestion:
    """Gestor central con listas internas (clientes, servicios, reservas)."""

    def __init__(self):
        """Inicializa las listas vacías del sistema."""
        # Listas en memoria: simulan la BD sin usar ningún motor.
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        """Registra un cliente validado en la lista interna."""
        # Verifica el tipo antes de guardar.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Solo se registran objetos Cliente.")
        # Valida integralmente antes de guardar.
        cliente.validar()
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.describir())
        return cliente

    def agregar_servicio(self, servicio):
        """Agrega un servicio validado a la lista interna."""
        # Verifica el tipo.
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Solo se agregan objetos Servicio.")
        # Valida el servicio.
        servicio.validar()
        self.servicios.append(servicio)
        logger.info("Servicio agregado: %s", servicio.describir())
        return servicio

    def crear_reserva(self, identificador, cliente, servicio, duracion):
        """Crea y guarda una reserva validando disponibilidad."""
        # Identificador obligatorio.
        if identificador is None or str(identificador).strip() == "":
            raise ParametroFaltanteError("El id de reserva es obligatorio.")
        # El servicio debe estar disponible.
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"Servicio '{servicio.nombre}' no disponible.")
        # Se construye la reserva (puede lanzar ReservaInvalidaError encadenada).
        reserva = Reserva(identificador, cliente, servicio, duracion)
        self.reservas.append(reserva)
        logger.info("Reserva creada: %s", reserva.describir())
        return reserva

    def buscar_cliente(self, documento):
        """Busca un cliente por documento en la lista interna."""
        for c in self.clientes:
            if c.documento == str(documento).strip():
                return c
        return None

    def resumen(self):
        """Retorna el conteo de objetos gestionados."""
        return (f"Clientes={len(self.clientes)} "
                f"Servicios={len(self.servicios)} Reservas={len(self.reservas)}")
