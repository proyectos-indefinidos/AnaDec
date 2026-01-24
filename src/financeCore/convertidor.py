#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
convertidor.py

Servicios de conversión de tasas de interés.

Este módulo opera sobre el objeto de dominio `TasaInteres` y permite:
- Convertir tasas efectivas entre periodos (MV/TV/SV/EA).
- Pasar de nominal a efectiva periódica y viceversa.
- Cambiar la frecuencia de capitalización de tasas nominales.
- Estandarizar cualquier tasa a EA (Efectiva Anual).
"""

from __future__ import annotations

from .tasa_interes import TasaInteres


class Convertidor:
    """Servicio para convertir tasas de interés."""

    def __init__(self, precision: int = 6) -> None:
        """
        Args:
            precision: Decimales de redondeo para resultados.
        """
        self.precision = precision

    def cambiar_temporalidad_en_efectivo(self, tasa: TasaInteres, nuevo_periodo: int) -> TasaInteres:
        """Convierte una tasa efectiva a otra temporalidad.

        Fórmula:
            (1 + i_nuevo) = (1 + i_actual)^(nuevo_periodo / periodo_actual)

        Args:
            tasa: TasaInteres con tipo="efectiva".
            nuevo_periodo: Periodo destino en meses (1, 3, 6, 12).

        Returns:
            Nueva TasaInteres efectiva equivalente.

        Raises:
            ValueError: Si `tasa` no es efectiva o `nuevo_periodo` no es válido.
        """
        if tasa.tipo != "efectiva":
            raise ValueError("cambiar_temporalidad_en_efectivo requiere una tasa efectiva.")
        if nuevo_periodo <= 0:
            raise ValueError("nuevo_periodo debe ser positivo.")

        if tasa.periodo == nuevo_periodo:
            return TasaInteres(
                valor=round(tasa.valor, self.precision),
                periodo=tasa.periodo,
                tipo="efectiva",
                es_anticipada=tasa.es_anticipada,
            )

        i_nuevo = (1 + tasa.valor) ** (nuevo_periodo / tasa.periodo) - 1
        return TasaInteres(
            valor=round(i_nuevo, self.precision),
            periodo=int(nuevo_periodo),
            tipo="efectiva",
            es_anticipada=False,
        )

    def nominal_a_efectiva_periodica(self, tasa: TasaInteres) -> TasaInteres:
        """Convierte una tasa nominal a su efectiva periódica de capitalización.

        Paso 1 (quitar nominal):
            i_periodica = tasa_nominal / n
            n = periodo_nominal / periodo_capitalizacion

        Si es anticipada, se asume que la tasa periódica resultante es un descuento d y se
        transforma a interés vencido:
            i = d / (1 - d)

        Args:
            tasa: TasaInteres con tipo="nominal".

        Returns:
            TasaInteres efectiva periódica con periodo igual al de capitalización.

        Raises:
            ValueError: Si `tasa` no es nominal o los periodos son inválidos.
        """
        if tasa.tipo != "nominal":
            raise ValueError("nominal_a_efectiva_periodica requiere una tasa nominal.")

        n = tasa.periodo_nominal / tasa.periodo
        if n <= 0:
            raise ValueError("Relación de periodos inválida.")

        i_periodica = tasa.valor / n

        if tasa.es_anticipada:
            if i_periodica >= 1:
                raise ValueError("Descuento anticipado periódico no puede ser >= 100%.")
            i_periodica = i_periodica / (1 - i_periodica)

        return TasaInteres(
            valor=round(i_periodica, self.precision),
            periodo=tasa.periodo,
            tipo="efectiva",
            es_anticipada=False,
        )

    def efectiva_periodica_a_nominal(
        self,
        tasa: TasaInteres,
        periodo_nominal: int,
        periodo_capitalizacion: int,
        es_anticipada: bool,
    ) -> TasaInteres:
        """Convierte una efectiva periódica a una nominal.

        Si es vencida:
            tasa_nominal = i_periodica * n

        Si es anticipada:
            d = i / (1 + i)
            tasa_nominal = d * n

        Donde:
            n = periodo_nominal / periodo_capitalizacion

        Args:
            tasa: TasaInteres efectiva periódica.
            periodo_nominal: Periodo nominal en meses (1, 3, 6, 12).
            periodo_capitalizacion: Periodo de capitalización en meses (1, 3, 6, 12).
            es_anticipada: True si nominal anticipada, False si vencida.

        Returns:
            TasaInteres nominal equivalente.

        Raises:
            ValueError: Si `tasa` no es efectiva o la relación de periodos no es válida.
        """
        if tasa.tipo != "efectiva":
            raise ValueError("efectiva_periodica_a_nominal requiere una tasa efectiva.")

        n = periodo_nominal / periodo_capitalizacion
        if n <= 0:
            raise ValueError("Relación de periodos inválida.")

        i = tasa.valor
        if es_anticipada:
            d = i / (1 + i)
            nom = d * n
        else:
            nom = i * n

        return TasaInteres(
            valor=round(nom, self.precision),
            periodo=int(periodo_capitalizacion),
            tipo="nominal",
            es_anticipada=es_anticipada,
            periodo_nominal=int(periodo_nominal),
        )

    def cambiar_frecuencia(self, tasa: TasaInteres, nuevo_periodo: int) -> TasaInteres:
        """Cambia la frecuencia de una tasa efectiva o nominal.

        - Si es efectiva: cambia temporalidad directamente.
        - Si es nominal:
            1) nominal -> efectiva periódica (paso 1)
            2) cambia temporalidad efectiva (paso 2)
            3) efectiva periódica -> nominal (re-nominaliza)

        Args:
            tasa: TasaInteres nominal o efectiva.
            nuevo_periodo: Periodo destino en meses (1, 3, 6, 12).

        Returns:
            TasaInteres equivalente con el nuevo periodo.

        Raises:
            ValueError: Si `nuevo_periodo` no es válido.
        """
        if nuevo_periodo <= 0:
            raise ValueError("nuevo_periodo debe ser positivo.")

        if tasa.tipo == "efectiva":
            return self.cambiar_temporalidad_en_efectivo(tasa, nuevo_periodo)

        i_actual = self.nominal_a_efectiva_periodica(tasa)
        i_nuevo = self.cambiar_temporalidad_en_efectivo(i_actual, nuevo_periodo)

        return self.efectiva_periodica_a_nominal(
            tasa=i_nuevo,
            periodo_nominal=tasa.periodo_nominal,
            periodo_capitalizacion=nuevo_periodo,
            es_anticipada=tasa.es_anticipada,
        )

    def tasa_a_ea_std(self, tasa: TasaInteres) -> float:
        """Convierte cualquier tasa (nominal o efectiva) a EA (efectiva anual).

        Args:
            tasa: TasaInteres nominal o efectiva.

        Returns:
            Valor decimal de la EA equivalente (ej. 0.2682...).

        Raises:
            ValueError: Si los periodos son inconsistentes.
        """
        if tasa.tipo == "efectiva":
            return self.cambiar_temporalidad_en_efectivo(tasa, 12).valor

        i_periodica = self.nominal_a_efectiva_periodica(tasa)
        return self.cambiar_temporalidad_en_efectivo(i_periodica, 12).valor


if __name__ == "__main__":
    convertidor = Convertidor()

    t_nom = TasaInteres.from_string("24% NA/MV")
    print("Nominal:", t_nom.to_string())
    print("EA:", convertidor.tasa_a_ea_std(t_nom))

    t_eff_tv = TasaInteres.from_string("6% TV")
    print("Vencida:", t_eff_tv.to_string())
    print("EA:", convertidor.tasa_a_ea_std(t_eff_tv))

    print("24% NA/MV -> NA/TV:", convertidor.cambiar_frecuencia(t_nom, 3).to_string())
    print("6% TV -> EA:", convertidor.cambiar_frecuencia(t_eff_tv, 12).to_string())
