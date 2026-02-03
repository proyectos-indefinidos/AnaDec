from __future__ import annotations

from typing import Union

import pandas as pd

from .tasa_interes import TasaInteres as tasaInteres

Number = Union[int, float]


class Calculador:
    """
    Calculador simple para:
    
    - cuota fija,
    - interés simple,
    - valor futuro (compuesto),
    - conversiones VP <-> VF.

    Attributes:
        precision: Decimales para redondear la tasa periódica interna.
    """

    def __init__(self, precision: int = 6) -> None:
        if precision < 0:
            raise ValueError("precision no puede ser negativa.")
        self.precision = precision

   
    def tasa_periodica(self, tasa: tasaInteres) -> float:
        """
        Devuelve la tasa efectiva por período (vencida) para cálculos.

        Reglas:
        - Si es efectiva: i = valor
        - Si es nominal:  i = valor / m, donde m = periodo_nominal / periodo

        Anticipada -> vencida:
            i = d / (1 - d)

        Raises:
            ValueError: Si la tasa es inválida o sus periodos no cuadran.
        """
        if tasa.valor <= -1:
            raise ValueError("La tasa no puede ser <= -100% (valor <= -1).")

        tipo = str(tasa.tipo).strip().lower()
        i: float

        if tipo == "efectiva":
            i = float(tasa.valor)

        elif tipo == "nominal":
            periodo_nominal = getattr(tasa, "periodo_nominal", None)
            if periodo_nominal is None:
                raise ValueError("Tasa nominal requiere un periodo nominal.")
            if periodo_nominal <= 0 or tasa.periodo <= 0:
                raise ValueError("los periodos deben ser positivos.")

            m = float(periodo_nominal) / float(tasa.periodo)
            if m <= 0:
                raise ValueError("Relación de periodos inválida (m <= 0).")

            i = float(tasa.valor) / m

        else:
            raise ValueError("Tipo de tasa no reconocido. Use 'efectiva' o 'nominal'.")

        # Si la tasa viene anticipada, convertir a vencida.
        es_anticipada = bool(getattr(tasa, "es_anticipada", False))
        if es_anticipada:
            if i >= 1:
                raise ValueError("Tasa anticipada inválida: debe ser < 1 por período.")
            i = i / (1 - i)

        return round(i, self.precision)
    

    def validar_monto_plazos(self, monto: Number, plazos: int) -> None:
        """
        Valida los parámetros básicos para operaciones de crédito.

        Args:
            monto: Valor del principal del préstamo.
            plazos: Número de períodos del préstamo.

        Raises:
            TypeError: Si `monto` no es numérico o `plazos` no es entero.
            ValueError: Si `monto` es negativo o si `plazos` es <= 0.
        """
        if not isinstance(monto, (int, float)):
            raise TypeError("monto debe ser numérico (int o float).")
        if monto < 0:
            raise ValueError("monto no puede ser negativo.")

        if not isinstance(plazos, int):
            raise TypeError("plazos debe ser un entero.")
        if plazos <= 0:
            raise ValueError("plazos debe ser > 0.")

    
    
    def calcular_cuota_fija(self, monto: float, tasa: tasaInteres, plazos: int) -> float:
        """
        Calcula la cuota fija de un préstamo (sistema francés).

        Fórmula:
            cuota = P * i / (1 - (1 + i)^(-n))

        Args:
            monto: Principal del préstamo.
            tasa: TasaInteres (efectiva o nominal; anticipada se normaliza a vencida).
            plazos: Número de períodos.

        Returns:
            Cuota fija redondeada a 2 decimales.
        """
        self.validar_monto_plazos(monto, plazos)

        i = self.tasa_periodica(tasa)
        if i == 0:
            return round(float(monto) / plazos, 2)

        cuota = float(monto) * i / (1 - (1 + i) ** (-plazos))
        return round(cuota, 2)

    
    def interes_simple(self, principal: float, tasa: tasaInteres, periodos: int) -> float:
        """
        Calcula el interés simple.

        Fórmula:
            I = P * i * n

        Args:
            principal: Monto inicial (>= 0).
            tasa: TasaInteres.
            periodos: Número de períodos (>= 0).

        Returns:
            Interés simple acumulado.
        """
        if not isinstance(periodos, int):
            raise TypeError("periodos debe ser un entero.")
        if principal < 0 or periodos < 0:
            raise ValueError("principal debe ser >= 0 y periodos >= 0.")

        i = self.tasa_periodica(tasa)
        interes = float(principal) * i * periodos
        return round(interes, 2)
    
    

    def valor_futuro(self, valor_presente: float, tasa: tasaInteres, periodos: int) -> float:
        """
        Calcula valor futuro con interés compuesto.

        Fórmula:
            VF = VP * (1 + i)^n
        """
        if not isinstance(periodos, int):
            raise TypeError("periodos debe ser un entero.")
        if valor_presente < 0 or periodos < 0:
            raise ValueError("valor presente debe ser >= 0 y periodos >= 0.")

        i = self.tasa_periodica(tasa)
        vf = float(valor_presente) * ((1 + i) ** periodos)
        return round(vf, 2)

    def valor_presente(self, valor_futuro: float, tasa: tasaInteres, periodos: int) -> float:
        """
        Calcula valor presente descontando con interés compuesto.

        Fórmula:
            VP = VF / (1 + i)^n
        """
        if not isinstance(periodos, int):
            raise TypeError("periodos debe ser un entero.")
        if valor_futuro < 0 or periodos < 0:
            raise ValueError("valor_futuro debe ser >= 0 y periodos >= 0.")

        i = self.tasa_periodica(tasa)
        vp = float(valor_futuro) / ((1 + i) ** periodos)
        return round(vp, 2)

    
    def convertidor_valor_futuro_a_presente(self, valor_futuro: float, tasa: tasaInteres, periodos: int,) -> float:

        return self.valor_presente(valor_futuro, tasa, periodos)

    def convertidor_valor_presente_a_futuro(self, valor_presente: float, tasa: tasaInteres, periodos: int,) -> float:

        return self.valor_futuro(valor_presente, tasa, periodos)


if __name__ == "__main__":
    calc = Calculador()

    t_nom = tasaInteres.from_string("24% NA/MV")
    monto = 10000000
    plazos = 12

    print("Nominal:", t_nom.to_string())
    cuota = calc.calcular_cuota_fija(monto, t_nom, plazos)
    print("Cuota fija:", f"{cuota:,.2f}")


    t_eff = tasaInteres.from_string("6% TV")
    inversion = 5000000
    tiempo = 24

    print("\nEfectiva:", t_eff.to_string())
    vf = calc.valor_futuro(inversion, t_eff, tiempo)
    print("Valor futuro:", f"{vf:,.2f}")

    vp = calc.valor_presente(vf, t_eff, tiempo)
    print("Valor presente (desde VF):", f"{vp:,.2f}")
