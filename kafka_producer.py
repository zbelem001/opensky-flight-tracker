"""
Kafka Producer pour l'API OpenSky Network
Récupère les données des vols autour de l'aéroport de Ouagadougou
"""

import json
import time
import requests
import os
from kafka import KafkaProducer
from datetime import datetime
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Coordonnées de l'aéroport de Dubai (DXB) - Émirats Arabes Unis
# Dubai International Airport (un des aéroports les plus fréquentés au monde)
DUBAI_LAT = 25.2532
DUBAI_LON = 55.3657
RADIUS = 100  # km autour de l'aéroport

class OpenSkyProducer:
    def __init__(self, bootstrap_servers=['localhost:9092'], topic='flights-data'):
        """Initialise le producteur Kafka"""
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.api_url = "https://opensky-network.org/api/states/all"
        logger.info(f"Producer Kafka initialisé sur le topic: {topic}")
    
    def fetch_flights(self):
        """Récupère les données des vols depuis l'API OpenSky"""
        try:
            # Calcul de la bounding box autour de Dubai
            # Approximation: 1 degré ≈ 111 km
            delta = RADIUS / 111.0
            
            params = {
                'lamin': DUBAI_LAT - delta,
                'lomin': DUBAI_LON - delta,
                'lamax': DUBAI_LAT + delta,
                'lomax': DUBAI_LON + delta
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('states', [])
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête API: {e}")
            return []
    
    def parse_flight_data(self, state):
        """Parse les données d'un vol depuis le format OpenSky"""
        try:
            return {
                'icao24': state[0],
                'callsign': state[1].strip() if state[1] else 'N/A',
                'origin_country': state[2],
                'time_position': state[3],
                'last_contact': state[4],
                'longitude': state[5],
                'latitude': state[6],
                'baro_altitude': state[7],
                'on_ground': state[8],
                'velocity': state[9],
                'true_track': state[10],
                'vertical_rate': state[11],
                'sensors': state[12],
                'geo_altitude': state[13],
                'squawk': state[14],
                'spi': state[15],
                'position_source': state[16],
                'timestamp': datetime.now().isoformat(),
                'airport': 'DXB'  # Code IATA Dubai International Airport
            }
        except (IndexError, TypeError) as e:
            logger.error(f"Erreur parsing: {e}")
            return None
    
    def calculate_distance(self, lat, lon):
        """Calcule la distance approximative depuis Dubai (en km)"""
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(DUBAI_LAT), radians(DUBAI_LON)
        lat2, lon2 = radians(lat), radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return 6371 * c  # Rayon de la Terre en km
    
    def classify_flight_status(self, flight):
        """Classifie le statut du vol (arrivée, départ, stationnement)"""
        if flight['on_ground']:
            return 'stationnement'
        
        distance = self.calculate_distance(flight['latitude'], flight['longitude'])
        
        if distance < 10:  # Moins de 10km
            if flight['vertical_rate'] and flight['vertical_rate'] < -1:
                return 'arrivée'
            elif flight['vertical_rate'] and flight['vertical_rate'] > 1:
                return 'départ'
        
        return 'en_vol'
    
    def send_to_kafka(self, flight_data):
        """Envoie les données vers Kafka"""
        try:
            status = self.classify_flight_status(flight_data)
            flight_data['status'] = status
            
            self.producer.send(
                self.topic,
                key=flight_data['icao24'],
                value=flight_data
            )
            logger.info(f"Vol envoyé: {flight_data['callsign']} - {status}")
        
        except Exception as e:
            logger.error(f"Erreur envoi Kafka: {e}")
    
    def run(self, interval=30):
        """Lance le producteur en boucle"""
        logger.info("Démarrage du producer OpenSky...")
        
        try:
            while True:
                flights = self.fetch_flights()
                
                if flights:
                    logger.info(f"{len(flights)} vols détectés")
                    for state in flights:
                        flight_data = self.parse_flight_data(state)
                        if flight_data and flight_data['latitude'] and flight_data['longitude']:
                            self.send_to_kafka(flight_data)
                else:
                    logger.warning("Aucun vol détecté dans la zone")
                
                self.producer.flush()
                logger.info(f"Attente de {interval} secondes...")
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Arrêt du producer...")
        finally:
            self.producer.close()

if __name__ == "__main__":
    # Lire les variables d'environnement
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(',')
    topic = os.getenv('KAFKA_TOPIC', 'flights-data')
    interval = int(os.getenv('FETCH_INTERVAL', '30'))
    
    producer = OpenSkyProducer(
        bootstrap_servers=bootstrap_servers,
        topic=topic
    )
    producer.run(interval=interval)
