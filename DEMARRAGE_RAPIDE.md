# ✈️ OpenSky Flight Tracker - Démarrage Express

> **Projet de Big Data & Streaming Temps Réel**  
> Surveillance en temps réel des vols autour de l'aéroport de Dubai

---

## 🚀 Lancer le projet en 1 minute

### Prérequis
- Docker installé (https://docs.docker.com/get-docker/)

### 3 commandes
```bash
# 1. Cloner
git clone https://github.com/zbelem001/opensky-flight-tracker.git
cd opensky-flight-tracker

# 2. Télécharger les images et lancer
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d

# 3. Attendre 1 minute puis ouvrir
# Dashboard : http://localhost:8501
# Kafka UI : http://localhost:8080
```

**C'est tout !** ✅

---

## 📊 Ce que vous verrez

- **Carte interactive** des avions en temps réel autour de Dubai
- **30-50 vols** simultanés dans la zone
- **Statistiques** : arrivées, départs, vols en transit
- **Mise à jour automatique** toutes les 10 secondes
- **Graphiques** : distribution horaire, altitudes, vitesse

---

## 🏗️ Architecture

```
API OpenSky → Kafka Producer → Apache Kafka → Spark Streaming → Dashboard Streamlit
```

**Technologies utilisées :**
- Apache Kafka 3.8.1 (message broker)
- Apache Spark 3.5.0 (traitement streaming)
- Streamlit 1.29.0 (visualisation)
- Docker (containerisation)

**5 conteneurs Docker** qui communiquent ensemble.

---

## 🐳 Images Docker Hub

Les 3 images de l'application sont publiques :

1. **zbelem001/opensky-producer** - Collecte des données API
2. **zbelem001/opensky-spark** - Traitement Spark
3. **zbelem001/opensky-dashboard** - Interface Streamlit

Voir : https://hub.docker.com/u/zbelem001

---

## 🛠️ Commandes utiles

```bash
# Voir le statut
docker-compose -f docker-compose.hub.yml ps

# Voir les logs
docker-compose -f docker-compose.hub.yml logs -f

# Arrêter
docker-compose -f docker-compose.hub.yml down

# Redémarrer
docker-compose -f docker-compose.hub.yml up -d
```

---

## 📚 Documentation complète

- **GUIDE_PROFESSEUR_SIMPLE.md** - Guide d'évaluation détaillé
- **README.md** - Documentation technique complète
- **DOCKER.md** - Guide Docker avancé

---

## ⏱️ Temps de démarrage

- Téléchargement images : 1-2 min (première fois)
- Démarrage services : 30-60 sec
- Premières données : 1-2 min
- **TOTAL : ~3 minutes**

---

## ✅ Validation rapide

Après démarrage, vérifiez :

```bash
# Tous les services doivent être "Up"
docker-compose -f docker-compose.hub.yml ps
```

Résultat attendu : **6 conteneurs** actifs
- opensky-zookeeper
- opensky-kafka
- opensky-kafka-ui
- opensky-producer
- opensky-spark
- opensky-dashboard

---

## 🎯 Points clés du projet

✅ Architecture microservices complète  
✅ Streaming temps réel avec Kafka + Spark  
✅ Traitement de flux avec agrégations temporelles  
✅ Visualisation interactive (Streamlit + Plotly)  
✅ Containerisation Docker multi-services  
✅ Images publiées sur Docker Hub  
✅ Données persistées en Parquet  

---

## 🌍 Données

**Source** : API OpenSky Network (données ADS-B publiques)  
**Zone** : 100 km autour de Dubai International Airport (DXB)  
**Fréquence** : Mise à jour toutes les 30 secondes  
**Volume** : 30-50 avions simultanés en moyenne  

---

**📧 Contact** : https://github.com/zbelem001/opensky-flight-tracker  
**🎓 Étudiant** : Zia Belem - Novembre 2025
