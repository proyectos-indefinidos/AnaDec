import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class NewsRepo:
    """
    Clase de Servicio (StateFul). 
    Encapsula la lógica de obtención de noticias financieras.
    """
    
    # DEFINIMOS EL TEMA POR DEFECTO AQUÍ (CONSTANTE DE CLASE)
    # Esto centraliza la configuración de búsqueda.
    DEFAULT_TOPIC = "(tasa de interes OR banco central OR inflacion OR pib OR economia) AND economia"

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.cache_noticias: Optional[pd.DataFrame] = pd.DataFrame()
        self.last_update: Optional[datetime] = None
        self.base_url = "https://newsapi.org/v2/everything"

    # Hacemos que 'filtro' sea opcional con '= None'
    def get_noticias(self, filtro: str = None) -> pd.DataFrame:
        """
        Obtiene noticias. Si no se especifica filtro, usa el tema financiero por defecto.
        """
        if not self.api_key:
            print("ERROR: No se encontró la NEWS_API_KEY.")
            return pd.DataFrame()

        # LOGICA DE SELECCION DE TEMA
        # Si el main no manda nada, usamos nuestro tema financiero predefinido
        tema_a_buscar = filtro if filtro else self.DEFAULT_TOPIC

        try:
            params = {
                'q': tema_a_buscar,
                'apiKey': self.api_key,
                'language': 'es',
                'sortBy': 'publishedAt',
                'pageSize': 20
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])

            if not articles:
                return pd.DataFrame()

            noticias_limpias = []
            for art in articles:
                noticias_limpias.append({
                    "Fecha": art.get("publishedAt", "")[:10],
                    "Fuente": art.get("source", {}).get("name", "Desconocido"),
                    "Título": art.get("title", ""),
                    "Descripción": art.get("description", "")
                })

            self.cache_noticias = pd.DataFrame(noticias_limpias)
            self.last_update = datetime.now()
            
            return self.cache_noticias

        except Exception as e:
            print(f"Error en NewsRepo: {e}")
            return pd.DataFrame()

    def force_update(self):
        """Limpia el caché para obligar a una nueva descarga."""
        self.cache_noticias = pd.DataFrame()
        self.last_update = None