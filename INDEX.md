# 📑 Index des Fichiers - OpenSky Flight Tracker

## 🎯 Fichiers Principaux (Code Source)

| Fichier | Lignes | Description |
|---------|--------|-------------|
| **kafka_producer.py** | 163 | 🟢 Producer Kafka - Collecte données depuis OpenSky API |
| **spark_consumer.py** | 173 | 🔵 Consumer Spark - Traite le stream avec PySpark |
| **dashboard.py** | 278 | 🟣 Dashboard Streamlit - Visualisation temps réel |

**Total Code Python : 614 lignes**

---

## 📦 Configuration & Infrastructure

| Fichier | Lignes | Description |
|---------|--------|-------------|
| **requirements.txt** | 16 | Dépendances Python (kafka-python-ng, pyspark, streamlit...) |
| **docker-compose.yml** | 54 | Configuration Kafka + Zookeeper + Kafka-UI |
| **.gitignore** | 35 | Fichiers à ignorer par Git |

---

## 🚀 Scripts Utilitaires

| Fichier | Description |
|---------|-------------|
| **start.sh** | 🎬 Lance automatiquement les 3 composants (Producer, Spark, Dashboard) |
| **check.sh** | ✅ Vérifie que tous les prérequis sont installés |
| **MIGRATION.sh** | 🔄 Nettoie l'ancienne structure (optionnel) |

---

## 📚 Documentation

| Fichier | Contenu |
|---------|---------|
| **README.md** | 📖 Documentation principale (197 lignes) - À LIRE EN PREMIER |
| **QUICKSTART.md** | ⚡ Guide de démarrage rapide (5 minutes) |
| **COMPARAISON.md** | 📊 Analyse avant/après simplification |
| **RESUME.txt** | 📝 Résumé avec commandes essentielles |
| **INDEX.md** | 📑 Ce fichier - Navigation |

---

## 🗂️ Ordre de Lecture Recommandé

### Pour Découvrir le Projet
1. **RESUME.txt** → Vue d'ensemble rapide
2. **README.md** → Documentation complète
3. **QUICKSTART.md** → Guide de démarrage

### Pour Développer
1. **kafka_producer.py** → Comprendre la collecte
2. **spark_consumer.py** → Comprendre le traitement
3. **dashboard.py** → Comprendre la visualisation

### Pour Déployer
1. **check.sh** → Vérifier prérequis
2. **docker-compose.yml** → Démarrer Kafka
3. **start.sh** → Lancer l'application

---

## 🔍 Détails des Fichiers

### 🟢 kafka_producer.py (163 lignes)
**Responsabilité :** Collecter les données de vols depuis l'API OpenSky Network

**Classes principales :**
- `OpenSkyProducer` : Gère la connexion Kafka et l'envoi de messages

**Méthodes clés :**
- `fetch_flights()` : Requête API OpenSky
- `parse_flight_data()` : Parse les données brutes
- `calculate_distance()` : Calcul distance depuis aéroport
- `classify_flight_status()` : Détermine statut (arrivée/départ/stationnement)
- `send_to_kafka()` : Envoie vers topic Kafka
- `run()` : Boucle principale (30s par défaut)

**Configuration :**
- Zone : Ouagadougou (12.3532°N, -1.5124°W)
- Rayon : 100 km
- Topic Kafka : `flights-data`
- Intervalle : 30 secondes

---

### 🔵 spark_consumer.py (173 lignes)
**Responsabilité :** Traiter le stream Kafka avec PySpark en temps réel

**Classes principales :**
- `FlightStreamProcessor` : Gère le streaming Spark

**Méthodes clés :**
- `define_schema()` : Schéma des données de vol
- `read_from_kafka()` : Lit depuis topic Kafka
- `process_stream()` : Parse JSON et calcule colonnes
- `compute_statistics()` : Agrégations par fenêtre temporelle
- `write_to_memory()` : Écrit dans tables Spark (pour Streamlit)
- `run()` : Lance le streaming

**Configuration :**
- Package Kafka : spark-sql-kafka-0-10_2.12:3.5.0
- Checkpoint : /tmp/checkpoint
- Fenêtre : 2 minutes (slide 1 minute)
- Tables : `flights_table`, `flight_statistics`

---

### 🟣 dashboard.py (278 lignes)
**Responsabilité :** Visualiser les données en temps réel avec Streamlit

**Classes principales :**
- `FlightDashboard` : Gère les visualisations

**Méthodes clés :**
- `get_flights_data()` : Lit table Spark `flights_table`
- `get_statistics()` : Lit table Spark `flight_statistics`
- `create_map()` : Carte interactive Plotly Mapbox
- `create_status_chart()` : Graphique en barres (statuts)
- `create_altitude_chart()` : Histogramme altitudes
- `create_timeline()` : Timeline statistiques

**Configuration :**
- Rafraîchissement : 5-60 secondes (slider)
- Layout : wide
- Thème : bleu (#1f77b4)

---

## 🎯 Points d'Entrée

### Lancement Automatique
```bash
./start.sh
```
Lance dans l'ordre :
1. Producer Kafka (PID stocké)
2. Spark Consumer (PID stocké)  
3. Dashboard Streamlit (PID stocké)

### Lancement Manuel (3 terminaux)
```bash
# Terminal 1
python kafka_producer.py

# Terminal 2
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python spark_consumer.py

# Terminal 3
streamlit run dashboard.py
```

---

## 📂 Structure Complète

```
opensky-flight-tracker/
│
├── 🎯 CODE SOURCE (614 lignes Python)
│   ├── kafka_producer.py       (163 lignes)
│   ├── spark_consumer.py       (173 lignes)
│   └── dashboard.py            (278 lignes)
│
├── 📦 CONFIGURATION
│   ├── requirements.txt        (16 lignes)
│   ├── docker-compose.yml      (54 lignes)
│   └── .gitignore              (35 lignes)
│
├── 🚀 SCRIPTS
│   ├── start.sh               (démarrage auto)
│   ├── check.sh               (vérification)
│   └── MIGRATION.sh           (nettoyage)
│
├── 📚 DOCUMENTATION
│   ├── README.md              (documentation principale)
│   ├── QUICKSTART.md          (guide rapide)
│   ├── COMPARAISON.md         (analyse)
│   ├── RESUME.txt             (résumé)
│   └── INDEX.md               (ce fichier)
│
└── 🔧 ENVIRONNEMENT
    └── venv/                  (environnement virtuel Python)
```

---

## 🔗 Flux de Données

```
1. OpenSky API
   ↓ (requête HTTP toutes les 30s)
   
2. kafka_producer.py
   ↓ (envoie JSON vers topic)
   
3. Kafka Topic: flights-data
   ↓ (streaming)
   
4. spark_consumer.py
   ↓ (traite et agrège)
   
5. Tables Spark en mémoire
   - flights_table
   - flight_statistics
   ↓ (requête SQL)
   
6. dashboard.py
   ↓ (affiche)
   
7. Navigateur Web
   http://localhost:8501
```

---

## 🎓 Pour Votre Évaluation

**Fichiers à présenter :**
1. README.md (vue d'ensemble)
2. kafka_producer.py (code source)
3. spark_consumer.py (code source)
4. dashboard.py (code source)
5. Capture d'écran du dashboard

**Points à mentionner :**
- ✅ Architecture microservices
- ✅ Streaming temps réel
- ✅ Technologies Big Data (Kafka, Spark)
- ✅ Visualisation interactive
- ✅ Code clean et documenté

---

**Créé le :** 6 Novembre 2025  
**Version :** 1.0 - Structure simplifiée  
**Auteur :** Votre Nom
