# 🐳 Guide : Publier vos Images Docker sur Docker Hub

## 🎯 Pourquoi publier sur Docker Hub ?

### ✅ Avantages ÉNORMES
- **Votre prof télécharge vos images en 1 commande** → Pas besoin de build
- **10x plus rapide** : `docker pull` vs `docker build` (30 sec vs 5 min)
- **Toujours accessible** : Docker Hub conserve vos images
- **Professionnel** : Montre que vous savez utiliser Docker Hub
- **Gratuit** : Stockage illimité d'images publiques

### 📊 Comparaison

| Méthode | Temps pour votre prof | Build nécessaire ? |
|---------|----------------------|-------------------|
| **Sans Docker Hub** | 5-10 min (build images) | ✅ Oui |
| **Avec Docker Hub** | 30 secondes (pull images) | ❌ Non |

---

## 🚀 Étapes pour publier sur Docker Hub

### 1️⃣ Créer un compte Docker Hub (2 minutes)

1. Allez sur https://hub.docker.com
2. Cliquez "Sign Up"
3. Créez votre compte (exemple: `zbelem001`)
4. Confirmez votre email

### 2️⃣ Login Docker depuis votre terminal (1 minute)

```bash
# Se connecter à Docker Hub
docker login

# Entrez votre username et password
Username: zbelem001
Password: ********
```

### 3️⃣ Tagger vos images (1 minute)

```bash
# Lister vos images actuelles
sudo docker images | grep opensky

# Tagger les 3 images
sudo docker tag opensky-flight-tracker_producer zbelem001/opensky-producer:latest
sudo docker tag opensky-flight-tracker_spark-consumer zbelem001/opensky-spark:latest
sudo docker tag opensky-flight-tracker_dashboard zbelem001/opensky-dashboard:latest
```

**Format** : `username/nom-image:version`

### 4️⃣ Push sur Docker Hub (2-5 minutes)

```bash
# Push les 3 images
sudo docker push zbelem001/opensky-producer:latest
sudo docker push zbelem001/opensky-spark:latest
sudo docker push zbelem001/opensky-dashboard:latest
```

**Attendez** : Ça peut prendre 2-5 minutes selon votre connexion internet.

### 5️⃣ Vérifier sur Docker Hub (30 secondes)

1. Allez sur https://hub.docker.com/u/zbelem001
2. Vous devriez voir vos 3 images publiées
3. Vérifiez que c'est en mode "Public"

---

## 📝 Modifier docker-compose.yml pour utiliser vos images

### Créez un nouveau fichier : `docker-compose.hub.yml`

```yaml
version: '3.8'

services:
  # Zookeeper - Gestionnaire de configuration Kafka
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

  # Kafka - Message Broker
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: opensky-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    networks:
      - opensky-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

  # Kafka UI - Interface web pour Kafka
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

  # Producer - Récupère les données OpenSky et les envoie à Kafka
  producer:
    image: zbelem001/opensky-producer:latest  # ← Image depuis Docker Hub
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

  # Spark Consumer - Traite les données en streaming
  spark-consumer:
    image: zbelem001/opensky-spark:latest  # ← Image depuis Docker Hub
    container_name: opensky-spark
    depends_on:
      kafka:
        condition: service_healthy
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      KAFKA_TOPIC: flights-data
    volumes:
      - flights-data:/data/flights_data
      - spark-checkpoint:/data/checkpoint
    networks:
      - opensky-network
    restart: unless-stopped

  # Dashboard Streamlit - Visualisation des données
  dashboard:
    image: zbelem001/opensky-dashboard:latest  # ← Image depuis Docker Hub
    container_name: opensky-dashboard
    depends_on:
      - spark-consumer
    ports:
      - "8501:8501"
    volumes:
      - flights-data:/data/flights_data:ro
    networks:
      - opensky-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  opensky-network:
    driver: bridge
    name: opensky-network

volumes:
  flights-data:
    name: opensky-flights-data
  spark-checkpoint:
    name: opensky-checkpoint
```

---

## 📧 Instructions pour votre professeur (ULTRA SIMPLE)

### Créez un fichier : `QUICKSTART_PROFESSOR.md`

