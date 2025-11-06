# 🚀 Guide de Démarrage Rapide

## ⚡ Installation en 5 Minutes

### 1️⃣ Prérequis
```bash
# Vérifier Python
python3 --version  # Doit être 3.8+

# Vérifier Docker
docker --version
docker-compose --version

# Vérifier Java 17
java -version  # Doit être 17.x
```

### 2️⃣ Cloner et Installer
```bash
# Cloner le projet
git clone <votre-repo>
cd opensky-flight-tracker

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3️⃣ Démarrer Kafka
```bash
# Lancer Kafka avec Docker
docker-compose up -d

# Vérifier que Kafka est actif
docker ps
# Vous devez voir : zookeeper, kafka, kafka-ui
```

### 4️⃣ Lancer l'Application
```bash
# Option A : Script automatique (RECOMMANDÉ)
./start.sh

# Option B : Lancement manuel (3 terminaux)

# Terminal 1 - Producer
python kafka_producer.py

# Terminal 2 - Spark Consumer
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python spark_consumer.py

# Terminal 3 - Dashboard
streamlit run dashboard.py
```

### 5️⃣ Accéder au Dashboard
```
🌐 Dashboard Streamlit : http://localhost:8501
🔍 Kafka UI : http://localhost:8080
```

---

## 🐛 Dépannage Express

### ❌ Kafka ne démarre pas
```bash
docker-compose down -v
docker-compose up -d
```

### ❌ Erreur Java avec Spark
```bash
# Installer Java 17
sudo apt install openjdk-17-jdk

# Définir JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### ❌ Aucun vol détecté
Zone Ouagadougou peut avoir peu de trafic. Pour tester, modifiez dans `kafka_producer.py` :
```python
# Changer les coordonnées pour Paris (beaucoup de vols)
OUAGA_LAT = 48.8566  # Paris
OUAGA_LON = 2.3522
RADIUS = 50
```

### ❌ Dashboard vide
1. Attendre 2-3 minutes que Spark agrège les données
2. Vérifier que `spark_consumer.py` tourne
3. Vérifier les logs : `tail -f /tmp/spark.log`

---

## 📊 Architecture Simplifiée

```
OpenSky API (toutes les 30s)
      ↓
kafka_producer.py (collecte et envoie vers Kafka)
      ↓
Kafka Topic: flights-data
      ↓
spark_consumer.py (traite et agrège en temps réel)
      ↓
Tables Spark en mémoire
      ↓
dashboard.py (affiche avec Streamlit)
```

---

## 🎯 Commandes Utiles

```bash
# Voir les logs du producer
tail -f /tmp/producer.log

# Voir les logs Spark
tail -f /tmp/spark.log

# Voir les logs Streamlit
tail -f /tmp/streamlit.log

# Arrêter tous les processus
pkill -f "kafka_producer|spark_consumer|streamlit"

# Nettoyer Kafka
docker-compose down -v

# Vérifier les topics Kafka
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Lire les messages Kafka
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic flights-data \
  --from-beginning \
  --max-messages 5
```

---

## ✅ Checklist de Vérification

- [ ] Python 3.8+ installé
- [ ] Java 17 installé
- [ ] Docker et Docker Compose installés
- [ ] Environnement virtuel créé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Kafka démarré (`docker ps` montre 3 conteneurs)
- [ ] Producer lancé (logs dans `/tmp/producer.log`)
- [ ] Spark Consumer lancé (logs dans `/tmp/spark.log`)
- [ ] Dashboard accessible sur http://localhost:8501

---

## 📝 Variables à Personnaliser

### kafka_producer.py
```python
OUAGA_LAT = 12.3532  # Latitude de votre zone
OUAGA_LON = -1.5124  # Longitude de votre zone
RADIUS = 100         # Rayon en km
```

Ligne 163 :
```python
producer.run(interval=30)  # Intervalle entre requêtes API
```

### spark_consumer.py
Ligne 60 :
```python
topic='flights-data'  # Nom du topic Kafka
```

Ligne 90 :
```python
window("processing_time", "2 minutes", "1 minute")  # Fenêtre d'agrégation
```

### dashboard.py
Ligne 211 :
```python
refresh_rate = st.sidebar.slider("...", 5, 60, 10)  # Taux de rafraîchissement
```

---

## 🎓 Pour Votre Rapport

**Technologies utilisées :**
- Apache Kafka 7.5.0 (streaming)
- Apache Spark 3.5.0 (traitement)
- PySpark (API Python)
- Streamlit 1.29.0 (visualisation)
- OpenSky Network API (données)
- Docker Compose (infrastructure)

**Concepts démontrés :**
- Streaming temps réel
- Architecture microservices
- ETL (Extract, Transform, Load)
- Agrégations par fenêtres temporelles
- Visualisation interactive
- Conteneurisation

---

**🎉 Bon courage pour votre projet !**
