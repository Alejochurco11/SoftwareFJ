"""Configuración centralizada del logger del sistema (archivo sistema.log)."""
# Toda la gestión de eventos y errores se registra aquí, sin usar bases de datos.
import logging  # Módulo estándar de registro de eventos.
import os  # Para resolver la ruta del archivo de log junto al paquete.


# Ruta del archivo de log (misma carpeta del paquete).
LOG_PATH = os.path.join(os.path.dirname(__file__), "sistema.log")


def obtener_logger(nombre="SoftwareFJ"):
    """Crea y configura el logger con salida a archivo y consola."""
    # Se obtiene (o crea) el logger con el nombre indicado.
    logger = logging.getLogger(nombre)
    # Se fija el nivel mínimo a INFO para capturar eventos relevantes.
    logger.setLevel(logging.INFO)
    # Si ya tiene manejadores se retorna tal cual (evita duplicados).
    if logger.handlers:
        return logger
    # Manejador de archivo: guarda todos los errores y eventos relevantes.
    manejador_archivo = logging.FileHandler(LOG_PATH, encoding="utf-8")
    # Manejador de consola: informa al usuario sin detener la aplicación.
    manejador_consola = logging.StreamHandler()
    # Formato común: fecha - nombre - nivel - mensaje.
    formato = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Se asigna el formato a ambos manejadores.
    manejador_archivo.setFormatter(formato)
    manejador_consola.setFormatter(formato)
    # Se registran los manejadores en el logger.
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)
    # Se retorna el logger listo para usar.
    return logger
