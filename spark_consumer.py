"""
Spark Streaming Consumer pour traiter les données de vols en temps réel
Calcule des statistiques et agrégations sur les vols
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightStreamProcessor:
    def __init__(self):
        """Initialise la session Spark avec les packages nécessaires"""
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
    
    def write_to_parquet(self, df, path="/tmp/flights_data"):
        """Écrit les données dans des fichiers Parquet pour partage avec Streamlit"""
        query = df \
            .writeStream \
            .outputMode("append") \
            .format("parquet") \
            .option("path", path) \
            .option("checkpointLocation", f"/tmp/checkpoint/{path.split('/')[-1]}") \
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
        query4 = self.write_to_parquet(flights_df, "/tmp/flights_data")
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
    processor = FlightStreamProcessor()
    processor.run()
