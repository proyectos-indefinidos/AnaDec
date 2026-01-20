from numpy import rint


class Convertidor:
    """Convertidor de tasas de interés con precisión de 6 dígitos."""
    def __init__(self):
        self.precision = 6
#El siguiente método convierte una tasa de interés de una temporalidad a otra
#Los params, funcionan de la siguiente manera:
#tasa: es la tasa de interés que se quiere convertir
#periodo_actual: es la temporalidad en la que se encuentra la tasa
#(puede ser 1(mes), 3(trimestre), 6(semestre), 12(año))
#nuevo_periodo:
    def cambiar_temporalidad_en_efectivo(self, tasa, periodo_actual, nuevo_periodo):
        """cambia la temporalidad de una tasa en efectivo a otra."""
        if periodo_actual <= 0 and nuevo_periodo <= 0:
            raise ValueError("Los períodos deben ser positivos y estar en la misma unidad")
        if tasa <= -1:
            raise ValueError("La tasa efectiva no puede ser <= -100%")
        if periodo_actual == nuevo_periodo:
            return round(tasa, self.precision)
        i_nuevo = (1 + tasa) ** (nuevo_periodo / periodo_actual) - 1
        return round(i_nuevo, self.precision)
#TODO: toca sacar de alguna forma la inflacion a la hora de cambiar de frecuencia, para tener en cuenta si
#se quiere cambiar a una frecuencia mayor o menor de la que se tiene

    def cambiar_temporalidad_en_nominal(self, tasa):
        pass

    def cambiar_frecuencia(self, tasa, nuevo_periodo):
        pass

    def tasa_a_ea_std(self, tasa):
        """Convierte generalmente a Efectiva Anual(EA)."""
        pass

if __name__ == "__main__":
    convertidor = Convertidor()
    # Ejemplo de uso, se puede revisar en las diapos, que voy a adjuntar, esta correcto!
    print(convertidor.cambiar_temporalidad_en_efectivo(0.06, 3, 12))