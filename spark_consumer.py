"""
Spark Streaming Consumer pour traiter les données de vols en temps réel
Calcule des statistiques et agrégations sur les vols
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightStreamProcessor:
    def __init__(self):
        """Initialise la session Spark avec les packages nécessaires"""
        # Nettoyer les anciens fichiers au démarrage pour éviter les conflits
        self.cleanup_old_data()
        
        self.spark = SparkSession.builder \
            .appName("OpenSkyFlightProcessor") \
            .config("spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
            .config("spark.driver.extraJavaOptions", 
                    "--add-opens=java.base/java.lang=ALL-UNNAMED "
                    "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
                    "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
                    "--add-opens=java.base/java.io=ALL-UNNAMED "
                    "--add-opens=java.base/java.util=ALL-UNNAMED "
                    "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED") \
            .config("spark.executor.extraJavaOptions", 
                    "--add-opens=java.base/java.lang=ALL-UNNAMED "
                    "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
                    "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
                    "--add-opens=java.base/java.io=ALL-UNNAMED "
                    "--add-opens=java.base/java.util=ALL-UNNAMED "
                    "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Session Spark initialisée")
    
    def cleanup_old_data(self):
        """Nettoie les anciens fichiers Parquet et checkpoint au démarrage"""
        data_path = os.getenv('FLIGHTS_DATA_PATH', '/tmp/flights_data')
        checkpoint_path = os.getenv('CHECKPOINT_PATH', '/data/checkpoint')
        
        for path in [data_path, checkpoint_path]:
            if os.path.exists(path):
                try:
                    logger.info(f"🧹 Nettoyage de {path}...")
                    shutil.rmtree(path)
                    logger.info(f"✅ {path} nettoyé avec succès")
                except Exception as e:
                    logger.warning(f"⚠️  Impossible de nettoyer {path}: {e}")
        
        # Recréer les répertoires
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(checkpoint_path, exist_ok=True)
        logger.info(f"📁 Répertoires créés: {data_path}, {checkpoint_path}")
    
    def define_schema(self):
        """Définit le schéma des données de vol"""
        return StructType([
            StructField("icao24", StringType(), True),
            StructField("callsign", StringType(), True),
            StructField("origin_country", StringType(), True),
            StructField("time_position", LongType(), True),
            StructField("last_contact", LongType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("baro_altitude", DoubleType(), True),
            StructField("on_ground", BooleanType(), True),
            StructField("velocity", DoubleType(), True),
            StructField("true_track", DoubleType(), True),
            StructField("vertical_rate", DoubleType(), True),
            StructField("geo_altitude", DoubleType(), True),
            StructField("squawk", StringType(), True),
            StructField("spi", BooleanType(), True),
            StructField("position_source", IntegerType(), True),
            StructField("timestamp", StringType(), True),
            StructField("airport", StringType(), True),
            StructField("status", StringType(), True)
        ])
    
    def read_from_kafka(self, topic='flights-data', bootstrap_servers='localhost:9092'):
        """Lit le stream depuis Kafka"""
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
    
    def process_stream(self, raw_stream):
        """Traite le stream de données"""
        schema = self.define_schema()
        
        # Parse JSON
        flights_df = raw_stream \
            .selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")
        
        # Ajoute des colonnes calculées
        processed_df = flights_df \
            .withColumn("processing_time", current_timestamp()) \
            .withColumn("altitude_ft", col("baro_altitude") * 3.28084) \
            .withColumn("speed_kmh", col("velocity") * 3.6) \
            .filter(col("callsign").isNotNull())
        
        return processed_df
    
    def compute_statistics(self, flights_df):
        """Calcule les statistiques par fenêtre temporelle"""
        # Agrégation par statut et fenêtre de 2 minutes
        stats_by_status = flights_df \
            .withWatermark("processing_time", "5 minutes") \
            .groupBy(
                window("processing_time", "2 minutes", "1 minute"),
                "status"
            ) \
            .agg(
                count("*").alias("count"),
                avg("altitude_ft").alias("avg_altitude_ft"),
                avg("speed_kmh").alias("avg_speed_kmh"),
                approx_count_distinct("callsign").alias("unique_flights")
            ) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                "status",
                "count",
                "avg_altitude_ft",
                "avg_speed_kmh",
                "unique_flights"
            )
        
        return stats_by_status
    
    def write_to_console(self, df, query_name="flights"):
        """Écrit les résultats dans la console"""
        query = df \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .queryName(query_name) \
            .start()
        
        return query
    
    def write_to_memory(self, df, table_name="flights_table"):
        """Écrit les résultats en mémoire pour Streamlit"""
        query = df \
            .writeStream \
            .outputMode("append") \
            .format("memory") \
            .queryName(table_name) \
            .start()
        
        return query
    
    def write_to_parquet(self, df, path=None):
        """Écrit les données dans des fichiers Parquet pour partage avec Streamlit"""
        # Utiliser /data/flights_data dans Docker, /tmp/flights_data en local
        if path is None:
            path = os.getenv('FLIGHTS_DATA_PATH', '/tmp/flights_data')
        
        # Utiliser /data/checkpoint dans Docker
        checkpoint_path = os.getenv('CHECKPOINT_PATH', f"/data/checkpoint/{path.split('/')[-1]}")
        
        query = df \
            .writeStream \
            .outputMode("append") \
            .format("parquet") \
            .option("path", path) \
            .option("checkpointLocation", checkpoint_path) \
            .start()
        
        return query
    
    def write_statistics_to_memory(self, stats_df):
        """Écrit les statistiques en mémoire"""
        query = stats_df \
            .writeStream \
            .outputMode("complete") \
            .format("memory") \
            .queryName("flight_statistics") \
            .start()
        
        return query
    
    def write_statistics_to_parquet(self, stats_df, path="/tmp/flight_statistics"):
        """Écrit les statistiques dans des fichiers Parquet"""
        query = stats_df \
            .writeStream \
            .outputMode("complete") \
            .format("parquet") \
            .option("path", path) \
            .option("checkpointLocation", f"/tmp/checkpoint/{path.split('/')[-1]}") \
            .start()
        
        return query
    
    def run(self):
        """Lance le traitement streaming"""
        logger.info("Démarrage du consumer Spark...")
        
        # Lecture depuis Kafka
        raw_stream = self.read_from_kafka()
        
        # Traitement
        flights_df = self.process_stream(raw_stream)
        
        # Statistiques
        stats_df = self.compute_statistics(flights_df)
        
        # Écriture des résultats
        query1 = self.write_to_console(flights_df, "raw_flights")
        query2 = self.write_to_memory(flights_df, "flights_table")
        query3 = self.write_statistics_to_memory(stats_df)
        query4 = self.write_to_parquet(flights_df)  # Utilise la variable d'environnement
        # Note: Les statistiques ne sont pas écrites en Parquet car le mode "complete" n'est pas supporté
        
        logger.info("Streaming démarré. Appuyez sur Ctrl+C pour arrêter.")
        
        # Attend la fin
        try:
            query1.awaitTermination()
        except KeyboardInterrupt:
            logger.info("Arrêt du streaming...")
            query1.stop()
            query2.stop()
            query3.stop()
            query4.stop()
            self.spark.stop()

if __name__ == "__main__":
    # Lire les variables d'environnement
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic = os.getenv('KAFKA_TOPIC', 'flights-data')
    
    processor = FlightStreamProcessor()
    
    # Lancer le traitement avec les bons paramètres
    logger.info(f"Démarrage du consumer Spark avec Kafka: {bootstrap_servers}, topic: {topic}")
    
    # Lecture depuis Kafka avec les paramètres corrects
    raw_stream = processor.read_from_kafka(topic=topic, bootstrap_servers=bootstrap_servers)
    
    # Traitement
    flights_df = processor.process_stream(raw_stream)
    
    # Statistiques
    stats_df = processor.compute_statistics(flights_df)
    
    # Écriture des résultats
    query1 = processor.write_to_console(flights_df, "raw_flights")
    query2 = processor.write_to_memory(flights_df, "flights_table")
    query3 = processor.write_statistics_to_memory(stats_df)
    query4 = processor.write_to_parquet(flights_df)
    
    logger.info("Streaming démarré. Appuyez sur Ctrl+C pour arrêter.")
    
    # Attend la fin
    try:
        query1.awaitTermination()
    except KeyboardInterrupt:
        logger.info("Arrêt du streaming...")
        query1.stop()
        query2.stop()
        query3.stop()
        query4.stop()
        processor.spark.stop()
