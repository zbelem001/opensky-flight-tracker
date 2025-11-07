# 📧 Email pour votre Professeur

---

**Objet** : Projet OpenSky Flight Tracker - Système de tracking de vols temps réel

---

Bonjour Professeur,

Je vous présente mon projet **OpenSky Flight Tracker**, un système de tracking et d'analyse de vols en temps réel.

## 🚀 Accès rapide (1 minute)

Le projet est conteneurisé avec Docker et les images sont pré-construites sur Docker Hub.

**Démarrage ultra-rapide** :

```bash
git clone https://github.com/zbelem001/opensky-flight-tracker.git
cd opensky-flight-tracker
docker-compose -f docker-compose.hub.yml up -d
```

Puis ouvrez **http://localhost:8501** pour accéder au dashboard.

## 📌 Liens importants

- **Code source** : https://github.com/zbelem001/opensky-flight-tracker
- **Images Docker** : https://hub.docker.com/u/zbelem001
- **Guide rapide** : [QUICKSTART_PROFESSOR.md](https://github.com/zbelem001/opensky-flight-tracker/blob/main/QUICKSTART_PROFESSOR.md)

## 🎯 Fonctionnalités

Le système track et analyse les vols dans un rayon de 100 km autour de l'aéroport international de **Dubai (DXB)** :

✅ **Tracking en temps réel** avec mise à jour toutes les 30 secondes  
✅ **Statistiques quotidiennes** : nombre de départs, arrivées, vols en transit  
✅ **Graphiques interactifs** : distribution horaire, statuts des vols  
✅ **Architecture scalable** : streaming de données avec Kafka et Spark  
✅ **Persistence** : stockage des données en format Parquet  

## 🛠️ Stack technique

**Architecture distribuée** :
- **Apache Kafka** : Message broker pour le streaming temps réel
- **Apache Spark** : Traitement de données en streaming
- **Streamlit** : Dashboard interactif et visualisations
- **Docker** : Containerisation complète de tous les services
- **OpenSky Network API** : Données ADS-B temps réel des avions
- **Parquet** : Format de stockage optimisé pour les données

**Services déployés** :
- Producer Kafka (récupération API)
- Spark Consumer (traitement streaming)
- Dashboard Streamlit (visualisation)
- Kafka UI (monitoring)
- Zookeeper + Kafka (infrastructure)

## 📊 Ce que vous verrez

Le dashboard affiche :
- **Vue temps réel** : Liste des vols actuels avec toutes leurs informations (altitude, vitesse, position, statut)
- **Statistiques du jour** : Nombre total de vols, départs, arrivées, vols en transit
- **Graphique de distribution horaire** : Répartition des vols par heure de la journée
- **Filtres interactifs** : Pour explorer les données

## 📝 Documentation

Le projet inclut une documentation complète :
- `README.md` : Documentation principale et guide d'installation
- `QUICKSTART_PROFESSOR.md` : Guide rapide pour tester le projet
- `DOCKER.md` : Documentation Docker approfondie
- `DOCKER_HUB_GUIDE.md` : Guide de publication sur Docker Hub
- Code commenté et structuré

## 🔧 Commandes utiles

**Voir les logs** :
```bash
docker-compose -f docker-compose.hub.yml logs -f
```

**Vérifier le statut** :
```bash
docker-compose -f docker-compose.hub.yml ps
```

**Arrêter** :
```bash
docker-compose -f docker-compose.hub.yml down
```

## 💡 Points techniques notables

1. **Architecture microservices** : Chaque composant est isolé dans son conteneur
2. **Streaming temps réel** : Utilisation de Kafka pour le flux de données
3. **Traitement distribué** : Spark pour les agrégations en streaming
4. **Déploiement professionnel** : Images Docker Hub publiques, documentation complète
5. **Monitoring** : Kafka UI pour visualiser les flux de messages
6. **Persistence** : Stockage en Parquet pour performance et compatibilité

## ⏱️ Temps de démarrage

- Téléchargement des images : ~1-2 minutes
- Démarrage des services : ~30 secondes
- Premières données visibles : ~1 minute

**Total : 2-3 minutes maximum**

## 📞 Support

Si vous rencontrez un problème :
- Consultez le guide `QUICKSTART_PROFESSOR.md`
- Section "Dépannage" dans `DOCKER.md`
- Vérifiez que Docker est installé et démarré : `docker --version`

## 🎓 Note technique

J'ai initialement ciblé l'aéroport de Ouagadougou (DFFD) mais dû au très faible trafic aérien (seulement 2-3 vols par jour visibles dans l'API OpenSky), j'ai reconfiguré le système pour Dubai International Airport (DXB), un des aéroports les plus fréquentés au monde, ce qui permet de mieux démontrer les capacités du système avec des données plus riches.

---

Je reste disponible pour toute question ou démonstration supplémentaire.

Cordialement,  
[Votre Nom]  
[Votre Email]  
[Date]

---

## 🔗 Liens rapides

- Repository : https://github.com/zbelem001/opensky-flight-tracker
- Docker Hub : https://hub.docker.com/u/zbelem001
- Dashboard : http://localhost:8501 (après démarrage)
- Kafka UI : http://localhost:8080 (après démarrage)