```markdown
# 🚀 OpenSky Flight Tracker - Démarrage Rapide

## Pour le professeur 👨‍🏫

### Prérequis
- Docker installé : https://docs.docker.com/get-docker/

### Démarrage (2 commandes, 1 minute)

1. **Téléchargez le projet**
```bash
git clone https://github.com/zbelem001/opensky-flight-tracker
cd opensky-flight-tracker
```

2. **Lancez tout** (utilise les images Docker Hub)
```bash
docker-compose -f docker-compose.hub.yml up -d
```

3. **Accédez au dashboard**
→ Ouvrez http://localhost:8501 dans votre navigateur

### C'est tout ! ✅

Le système télécharge automatiquement les images depuis Docker Hub et démarre tous les services.

**Temps total** : 1-2 minutes (selon votre connexion internet)

---

## 📊 Ce que vous verrez

- **Dashboard Streamlit** : http://localhost:8501
  - Statistiques en temps réel des vols autour de Dubai
  - Graphiques interactifs
  
- **Kafka UI** : http://localhost:8080
  - Visualisation des messages Kafka

---

## 🛑 Pour arrêter

```bash
docker-compose -f docker-compose.hub.yml down
```

---

## 🔧 Dépannage

**Problème : "Cannot connect to Docker daemon"**
```bash
# Démarrer Docker
sudo systemctl start docker

# Réessayer
docker-compose -f docker-compose.hub.yml up -d
```

**Problème : Le dashboard ne charge pas**
```bash
# Attendre 30 secondes que tous les services démarrent
# Puis rafraîchir http://localhost:8501
```

**Voir les logs**
```bash
docker-compose -f docker-compose.hub.yml logs -f
```
```

---

## 🎯 Commandes complètes pour VOUS

### Script complet pour publier vos images

```bash
#!/bin/bash
# publish-docker-images.sh

echo "🔐 Login Docker Hub..."
docker login

echo "🏷️  Tagging images..."
sudo docker tag opensky-flight-tracker_producer zbelem001/opensky-producer:latest
sudo docker tag opensky-flight-tracker_spark-consumer zbelem001/opensky-spark:latest
sudo docker tag opensky-flight-tracker_dashboard zbelem001/opensky-dashboard:latest

echo "📤 Pushing images to Docker Hub..."
sudo docker push zbelem001/opensky-producer:latest
sudo docker push zbelem001/opensky-spark:latest
sudo docker push zbelem001/opensky-dashboard:latest

echo "✅ Done! Images disponibles sur Docker Hub"
echo "🔗 https://hub.docker.com/u/zbelem001"
```

### Rendre le script exécutable et l'exécuter

```bash
chmod +x publish-docker-images.sh
./publish-docker-images.sh
```

---

## 📧 Email mis à jour pour votre prof

```
Bonjour Professeur,

Je vous partage mon projet OpenSky Flight Tracker.

🚀 DÉMARRAGE ULTRA RAPIDE (1 minute)

1. git clone https://github.com/zbelem001/opensky-flight-tracker
2. cd opensky-flight-tracker
3. docker-compose -f docker-compose.hub.yml up -d
4. Ouvrez http://localhost:8501

Les images Docker sont pré-construites et hébergées sur Docker Hub,
donc pas besoin de build - tout est automatique !

📌 LIENS
- Code : https://github.com/zbelem001/opensky-flight-tracker
- Images Docker : https://hub.docker.com/u/zbelem001
- Documentation : Voir README.md

Le dashboard affiche les vols en temps réel autour de Dubai (DXB).

Cordialement,
[Votre nom]
```

---

## 📊 Avantages pour votre prof

### Avant (sans Docker Hub)
```bash
git clone ...
cd opensky-flight-tracker
docker-compose build      # ← 5-10 minutes 😴
docker-compose up -d
```

### Après (avec Docker Hub)
```bash
git clone ...
cd opensky-flight-tracker
docker-compose -f docker-compose.hub.yml up -d  # ← 30 secondes ⚡
```

**Gain de temps : 10x plus rapide !**

---

## ✅ Checklist finale

Avant de partager avec votre prof :

- [ ] Compte Docker Hub créé
- [ ] Login `docker login` effectué
- [ ] Images taguées
- [ ] Images pushées sur Docker Hub
- [ ] Vérification sur https://hub.docker.com/u/zbelem001
- [ ] `docker-compose.hub.yml` créé
- [ ] `QUICKSTART_PROFESSOR.md` créé
- [ ] README.md mis à jour avec instructions Docker Hub
- [ ] Test en local : `docker-compose -f docker-compose.hub.yml up -d`
- [ ] Push sur GitHub

---

## 🎓 Note importante

**Images publiques** : Vos images seront publiques (tout le monde peut les télécharger)
- C'est OK pour un projet éducatif
- Ajoutez un LICENSE au projet (MIT recommandé)
- Ne mettez JAMAIS de secrets/passwords dans les images

**Taille des images** :
- Producer : ~200 MB
- Spark : ~800 MB (Java + Spark)
- Dashboard : ~500 MB
- **Total** : ~1.5 GB

Docker Hub gratuit : **Illimité pour images publiques** ✅

---

## 🏆 Résultat final

Votre prof tape 2 commandes et voit votre projet en 1 minute ! 🚀

**C'est LA solution professionnelle !** 💪
