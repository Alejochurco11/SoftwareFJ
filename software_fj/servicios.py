"""Servicios especializados: ReservaSala, AlquilerEquipo y AsesoriaEspecializada."""
# Cada uno hereda de Servicio e implementa polimorfismo real.
from .entidades import Servicio  # Clase abstracta padre.
from .excepciones import (  # Errores de dominio.
    ParametroFaltanteError,
    CalculoInconsistenteError,
)


class ReservaSala(Servicio):
    """Servicio de reserva de salas por horas."""

    def __init__(self, identificador, nombre, precio_base, capacidad, tipo_sala="Estándar",
                 disponible=True):
        """Crea la sala con capacidad y tipo."""
        # Inicializa la parte común del servicio.
        super().__init__(identificador, nombre, precio_base, disponible)
        # Capacidad obligatoria mayor que cero.
        if capacidad is None:
            raise ParametroFaltanteError("La capacidad de la sala es obligatoria.")
        try:
            cap = int(capacidad)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("La capacidad debe ser numérica.") from exc
        if cap <= 0:
            raise CalculoInconsistenteError("La capacidad debe ser mayor que cero.")
        self._capacidad = cap
        # Tipo de sala (Estándar, Premium, Auditorio...).
        self._tipo_sala = str(tipo_sala).strip() or "Estándar"

    def validar_parametros(self, duracion):
        """Valida la duración en horas (1 a 12)."""
        try:
            d = float(duracion)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("La duración debe ser numérica.") from exc
        if d <= 0 or d > 12:
            raise CalculoInconsistenteError("Duración de sala inválida (1 a 12 horas).")
        return True

    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0):
        """Costo = precio_base * horas + recargo 20% si capacidad > 20."""
        # Primero se validan los parámetros de entrada.
        self.validar_parametros(duracion)
        # Subtotal según horas.
        subtotal = self._precio_base * float(duracion)
        # Recargo del 20% para salas grandes (capacidad mayor a 20).
        if self._capacidad > 20:
            subtotal *= 1.20
        # Se aplican impuesto y descuento con validación estricta.
        return self._aplicar_impuesto_descuento(subtotal, impuesto, descuento)

    def validar(self):
        """Validación integral de la sala."""
        return self.validar_parametros(1)

    def describir(self):
        """Descripción legible de la sala."""
        return (f"Sala[{self._id}] {self._nombre} tipo={self._tipo_sala} "
                f"cap={self._capacidad} precio_hora={self._precio_base}")


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por días y cantidad."""

    def __init__(self, identificador, nombre, precio_base, tipo_equipo, stock,
                 disponible=True):
        """Crea el equipo con tipo y stock disponible."""
        # Inicializa la parte común.
        super().__init__(identificador, nombre, precio_base, disponible)
        # Tipo de equipo obligatorio.
        if tipo_equipo is None or str(tipo_equipo).strip() == "":
            raise ParametroFaltanteError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = str(tipo_equipo).strip()
        # Stock numérico mayor o igual a cero.
        try:
            s = int(stock)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("El stock debe ser numérico.") from exc
        if s < 0:
            raise CalculoInconsistenteError("El stock no puede ser negativo.")
        self._stock = s
        # Cantidad solicitada por defecto (se ajusta por reserva).
        self._cantidad = 1

    def validar_parametros(self, duracion):
        """Valida duración en días (1 a 30) y que haya stock."""
        try:
            d = float(duracion)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("La duración (días) debe ser numérica.") from exc
        if d <= 0 or d > 30:
            raise CalculoInconsistenteError("Duración de alquiler inválida (1 a 30 días).")
        if self._stock <= 0:
            # Servicio existe pero sin unidades: no disponible para operar.
            from .excepciones import ServicioNoDisponibleError
            raise ServicioNoDisponibleError("Sin stock disponible para este equipo.")
        return True

    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0, cantidad=1):
        """Costo = precio_base * cantidad * días (sobrecarga con cantidad)."""
        # Valida duración y stock.
        self.validar_parametros(duracion)
        # Cantidad entera mayor que cero y menor o igual al stock.
        try:
            c = int(cantidad)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("La cantidad debe ser numérica.") from exc
        if c <= 0:
            raise CalculoInconsistenteError("La cantidad debe ser mayor que cero.")
        if c > self._stock:
            from .excepciones import ServicioNoDisponibleError
            raise ServicioNoDisponibleError(
                f"Stock insuficiente: pide {c}, hay {self._stock}.")
        # Subtotal por cantidad y días.
        subtotal = self._precio_base * c * float(duracion)
        return self._aplicar_impuesto_descuento(subtotal, impuesto, descuento)

    def validar(self):
        """Validación integral del equipo."""
        return self.validar_parametros(1)

    def describir(self):
        """Descripción legible del equipo."""
        return (f"Equipo[{self._id}] {self._nombre} tipo={self._tipo_equipo} "
                f"stock={self._stock} precio_dia={self._precio_base}")


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada por horas y nivel."""

    # Factores multiplicadores por nivel de especialidad.
    FACTORES = {"Básica": 1.0, "Intermedia": 1.5, "Avanzada": 2.0}

    def __init__(self, identificador, nombre, precio_base, especialidad, nivel="Básica",
                 disponible=True):
        """Crea la asesoría con especialidad y nivel."""
        # Inicializa la parte común.
        super().__init__(identificador, nombre, precio_base, disponible)
        # Especialidad obligatoria.
        if especialidad is None or str(especialidad).strip() == "":
            raise ParametroFaltanteError("La especialidad es obligatoria.")
        self._especialidad = str(especialidad).strip()
        # Nivel debe estar en el catálogo permitido.
        if nivel not in self.FACTORES:
            raise ParametroFaltanteError(
                f"Nivel inválido. Use: {list(self.FACTORES.keys())}.")
        self._nivel = nivel

    def validar_parametros(self, duracion):
        """Valida duración en horas (1 a 8)."""
        try:
            d = float(duracion)
        except (TypeError, ValueError) as exc:
            raise ParametroFaltanteError("La duración debe ser numérica.") from exc
        if d <= 0 or d > 8:
            raise CalculoInconsistenteError("Duración de asesoría inválida (1 a 8 horas).")
        return True

    def calcular_costo(self, duracion=1, impuesto=0.0, descuento=0.0):
        """Costo = precio_base * horas * factor_nivel."""
        # Valida la duración.
        self.validar_parametros(duracion)
        # Aplica el factor según el nivel.
        subtotal = self._precio_base * float(duracion) * self.FACTORES[self._nivel]
        return self._aplicar_impuesto_descuento(subtotal, impuesto, descuento)

    def validar(self):
        """Validación integral de la asesoría."""
        return self.validar_parametros(1)

    def describir(self):
        """Descripción legible de la asesoría."""
        return (f"Asesoría[{self._id}] {self._nombre} esp={self._especialidad} "
                f"nivel={self._nivel} precio_hora={self._precio_base}")
