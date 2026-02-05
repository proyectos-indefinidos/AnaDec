import os
import logging
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Optional

# Configurar logging para este módulo
logger = logging.getLogger(__name__)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; if it's not installed, we assume
    # environment variables are already provided by the OS/container.
    pass

class NewsRepo:
    """
    Clase de Servicio (StateFul). 
    Encapsula la lógica de obtención de noticias financieras.
    """
    
    # DEFINIMOS EL TEMA POR DEFECTO AQUÍ (CONSTANTE DE CLASE)
    # Esto centraliza la configuración de búsqueda.
    DEFAULT_TOPIC = "(tasa de interés OR banco central OR inflación OR pib OR economia) AND economia"

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.cache_noticias: pd.DataFrame = pd.DataFrame()
        self.last_update: Optional[datetime] = None
        self.base_url = "https://newsapi.org/v2/everything"
        self.cache_duration_minutes = 30  # Cache duration in minutes

    # Hacemos que 'filtro' sea opcional con '= None'
    def get_noticias(self, filtro: str = None) -> pd.DataFrame:
        """
        Obtiene noticias. Si no se especifica filtro, usa el tema financiero por defecto.
        Implementa caché para evitar llamadas redundantes a la API.
        """
        if not self.api_key or not self.api_key.strip():
            logger.error("ERROR: No se encontró la NEWS_API_KEY o está vacía.")
            return pd.DataFrame()

        # LOGICA DE SELECCION DE TEMA
        # Si el main no manda nada, usamos nuestro tema financiero predefinido
        tema_a_buscar = filtro if filtro else self.DEFAULT_TOPIC

        # Verificar si hay caché válido
        if self._is_cache_valid():
            logger.info("Usando caché de noticias")
            return self.cache_noticias

        try:
            params = {
                'q': tema_a_buscar,
                'apiKey': self.api_key,
                'language': 'es',
                'sortBy': 'publishedAt',
                'pageSize': 20
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])

            if not articles:
                return pd.DataFrame()

            noticias_limpias = []
            for art in articles:
                published_raw = art.get("publishedAt")
                fecha = ""
                if isinstance(published_raw, str):
                    try:
                        # Intentar parsear fecha/hora en formato ISO 8601
                        fecha_dt = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
                        fecha = fecha_dt.date().isoformat()
                    except ValueError:
                        # Como respaldo, usar los primeros 10 caracteres solo si la cadena es suficientemente larga
                        if len(published_raw) >= 10:
                            fecha = published_raw[:10]
                
                noticias_limpias.append({
                    "Fecha": fecha,
                    "Fuente": art.get("source", {}).get("name", "Desconocido"),
                    "Título": art.get("title", ""),
                    "Descripción": art.get("description", "")
                })

            self.cache_noticias = pd.DataFrame(noticias_limpias)
            self.last_update = datetime.now(timezone.utc)
            
            return self.cache_noticias

        except requests.RequestException as e:
            logger.error(f"Error en NewsRepo (problema de red/HTTP): {e}")
            return pd.DataFrame()

    def _is_cache_valid(self) -> bool:
        """Verifica si el caché es válido basándose en la última actualización."""
        if self.last_update is None or self.cache_noticias.empty:
            return False
        
        time_since_update = datetime.now(timezone.utc) - self.last_update
        return time_since_update.total_seconds() / 60 < self.cache_duration_minutes

    def force_update(self):
        """Limpia el caché para obligar a una nueva descarga."""
        self.cache_noticias = pd.DataFrame()
        self.last_update = None