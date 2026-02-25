"""
Módulo de acceso a datos del mercado financiero (Superintendencia Financiera).
Extrae tasas de crédito usando la API de Datos Abiertos de Colombia (Socrata).
Utiliza el patrón Envelope para almacenar un 'last_update' dentro del JSON,
evitando descargas redundantes en despliegues con Docker por 15 días.
"""
import os
import json
import time
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MarketRepo:
    def __init__(self):
        self.api_url = "https://www.datos.gov.co/resource/yvb2-ppaa.json"
        self.cache_file = "market_rates_cache.json"
        # Límite configurado a 15 días (15 días * 24 h * 60 min * 60 s)
        self.cache_duration_seconds = 15 * 24 * 60 * 60  

        self.top_banks = [
            "BANCOLOMBIA",
            "BANCO DE BOGOTA",
            "DAVIVIENDA",
            "BBVA COLOMBIA",
            "BANCO DE OCCIDENTE",
            "SCOTIABANK COLPATRIA",
            "BANCO CAJA SOCIAL",
            "BANCO POPULAR",
            "BANCO AV VILLAS"
        ]

    def get_credit_rates(self) -> List[Dict[str, Any]]:
        """
        Devuelve una lista filtrada y limpia con las tasas de crédito de los bancos principales.
        """
        raw_data = self._fetch_raw_data()
        return self._filter_top_banks(raw_data)

    def _fetch_raw_data(self) -> List[Dict[str, Any]]:
        """
        Lee los datos. Primero revisa el interior del JSON para verificar el 'last_update'.
        Si tiene más de 15 días, hace la petición a la API.
        """
        # 1. Intentar leer el caché y verificar su edad internamente
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_content = json.load(f)
                    
                    # Extraemos el timestamp guardado en el JSON (0 si no existe)
                    last_update = cache_content.get("last_update", 0)
                    
                    # Si la diferencia entre hoy y el last_update es menor a 15 días...
                    if (time.time() - last_update) < self.cache_duration_seconds:
                        logger.info("Retornando datos desde caché (Vigente por 15 días).")
                        return cache_content.get("data", [])
                    else:
                        logger.info("El caché superó los 15 días. Se requiere actualización.")
                        
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Error leyendo el caché, se descargará de nuevo: {e}")

        # 2. Si el archivo no existe o superó los 15 días, descargar de la API
        logger.info("Descargando datos frescos de la API de Socrata...")
        try:
            parametros = {
                "$limit": 1000,
                "$order": "fecha_corte DESC"
            }
            response = requests.get(self.api_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 3. Guardar en caché con la marca de tiempo exacta
            self._write_cache(data)
            return data

        except requests.RequestException as e:
            logger.error(f"Error al conectar con la API de Socrata: {e}")
            # Mecanismo de rescate: si Socrata falla hoy, devolvemos los datos del JSON pase lo que pase
            return self._read_fallback_cache()

    def _write_cache(self, data: List[Dict[str, Any]]) -> None:
        """
        Guarda los datos envolviéndolos en un diccionario que contiene el 'last_update'.
        """
        cache_content = {
            "last_update": time.time(),
            "data": data
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_content, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logger.error(f"Error al escribir caché: {e}")

    def _read_fallback_cache(self) -> List[Dict[str, Any]]:
        """
        Lee los datos del caché ignorando la fecha de expiración. 
        Se usa ÚNICAMENTE si la API externa se cae para no dejar la app inoperativa.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_content = json.load(f)
                    return cache_content.get("data", [])
            except (IOError, json.JSONDecodeError):
                pass
        return []

    def _filter_top_banks(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra el JSON crudo (sin cambios respecto a la versión anterior)."""
        filtered_rates = []
        for row in data:
            entidad_cruda = row.get("nombre_entidad", "").upper()
            if any(banco in entidad_cruda for banco in self.top_banks):
                tasa_str = row.get("tasa_efectiva_promedio")
                if not tasa_str:
                    continue
                try:
                    tasa_float = float(tasa_str)
                except ValueError:
                    continue

                filtered_rates.append({
                    "banco": entidad_cruda,
                    "tipo_credito": row.get("tipo_de_cr_dito", "No especificado"),
                    "producto": row.get("producto_de_cr_dito", "General"),
                    "tasa_ea": tasa_float,
                    "fecha_corte": row.get("fecha_corte", "")[:10]
                })
        return filtered_rates

# === ZONA DE PRUEBAS ===
if __name__ == "__main__":
    print("Test Start: Probando persistencia de 15 días...")
    repo = MarketRepo()
    resultados = repo.get_credit_rates()
    if resultados:
        print(f"Éxito: Se obtuvieron {len(resultados)} registros filtrados.")
    else:
        print("Fallo: El array está vacío.")