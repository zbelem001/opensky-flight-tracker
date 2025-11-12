# ✈️ OpenSky Flight Tracker - Installation Sans Git

> **Démarrage en 2 minutes - Aucun clone de repo nécessaire !**

## 🚀 Méthode Ultra-Rapide (Recommandée)

### Étape 1 : Créer le fichier docker-compose.yml

Créez un nouveau dossier et un fichier `docker-compose.yml` :

```bash
mkdir opensky-flight-tracker
cd opensky-flight-tracker
```

Téléchargez le fichier directement :
```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/zbelem001/opensky-flight-tracker/main/docker-compose-standalone.yml
```

**OU** copiez-collez le contenu ci-dessous dans un fichier `docker-compose.yml` :

<details>
<summary>📋 Cliquez pour voir le contenu du docker-compose.yml</summary>

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: opensky-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    networks:
      - opensky-network
    restart: unless-stopped

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: opensky-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    networks:
      - opensky-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: opensky-kafka-ui
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: opensky-cluster
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - opensky-network
    restart: unless-stopped

  producer:
    image: zbelem001/opensky-producer:latest
    container_name: opensky-producer
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      KAFKA_TOPIC: flights-data
      FETCH_INTERVAL: 30
    networks:
      - opensky-network
    restart: unless-stopped

  spark-consumer:
    image: zbelem001/opensky-spark:latest
    container_name: opensky-spark
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      KAFKA_TOPIC: flights-data
      FLIGHTS_DATA_PATH: /data/flights_data
      CHECKPOINT_PATH: /data/checkpoint
    volumes:
      - flights-data:/data/flights_data
      - spark-checkpoint:/data/checkpoint
    networks:
      - opensky-network
    restart: unless-stopped

  dashboard:
    image: zbelem001/opensky-dashboard:latest
    container_name: opensky-dashboard
    depends_on:
      - spark-consumer
    ports:
      - "8501:8501"
    environment:
      FLIGHTS_DATA_PATH: /data/flights_data
    volumes:
      - flights-data:/data/flights_data:ro
    networks:
      - opensky-network
    restart: unless-stopped

networks:
  opensky-network:
    driver: bridge

volumes:
  flights-data:
  spark-checkpoint:
```

</details>

### Étape 2 : Lancer le projet

```bash
docker-compose up -d
```

### Étape 3 : Accéder au dashboard

Attendez **2 minutes** puis ouvrez :
- 📊 **Dashboard** : http://localhost:8501
- 🔍 **Kafka UI** : http://localhost:8080

---

## ✅ C'est tout !

**Aucun Git, aucun Python, aucun code à compiler !**

Les images Docker contiennent tout le nécessaire :
- ✅ zbelem001/opensky-producer
- ✅ zbelem001/opensky-spark
- ✅ zbelem001/opensky-dashboard

---

## 🛠️ Commandes utiles

```bash
# Voir le statut
docker-compose ps

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Tout nettoyer (volumes inclus)
docker-compose down -v
```

---

## 📊 Ce que vous verrez

- **Carte interactive** avec les avions en temps réel autour de Dubai
- **Statistiques** : arrivées, départs, vols en transit
- **Graphiques** : distribution horaire, altitudes
- **Mise à jour automatique** toutes les 10 secondes

---

## 🐳 Images Docker Hub

Les 3 images sont publiques :
1. https://hub.docker.com/r/zbelem001/opensky-producer
2. https://hub.docker.com/r/zbelem001/opensky-spark
3. https://hub.docker.com/r/zbelem001/opensky-dashboard

---

## 📚 Documentation complète

Pour le code source et la documentation complète :
https://github.com/zbelem001/opensky-flight-tracker

---

**🎓 Projet de Big Data & Streaming Temps Réel**  
**Auteur** : Zia Belem  
**Technologies** : Kafka • Spark • Streamlit • Docker
