import pandas as pd

from financeCore import tasaInteres


class Calculador:
    """
    Proyecta como el tiempo se traduce en dinero.
    Tiene en cuenta 360 días como base comercial.
    """
    def __init__(self):
        self.dias_por_anio = 360

    def calcular_cuota_fija(self, monto: float, tasa: tasaInteres, plazos: int):
        pass

    def generar_tabla_amortizacion(self, monto: float, tasa: tasaInteres, plazos: int):
        pass

    def calcular_retorno_inversion(self, inversion: float, tasa: tasaInteres, tiempo_meses: int) -> float:
        pass
