"""Punto de entrada consola: simula 12 operaciones válidas e inválidas sin caerse."""
# Demuestra try/except, try/except/else, try/except/finally y encadenamiento.
from software_fj.entidades import Cliente  # Entidad de cliente.
from software_fj.servicios import (  # Tres servicios especializados.
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada,
)
from software_fj.reservas import SistemaGestion  # Gestor con listas internas.
from software_fj.excepciones import SoftwareFJError  # Base de errores propios.
from software_fj.logger_config import obtener_logger  # Logger a sistema.log.

# Logger principal de la demo.
logger = obtener_logger()


def operacion(titulo, funcion):
    """Ejecuta una operación protegida para que el sistema siga activo ante errores."""
    print(f"\n--- {titulo} ---")
    try:
        # Se ejecuta la operación solicitada.
        resultado = funcion()
    except SoftwareFJError as err:
        # Errores controlados del dominio: se registran y se continúa.
        logger.error("Fallo controlado en '%s': %s", titulo, err)
        print(f"[ERROR CONTROLADO] {err}")
        return None
    except Exception as err:
        # Cualquier otro error inesperado también se registra sin tumbar la app.
        logger.exception("Fallo inesperado en '%s'", titulo)
        print(f"[ERROR INESPERADO] {err}")
        return None
    else:
        # Bloque else: solo si NO hubo excepción (uso exigido de try/except/else).
        logger.info("Operación '%s' exitosa.", titulo)
        print(f"[OK] {resultado}")
        return resultado
    finally:
        # Bloque finally: siempre se ejecuta (uso exigido de try/finally).
        print("(fin de operación, el sistema sigue activo)")


