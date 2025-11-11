# 🚀 OpenSky Flight Tracker - Guide Professeur

## 👨‍🏫 Démarrage en 30 secondes

### Prérequis
✅ **Docker** doit être installé sur votre machine  
📥 Si pas installé : https://docs.docker.com/get-docker/

---

## ⚡ 3 Étapes - C'est tout !

### 1️⃣ Cloner le projet
```bash
git clone https://github.com/zbelem001/opensky-flight-tracker.git
cd opensky-flight-tracker
```

### 2️⃣ Lancer le projet
```bash
# D'abord, télécharger les dernières images (recommandé)
docker-compose -f docker-compose.hub.yml pull

# Puis lancer tous les services
docker-compose -f docker-compose.hub.yml up -d
```

> 💡 **Ces commandes téléchargent automatiquement les 3 images Docker depuis Docker Hub**  
> Pas besoin de compiler, installer Python, ou quoi que ce soit d'autre !

> ⚠️ **Important** : Le `pull` garantit d'avoir les dernières versions avec le nettoyage automatique intégré

### 3️⃣ Ouvrir le dashboard
Attendez **1 minute** puis ouvrez votre navigateur :

🌐 **Dashboard principal** : http://localhost:8501  
🔍 **Interface Kafka** : http://localhost:8080

---

## 📊 Ce que vous verrez

### Dashboard (http://localhost:8501)
- **Carte interactive** des avions autour de Dubai en temps réel
- **Statistiques de la journée** : nombre total de vols, arrivées, départs
- **Graphiques** : distribution horaire, altitude, vitesse
- **Tableau** des derniers vols détectés

### Les données se mettent à jour automatiquement toutes les 10 secondes !

---

## ⏱️ Temps de chargement

| Étape | Durée |
|-------|-------|
| Téléchargement des images Docker | 1-2 min |
| Démarrage des services | 30-60 sec |
| Premières données visibles | 1-2 min |
| **TOTAL** | **3-4 minutes max** |

---

## 🏗️ Architecture du Projet

```
OpenSky API  →  Kafka Producer  →  Apache Kafka  →  Spark Consumer  →  Dashboard Streamlit
(Données ADS-B)   (Python)         (Message Queue)    (Traitement)      (Visualisation)
```

**5 conteneurs Docker** :
1. 🔧 **Zookeeper** - Coordination Kafka
2. 📬 **Kafka** - Message broker
3. 🎛️ **Kafka-UI** - Interface de monitoring
4. ✈️ **Producer** - Collecte des vols depuis l'API OpenSky (toutes les 30s)
5. ⚡ **Spark Consumer** - Traitement streaming et stockage Parquet
6. 📊 **Dashboard** - Visualisation Streamlit

---

## 🛠️ Commandes Utiles

### Voir si tout fonctionne
```bash
docker-compose -f docker-compose.hub.yml ps
```

Vous devriez voir 6 services avec le statut **"Up"**.

### Voir les logs en temps réel
```bash
# Tous les services
docker-compose -f docker-compose.hub.yml logs -f

# Un service spécifique
docker-compose -f docker-compose.hub.yml logs -f producer
docker-compose -f docker-compose.hub.yml logs -f spark-consumer
docker-compose -f docker-compose.hub.yml logs -f dashboard
```

### Arrêter le projet
```bash
docker-compose -f docker-compose.hub.yml down
```

### Redémarrer
```bash
docker-compose -f docker-compose.hub.yml up -d
```

### Tout supprimer (y compris les données)
```bash
docker-compose -f docker-compose.hub.yml down -v
```

---

## 🎯 Ce qui est démontré dans ce projet

### Technologies de Big Data
- ✅ **Apache Kafka** : Streaming de données en temps réel
- ✅ **Apache Spark** : Traitement distribué (PySpark 3.5.0)
- ✅ **Parquet** : Format columnar pour le stockage
- ✅ **Docker** : Containerisation complète

### Compétences techniques
- ✅ Consommation d'API REST (OpenSky Network)
- ✅ Architecture microservices
- ✅ Traitement de flux en temps réel
- ✅ Agrégations par fenêtre temporelle
- ✅ Visualisation interactive (Streamlit + Plotly)
- ✅ Persistence de données
- ✅ Publication Docker Hub

---

