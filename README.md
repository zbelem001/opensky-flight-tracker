# OpenSky Flight Tracker ✈️

Tableau de bord temps réel des vols autour de l'aéroport international de **Dubai (DXB)** utilisant Apache Kafka, Apache Spark et Streamlit.

> **Note** : Le projet ciblait initialement Ouagadougou (DFFD), mais a été reconfiguré pour Dubai en raison du faible trafic aérien à Ouagadougou (peu de vols détectés dans l'API OpenSky Network).

## 🏗️ Architecture

```
OpenSky API → Kafka Producer → Kafka Topic → Spark Streaming → Fichiers Parquet → Streamlit Dashboard
                    ↓               ↓                ↓
              (30s interval)  (flights-data)   (Agrégations)
```

**Flux de données :**
1. **kafka_producer.py** : Collecte les vols dans un rayon de 100km autour de Dubai depuis l'API OpenSky
2. **Kafka Topic** : `flights-data` stocke les messages JSON
3. **spark_consumer.py** : Traite le stream en temps réel et écrit dans `/tmp/flights_data/`
4. **dashboard.py** : Lit les fichiers Parquet et affiche les visualisations

## 📋 Prérequis

- **Python 3.12+**
- **Docker & Docker Compose** (pour Kafka)
- **Java 17** (pour Spark)
- Connexion internet (API OpenSky Network)

## 🚀 Installation & Démarrage

### 1. Préparer l'environnement

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

### 2. Démarrer Kafka

```bash
# Lancer Kafka et Zookeeper avec Docker
docker-compose up -d

# Vérifier que les conteneurs tournent
docker ps
```

### 3. Lancer l'application (méthode automatique)

```bash
# Tout en un seul script !
bash start.sh
```

Le script `start.sh` lance automatiquement :
- ✅ Le Kafka Producer
- ✅ Le Spark Consumer  
- ✅ Le Dashboard Streamlit

**Accès :**
- 📊 Dashboard : http://localhost:8501
- 🔍 Kafka UI : http://localhost:8080

**Arrêter :** Appuyez sur `Ctrl+C`

### Alternative : Lancement manuel (3 terminaux)

**Terminal 1 - Kafka Producer :**
```bash
source venv/bin/activate
./venv/bin/python kafka_producer.py
```

**Terminal 2 - Spark Consumer :**
```bash
source venv/bin/activate
bash run_spark.sh
```

**Terminal 3 - Dashboard Streamlit :**
```bash
source venv/bin/activate
./venv/bin/python -m streamlit run dashboard.py
```

## 📊 Fonctionnalités

### Kafka Producer
- ✅ Collecte des vols dans un rayon de 100km autour de Dubai (DXB)
- ✅ Calcul de distance depuis l'aéroport
- ✅ Classification automatique : **arrivée**, **départ**, **stationnement**, **en_vol**
- ✅ Envoi vers le topic Kafka `flights-data` (intervalle 30s)
- ✅ Gestion des erreurs et retry automatique

### Spark Consumer
- ✅ Stream processing en temps réel avec PySpark 3.5.0
- ✅ Conversion des unités (mètres → pieds, m/s → km/h)
- ✅ Agrégations par fenêtre temporelle (2 minutes glissantes)
- ✅ Écriture dans des fichiers Parquet pour partage avec Streamlit
- ✅ Statistiques par statut de vol
- ✅ Dédoublonnage par ICAO24

### Dashboard Streamlit
- ✅ **Carte interactive** des vols (Plotly Mapbox avec OpenStreetMap)
- ✅ **Métriques en temps réel** : arrivées, départs, stationnement, total
- ✅ **Graphiques** : distribution par statut, altitudes
- ✅ **Timeline** : évolution du nombre de vols
- ✅ **Tableau détaillé** : derniers vols avec callsign, pays, statut, altitude, vitesse
- ✅ **Auto-refresh** : toutes les 10 secondes (configurable)

## 🛠️ Configuration

### Changer l'aéroport surveillé

Modifier dans `kafka_producer.py` :
```python
# Coordonnées de l'aéroport (exemple : Paris CDG)
DUBAI_LAT = 49.0097
DUBAI_LON = 2.5479
RADIUS = 100  # km
```

### Ajuster l'intervalle de polling

Dans `kafka_producer.py`, ligne 162 :
```python
producer.run(interval=30)  # 30 secondes (recommandé pour éviter rate limit)
```

### Modifier le topic Kafka

Dans tous les fichiers :
```python
topic='flights-data'  # Nom du topic
```

## 📦 Structure du Projet

```
opensky-flight-tracker/
├── kafka_producer.py       # 165 lignes - Collecte API OpenSky → Kafka
├── spark_consumer.py       # 215 lignes - Traitement Spark → Parquet
├── dashboard.py            # 280 lignes - Dashboard Streamlit
├── run_spark.sh            # Script helper pour Spark avec Java 17
├── start.sh                # Lancement automatique des 3 composants
├── requirements.txt        # Dépendances Python
├── docker-compose.yml      # Kafka + Zookeeper
├── check.sh                # Vérification de l'environnement
└── README.md              # Documentation complète
```

## 🐛 Problèmes Rencontrés & Solutions

### 1. ❌ Trafic aérien insuffisant à Ouagadougou

**Problème :** L'API OpenSky Network retournait très peu de vols (0-2) autour de Ouagadougou (DFFD).

**Solution :** Changement pour l'aéroport de **Dubai International (DXB)**, un des plus fréquentés au monde (30-50 vols simultanés dans la zone).

### 2. ❌ `ModuleNotFoundError: No module named 'kafka'`

**Problème :** Les scripts n'utilisaient pas le Python du venv.

**Solution :**
```bash
# Installation correcte
pip install kafka-python-ng==2.2.2

# Modification des scripts start.sh et run_spark.sh
./venv/bin/python kafka_producer.py  # au lieu de python
```

### 3. ❌ Erreur Spark avec Java 17

**Problème :** Incompatibilité entre PySpark 3.5.0 et Spark 4.0.1 système (`/opt/spark`).

**Solution :**
```bash
# Dans run_spark.sh
unset SPARK_HOME  # Désactive le Spark système
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Ajout d'options JVM dans spark_consumer.py
.config("spark.driver.extraJavaOptions", 
        "--add-opens=java.base/java.lang=ALL-UNNAMED ...")
```

### 4. ❌ `Distinct aggregations are not supported on streaming DataFrames`

**Problème :** `countDistinct()` n'est pas supporté en mode streaming.

**Solution :**
```python
# Avant
countDistinct("callsign").alias("unique_flights")

# Après
approx_count_distinct("callsign").alias("unique_flights")
```

### 5. ❌ Streamlit n'affiche rien

**Problème :** Streamlit ne peut pas accéder aux tables Spark en mémoire (processus séparés).

**Solution :**
- Spark écrit dans des **fichiers Parquet** : `/tmp/flights_data/*.parquet`
- Streamlit lit ces fichiers au lieu de se connecter à Spark
- Les statistiques sont calculées directement dans le dashboard

### 6. ❌ `This query does not support recovering from checkpoint`

**Problème :** Checkpoints corrompus dans `/tmp/checkpoint/`.

**Solution :**
```bash
# Nettoyage automatique dans start.sh
rm -rf /tmp/checkpoint/* /tmp/flights_data

# Suppression de la config globale dans spark_consumer.py
# .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint")  # ❌
```

### 7. ❌ `Data source parquet does not support Complete output mode`

**Problème :** Les statistiques agrégées (mode "complete") ne peuvent pas être écrites en Parquet.

**Solution :**
- Vols : écriture en **Parquet** (mode "append")
- Statistiques : calcul direct dans **Streamlit** à partir des vols

## 🔍 Dépannage

### Kafka ne démarre pas

```bash
# Redémarrer proprement
docker-compose down -v
docker-compose up -d

# Vérifier les logs
docker-compose logs kafka
```

### Erreur Java avec Spark

```bash
# Installer Java 17
sudo apt install openjdk-17-jdk

# Vérifier la version
java -version  # doit afficher 17.x

# Définir JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Aucun fichier Parquet créé

```bash
# Vérifier que Spark tourne
ps aux | grep spark_consumer

# Voir les logs
tail -f /tmp/spark.log

# Vérifier les données Kafka
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic flights-data --from-beginning
```

### Dashboard vide ou erreur

```bash
# Vérifier que les fichiers existent
ls -lh /tmp/flights_data/*.parquet

# Vérifier les logs Streamlit
tail -f /tmp/streamlit.log

# Relancer proprement
bash start.sh
```

### Trop de vols / Performances

```python
# Dans dashboard.py, limiter la lecture
latest_files = sorted(parquet_files, key=os.path.getmtime, reverse=True)[:10]

# Réduire la fenêtre temporelle
five_min_ago = pd.Timestamp.now() - pd.Timedelta(minutes=3)  # au lieu de 5
```

## 📈 Données OpenSky Network

### Limites de l'API

| Compte | Requêtes/jour | Recommandation |
|--------|---------------|----------------|
| Anonyme | 400 | Intervalle ≥ 30s |
| Gratuit | 4000 | Intervalle ≥ 10s |
| Premium | Illimité | Pas de limite |

**Inscription gratuite :** https://opensky-network.org/

### Structure des données

```json
{
  "icao24": "89643f",           // ID unique de l'avion
  "callsign": "UAE414",         // Indicatif du vol
  "origin_country": "United Arab Emirates",
  "latitude": 25.2532,          // Position GPS
  "longitude": 55.3657,
  "baro_altitude": 1234.5,      // Altitude en mètres
  "velocity": 123.45,           // Vitesse en m/s
  "vertical_rate": -2.5,        // Montée/descente (m/s)
  "on_ground": false,           // Au sol ?
  "status": "départ"            // Calculé par notre logique
}
```

## 🎓 Contexte Académique

**Projet réalisé dans le cadre d'un cours de Big Data et Streaming en Temps Réel**

### Concepts mis en pratique

- ✅ **Streaming temps réel** : Apache Kafka + Spark Structured Streaming
- ✅ **Message broker** : Publication/Souscription avec Kafka
- ✅ **Traitement distribué** : PySpark avec agrégations fenêtrées
- ✅ **APIs REST** : Consommation de l'API OpenSky Network
- ✅ **Visualisation** : Dashboard interactif avec Streamlit et Plotly
- ✅ **Conteneurisation** : Docker pour Kafka
- ✅ **Format columnar** : Parquet pour le partage de données

### Technologies utilisées

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Message Broker | Apache Kafka | 3.8.1 |
| Stream Processing | Apache Spark | 3.5.0 (PySpark) |
| Python | Python | 3.12 |
| Dashboard | Streamlit | 1.29.0 |
| Visualisation | Plotly | 5.18.0 |
| Client Kafka | kafka-python-ng | 2.2.2 |
| Conteneurisation | Docker | Latest |

## 📝 Améliorations Possibles

- [ ] Ajouter des **alertes** (vol en approche, turbulences)
- [ ] **Prédictions ML** : heure d'arrivée estimée, retards
- [ ] **Historique** : stockage PostgreSQL/MongoDB
- [ ] **Multi-aéroports** : sélection dynamique dans Streamlit
- [ ] **Authentification** OpenSky : augmenter les limites API
- [ ] **CI/CD** : déploiement automatisé avec GitHub Actions
- [ ] **Kubernetes** : orchestration pour production
- [ ] **Tests unitaires** : pytest pour la logique métier

## 📝 Licence

MIT License - Libre d'utilisation pour projets académiques et personnels.

## 🤝 Contribution

Pull requests bienvenues ! Pour des changements majeurs, ouvrez d'abord une issue.

---

**Auteur** : Zia  
**Date** : 6 Novembre 2025  
**Projet** : OpenSky Flight Tracker - Real-time Aviation Monitoring  

**Technologies** : Kafka • Spark • Python • Streamlit • Docker • Parquet

## 🚀 Installation Rapide

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd opensky-flight-tracker
```

### 2. Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Démarrer Kafka avec Docker
```bash
docker-compose up -d
```

Vérifier que Kafka est actif :
```bash
docker ps
```

## 🎯 Utilisation

### Lancer les 3 composants (dans 3 terminaux différents)

**Terminal 1 - Kafka Producer :**
```bash
source venv/bin/activate
python kafka_producer.py
```

**Terminal 2 - Spark Consumer :**
```bash
source venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python spark_consumer.py
```

**Terminal 3 - Dashboard Streamlit :**
```bash
source venv/bin/activate
streamlit run dashboard.py
```

Le dashboard sera accessible sur : **http://localhost:8501**

## 📊 Fonctionnalités

### Kafka Producer
- ✅ Collecte des vols dans un rayon de 100km autour de Ouagadougou
- ✅ Calcul de distance depuis l'aéroport
- ✅ Classification des vols (arrivée, départ, stationnement, en vol)
- ✅ Envoi vers le topic Kafka `flights-data`

### Spark Consumer
- ✅ Stream processing en temps réel
- ✅ Conversion des unités (mètres → pieds, m/s → km/h)
- ✅ Agrégations par fenêtre temporelle (2 minutes)
- ✅ Statistiques par statut de vol

### Dashboard Streamlit
- ✅ Carte interactive des vols (Plotly Mapbox)
- ✅ Métriques en temps réel (arrivées, départs, stationnement)
- ✅ Graphiques de distribution (statuts, altitudes)
- ✅ Timeline des statistiques
- ✅ Tableau détaillé des vols

## 🛠️ Configuration

### Zone de surveillance
Modifiez les constantes dans `kafka_producer.py` :
```python
OUAGA_LAT = 12.3532  # Latitude Ouagadougou
OUAGA_LON = -1.5124  # Longitude Ouagadougou
RADIUS = 100         # Rayon en km
```

### Intervalle de polling
Dans `kafka_producer.py`, ligne finale :
```python
producer.run(interval=30)  # 30 secondes
```

### Kafka Topic
Dans tous les fichiers, changez :
```python
topic='flights-data'  # Nom du topic
```

## 📦 Structure du Projet

```
opensky-flight-tracker/
├── kafka_producer.py       # 180 lignes - Producer Kafka
├── spark_consumer.py       # 150 lignes - Consumer Spark
├── dashboard.py            # 250 lignes - Dashboard Streamlit
├── requirements.txt        # Dépendances Python
├── docker-compose.yml      # Configuration Kafka
└── README.md              # Ce fichier
```

## 🔍 Dépannage

### Kafka ne démarre pas
```bash
docker-compose down -v
docker-compose up -d
```

### Erreur Java avec Spark
Installer Java 17 :
```bash
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Aucun vol détecté
- Zone Ouagadougou peut avoir peu de trafic
- Tester avec une zone plus fréquentée (Paris, Londres)
- Vérifier les limites de l'API OpenSky (400 req/jour sans compte)

### Dashboard Streamlit vide
1. Vérifier que `spark_consumer.py` est lancé
2. Attendre 2-3 minutes que Spark agrège des données
3. Vérifier les logs dans la console Spark

## 📈 Données OpenSky Network

**Limites API :**
- Sans compte : 400 requêtes/jour
- Compte gratuit : 4000 requêtes/jour
- Délai recommandé : 30+ secondes entre requêtes

**Champs principaux :**
- `callsign` : Indicatif du vol
- `origin_country` : Pays d'origine
- `latitude/longitude` : Position GPS
- `baro_altitude` : Altitude barométrique (mètres)
- `velocity` : Vitesse (m/s)
- `vertical_rate` : Taux de montée/descente
- `on_ground` : Au sol (True/False)

## 🎓 Projet Académique

Ce projet est réalisé dans le cadre d'un cours de **Big Data et Streaming en Temps Réel**.

**Technologies étudiées :**
- Apache Kafka (message broker)
- Apache Spark Structured Streaming
- PySpark (Python API pour Spark)
- Streamlit (dashboards interactifs)
- API REST (OpenSky Network)
- Docker (conteneurisation)

## 📝 Licence

MIT License - Libre d'utilisation pour projets académiques et personnels.

## 🤝 Contribution

Pull requests bienvenues ! Pour des changements majeurs, ouvrez d'abord une issue.

---

**Auteur** : Votre Nom  
**Date** : Novembre 2025  
**Contact** : votre.email@example.com
