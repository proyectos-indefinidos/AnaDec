#!/usr/bin/python
# -*- coding: utf-8 -*-

class TasaInteres:
    """Donde se reciben los datos creados de la clase estandarizador y se crean los objetos TasaInteres. De esta clase depende el convertidor, comparador y calculador. Solo creación de objetos."""
    def __init__(self):
        self.valor = None
        self.periodo = None
        self.tipo = None
        self.es_anticipada = None
