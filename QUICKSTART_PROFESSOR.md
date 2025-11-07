# 🚀 OpenSky Flight Tracker - Démarrage Rapide pour Professeur

## 👨‍🏫 Guide Ultra-Rapide (1 minute)

### Prérequis
- **Docker** installé sur votre machine
- Si pas installé : https://docs.docker.com/get-docker/

---

## ⚡ Démarrage en 3 commandes

### 1. Cloner le projet
```bash
git clone https://github.com/zbelem001/opensky-flight-tracker.git
cd opensky-flight-tracker
```

### 2. Lancer tous les services
```bash
docker-compose -f docker-compose.hub.yml up -d
```

**Note** : Cette commande télécharge automatiquement les images pré-construites depuis Docker Hub.  
Pas besoin de compiler quoi que ce soit ! ⚡

### 3. Accéder au dashboard
Ouvrez votre navigateur : **http://localhost:8501**

---

## 📊 Ce que vous allez voir

### Dashboard Streamlit (http://localhost:8501)
- **Statistiques en temps réel** des vols autour de l'aéroport de Dubai (DXB)
- **Graphiques interactifs** : distribution horaire, statut des vols
- **Mise à jour automatique** toutes les 30 secondes

### Kafka UI (http://localhost:8080)
- Interface de monitoring Kafka
- Visualisation des messages en temps réel
- Topics et consommateurs

---

## ⏱️ Temps de démarrage

- **Téléchargement des images** : 1-2 minutes (selon connexion)
- **Démarrage des services** : 30-60 secondes
- **Premières données visibles** : ~1 minute après démarrage

**Total** : Environ 2-3 minutes pour tout voir fonctionner

---

## 🔧 Commandes utiles

### Voir les logs en temps réel
```bash
docker-compose -f docker-compose.hub.yml logs -f
```

### Voir les logs d'un service spécifique
```bash
docker-compose -f docker-compose.hub.yml logs -f producer
docker-compose -f docker-compose.hub.yml logs -f spark-consumer
docker-compose -f docker-compose.hub.yml logs -f dashboard
```

### Vérifier le statut des services
```bash
docker-compose -f docker-compose.hub.yml ps
```

### Arrêter tous les services
```bash
docker-compose -f docker-compose.hub.yml down
```

### Redémarrer (après un arrêt)
```bash
docker-compose -f docker-compose.hub.yml up -d
```

---

## 🏗️ Architecture du Projet

```
┌─────────────────┐
│  OpenSky API    │  Données temps réel des vols
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Kafka Producer │  Récupère les vols toutes les 30s
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Apache Kafka   │  Message Broker
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Spark Consumer │  Traitement streaming + Parquet
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Dashboard      │  Visualisation Streamlit
│  (Port 8501)    │
└─────────────────┘
```

---

## 📦 Technologies Utilisées

- **Apache Kafka** : Message broker pour streaming temps réel
- **Apache Spark** : Traitement de données en streaming
- **Streamlit** : Dashboard interactif en Python
- **Docker** : Containerisation de tous les services
- **OpenSky Network API** : Données ADS-B temps réel des avions
- **Parquet** : Format de stockage des données

---

## 🛠️ Dépannage

### Problème : "Cannot connect to the Docker daemon"
```bash
# Sur Linux
sudo systemctl start docker

# Vérifier que Docker fonctionne
docker ps
```

### Problème : Le dashboard ne charge pas
```bash
# 1. Vérifier que tous les services sont "Up"
docker-compose -f docker-compose.hub.yml ps

# 2. Attendre 30-60 secondes supplémentaires
# 3. Rafraîchir http://localhost:8501
```

### Problème : "Port already in use"
```bash
# Vérifier quel processus utilise le port
sudo lsof -i :8501
sudo lsof -i :9092

# Arrêter le processus ou changer le port dans docker-compose.hub.yml
```

### Voir les logs détaillés
```bash
# Tous les services
docker-compose -f docker-compose.hub.yml logs

# Dernieres 50 lignes seulement
docker-compose -f docker-compose.hub.yml logs --tail=50

# Suivre en temps réel
docker-compose -f docker-compose.hub.yml logs -f
```

---

## 🌍 Données affichées

Le système track les vols dans un rayon de **100 km** autour de l'aéroport international de **Dubai (DXB)**.

**Informations collectées** :
- Indicatif d'appel (callsign)
- Altitude, vitesse, position
- Statut : départ, arrivée, en vol, stationnement
- Pays d'origine
- Et plus...

**Fréquence de mise à jour** : Toutes les 30 secondes

---

## 📝 Notes importantes

### Permissions Docker
Sur Linux, si vous avez une erreur de permission :
```bash
# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Puis se déconnecter/reconnecter
# Ou utiliser sudo devant les commandes docker
```

### Stockage des données
Les données sont persistées dans des volumes Docker :
- `opensky-flights-data` : Fichiers Parquet des vols
- `opensky-checkpoint` : Checkpoints Spark

Ces volumes persistent même après `docker-compose down`.

Pour tout supprimer (y compris les données) :
```bash
docker-compose -f docker-compose.hub.yml down -v
```

---

## 🎯 Évaluation du Projet

### Points forts à observer :

1. **Architecture distribuée** : Kafka + Spark pour du streaming temps réel
2. **Containerisation** : Tout fonctionne avec Docker
3. **Scalabilité** : Architecture facilement extensible
4. **Monitoring** : Kafka UI pour visualiser les flux
5. **Visualisation** : Dashboard interactif avec Streamlit
6. **Persistence** : Données stockées en Parquet
7. **Documentation** : README, guides, commentaires dans le code

### Ce qui est démontré :

- ✅ Intégration API REST (OpenSky Network)
- ✅ Streaming de données avec Kafka
- ✅ Traitement temps réel avec Spark
- ✅ Visualisation de données avec Streamlit
- ✅ Containerisation Docker multi-services
- ✅ Persistence de données (Parquet)
- ✅ Architecture microservices

---

## 📚 Documentation Complète

- **README.md** : Documentation principale du projet
- **DOCKER.md** : Guide détaillé Docker
- **DOCKER_HUB_GUIDE.md** : Guide publication Docker Hub
- **Code commenté** : Tous les fichiers Python sont documentés

---

## 🎓 Contact Étudiant

- **Repository GitHub** : https://github.com/zbelem001/opensky-flight-tracker
- **Images Docker** : https://hub.docker.com/u/zbelem001

---

## ⭐ Bonus : Commandes Avancées

### Voir les données en temps réel dans Kafka
```bash
# Se connecter au conteneur Kafka
docker exec -it opensky-kafka bash

# Lire les messages du topic
kafka-console-consumer --bootstrap-server localhost:9092 --topic flights-data --from-beginning
```

### Voir les fichiers Parquet créés
```bash
docker exec opensky-spark ls -lh /data/flights_data/
```

### Forcer le redémarrage d'un service
```bash
docker-compose -f docker-compose.hub.yml restart producer
```

---

**🎉 Bon test du projet ! Si vous avez des questions, consultez la documentation dans le repository GitHub.**
