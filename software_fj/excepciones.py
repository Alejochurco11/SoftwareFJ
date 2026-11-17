"""Módulo de excepciones personalizadas del sistema Software FJ."""
# Excepciones base y específicas para manejo robusto y registro en logs.


class SoftwareFJError(Exception):
    """Clase base para todos los errores del sistema Software FJ."""
    pass


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no pasan la validación."""
    pass


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no está disponible para reserva."""
    pass


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza ante intentos de reserva incorrectos (duración, estado, etc.)."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación no permitida por el estado actual."""
    pass


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos recibe valores inconsistentes."""
    pass