## 🐳 Images Docker Hub

Les 3 images utilisées sont publiques et disponibles sur Docker Hub :

1. 📦 **zbelem001/opensky-producer:latest**  
   https://hub.docker.com/r/zbelem001/opensky-producer

2. 📦 **zbelem001/opensky-spark:latest**  
   https://hub.docker.com/r/zbelem001/opensky-spark

3. 📦 **zbelem001/opensky-dashboard:latest**  
   https://hub.docker.com/r/zbelem001/opensky-dashboard

Vous pouvez les télécharger manuellement avec :
```bash
docker pull zbelem001/opensky-producer:latest
docker pull zbelem001/opensky-spark:latest
docker pull zbelem001/opensky-dashboard:latest
```

---

## 🌍 Données collectées

**Zone surveillée** : Aéroport international de **Dubai (DXB)**  
**Rayon** : 100 km autour de l'aéroport  
**Fréquence** : Toutes les 30 secondes  

**Pourquoi Dubai ?**  
Dubai est l'un des aéroports les plus fréquentés au monde. On détecte généralement **30-50 vols simultanés** dans la zone, ce qui génère suffisamment de données pour démontrer le streaming en temps réel.

> 📝 Note : Le projet ciblait initialement Ouagadougou (Burkina Faso), mais le faible trafic aérien (0-2 vols) rendait la démonstration moins convaincante.

---

## 🔧 Dépannage

### ❌ "Cannot connect to the Docker daemon"
```bash
# Démarrer Docker
sudo systemctl start docker

# Ou sur Windows/Mac : ouvrir Docker Desktop
```

### ❌ Le dashboard ne s'affiche pas
1. Vérifiez que tous les services sont démarrés :
   ```bash
   docker-compose -f docker-compose.hub.yml ps
   ```
2. Attendez 1-2 minutes supplémentaires (temps que Spark collecte des données)
3. Rafraîchissez la page http://localhost:8501

### ❌ "Port 8501 is already allocated"
Un autre service utilise le port. Deux options :
```bash
# Option 1 : Arrêter le service qui utilise le port
sudo lsof -i :8501
sudo kill -9 <PID>

# Option 2 : Changer le port dans docker-compose.hub.yml
# Remplacer "8501:8501" par "8502:8501" par exemple
```

### 🔍 Voir les messages Kafka en temps réel
```bash
docker exec -it opensky-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic flights-data \
  --from-beginning
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez dans le repository :

- **README.md** - Documentation principale et complète
- **DOCKER.md** - Guide détaillé Docker
- **QUICKSTART.md** - Guide démarrage classique (sans Docker Hub)
- **Code source** - Tous les fichiers Python sont documentés

---

## 🎓 Points d'évaluation

### Architecture (30%)
- Architecture microservices avec 5 composants
- Communication asynchrone via Kafka
- Traitement streaming avec Spark
- Persistence avec Parquet

### Technologies (30%)
- Apache Kafka (message broker)
- Apache Spark Structured Streaming
- Docker multi-conteneurs
- API REST (OpenSky Network)

### Qualité du code (20%)
- Code commenté et documenté
- Gestion d'erreurs
- Configuration via variables d'environnement
- Logs structurés

### Fonctionnalités (20%)
- Collecte temps réel des vols
- Classification automatique (arrivée/départ/en vol)
- Agrégations temporelles
- Visualisation interactive
- Auto-refresh

---

## ✅ Checklist de validation

- [ ] Le projet démarre avec une seule commande
- [ ] Le dashboard affiche des données dans les 2 minutes
- [ ] Les statistiques se mettent à jour automatiquement
- [ ] La carte montre les avions en temps réel
- [ ] Les logs Kafka montrent des messages entrants
- [ ] L'interface Kafka UI est accessible
- [ ] Pas d'erreurs dans les logs

---

## 📧 Contact

**Repository GitHub** : https://github.com/zbelem001/opensky-flight-tracker  
**Étudiant** : Zia Belem  
**Date** : Novembre 2025

---

## 🎉 Merci d'évaluer ce projet !

**Temps estimé d'évaluation** : 10-15 minutes
1. Démarrage (3 min)
2. Exploration du dashboard (5 min)
3. Vérification des logs et Kafka UI (3 min)
4. Review du code source (si souhaité)