def main():
    """Orquesta las 12 operaciones de la simulación."""
    print("=== SOFTWARE FJ - Sistema Integral (consola, sin BD) ===")
    sistema = SistemaGestion()

    # Contenedores para reutilizar objetos entre operaciones.
    ctx = {}

    # OP 1: registro válido de cliente (caso feliz).
    def op1():
        c = Cliente("C-001", "Steven Alejandro Bello", "12345678",
                    "steven.bello@unad.edu.co", "+57 3001234567")
        sistema.registrar_cliente(c)
        ctx["cliente_ok"] = c
        return c.describir()
    operacion("OP1 Registrar cliente válido", op1)

    # OP 2: registro inválido (email malo) -> ClienteInvalidoError.
    def op2():
        c = Cliente("C-002", "Ana Pérez", "87654321", "correo-sin-arroba")
        sistema.registrar_cliente(c)
        return c.describir()
    operacion("OP2 Registrar cliente con email inválido (falla esperada)", op2)

    # OP 3: registro inválido (documento con letras) -> ClienteInvalidoError.
    def op3():
        c = Cliente("C-003", "Luis Gómez", "ABC12", "luis@mail.com")
        sistema.registrar_cliente(c)
        return c.describir()
    operacion("OP3 Registrar cliente con documento inválido (falla esperada)", op3)

    # OP 4: crear servicio de sala válido.
    def op4():
        s = ReservaSala("S-001", "Sala de Juntas Premium", 50000,
                        capacidad=25, tipo_sala="Premium")
        sistema.agregar_servicio(s)
        ctx["sala"] = s
        # Demuestra método sobrecargado variante 1 (base).
        base = s.calcular_costo_base(duracion=2)
        return f"{s.describir()} | costo_base(2h)={base}"
    operacion("OP4 Crear ReservaSala válida + sobrecarga base", op4)

    # OP 5: crear servicio con precio negativo -> CalculoInconsistenteError.
    def op5():
        s = AlquilerEquipo("S-002", "Video Beam", -1000, tipo_equipo="Proyector", stock=5)
        sistema.agregar_servicio(s)
        return s.describir()
    operacion("OP5 Crear equipo con precio negativo (falla esperada)", op5)

    # OP 6: crear asesoría válida + demostrar las 3 sobrecargas.
    def op6():
        a = AsesoriaEspecializada("S-003", "Asesoría Cloud", 80000,
                                  especialidad="DevOps", nivel="Avanzada")
        sistema.agregar_servicio(a)
        ctx["asesoria"] = a
        b = a.calcular_costo_base(duracion=2)
        c = a.calcular_costo_con_impuesto(duracion=2, impuesto=0.19)
        d = a.calcular_costo_con_descuento(duracion=2, impuesto=0.19, descuento=0.1)
        return f"{a.describir()} | base={b} | c/impuesto={c} | c/desc={d}"
    operacion("OP6 Crear Asesoría válida + 3 sobrecargas", op6)

    # OP 7: reserva exitosa + confirmar + procesar (camino feliz con else).
    def op7():
        r = sistema.crear_reserva("R-001", ctx["cliente_ok"], ctx["sala"], duracion=2)
        ctx["reserva_ok"] = r
        r.confirmar()
        # try/except/else interno: recalcula costo final solo si confirma bien.
        try:
            total = r.procesar()
        except SoftwareFJError:
            raise
        else:
            return f"{r.describir()} | total_final={total}"
    operacion("OP7 Reserva exitosa sala (confirmar+procesar)", op7)

    # OP 8: reserva con duración 0 -> ReservaInvalidaError encadenada.
    def op8():
        return sistema.crear_reserva("R-002", ctx["cliente_ok"], ctx["sala"],
                                     duracion=0).describir()
    operacion("OP8 Reserva con duración 0 (falla esperada)", op8)

    # OP 9: reserva con servicio no disponible -> ServicioNoDisponibleError.
    def op9():
        ctx["sala"].disponible = False
        try:
            return sistema.crear_reserva("R-003", ctx["cliente_ok"], ctx["sala"],
                                         duracion=1).describir()
        finally:
            # Se restaura para no bloquear el resto de la demo.
            ctx["sala"].disponible = True
    operacion("OP9 Reserva con servicio no disponible (falla esperada)", op9)

    # OP 10: cálculo inconsistente (descuento 95% > 90%) -> CalculoInconsistenteError.
    def op10():
        valor = ctx["asesoria"].calcular_costo(duracion=2, impuesto=0.19, descuento=0.95)
        return f"costo={valor}"
    operacion("OP10 Costo con descuento 95% (falla esperada)", op10)

    # OP 11: cancelar y luego intentar procesar cancelada -> OperacionNoPermitida.
    def op11():
        r = sistema.crear_reserva("R-004", ctx["cliente_ok"], ctx["asesoria"], duracion=2)
        ctx["reserva_cancel"] = r
        r.confirmar()
        r.cancelar()
        # Esto debe fallar: cancelada ya no se puede procesar.
        r.procesar()
        return r.describir()
    operacion("OP11 Cancelar y procesar cancelada (falla esperada)", op11)

    # OP 12: alquiler de equipo válido + reserva (tercer servicio en acción).
    def op12():
        eq = AlquilerEquipo("S-004", "Portátil Empresarial", 60000,
                            tipo_equipo="Laptop", stock=10)
        sistema.agregar_servicio(eq)
        ctx["equipo"] = eq
        r = sistema.crear_reserva("R-005", ctx["cliente_ok"], eq, duracion=3)
        r.confirmar()
        total = r.procesar()
        return f"{r.describir()} | total_final={total}"
    operacion("OP12 Equipo válido + reserva exitosa", op12)

    # OP 13: equipo con stock 0 -> ServicioNoDisponibleError al validar.
    def op13():
        eq = AlquilerEquipo("S-005", "Portátil Gamer", 60000,
                            tipo_equipo="Laptop", stock=0)
        sistema.agregar_servicio(eq)
        return sistema.crear_reserva("R-006", ctx["cliente_ok"], eq,
                                     duracion=3).describir()
    operacion("OP13 Equipo sin stock (falla esperada)", op13)

    # Resumen final: el sistema nunca se cayó.
    print("\n=== RESUMEN FINAL ===")
    print(sistema.resumen())
    print(f"Reservas creadas: {len(sistema.reservas)}")
    for r in sistema.reservas:
        print(" -", r.describir())
    print("\nVer detalle de errores en software_fj/sistema.log")
    logger.info("Simulación completa: %s", sistema.resumen())


if __name__ == "__main__":
    main()
