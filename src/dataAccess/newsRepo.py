#!/usr/bin/python
# -*- coding: utf-8 -*-

class NewsRepo:
    """Clase de Servicio (StateFul). Almacena las noticias mediante API de noticias(TBD), de esa forma, se almacenan dentro del cache."""
    def __init__(self):
        self.API_KEY = None
        self.cache_noticias = None
        self.last_update = None

    def get_noticias(self, filtro):
        """Obtiene las noticias y las almacena dentro del DataFrame."""
        pass

    def force_update(self, ):
        """Fuerza la actualización del feed de noticias."""
        pass
