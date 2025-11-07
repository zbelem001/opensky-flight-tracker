# Installation et Configuration de Docker

## ✅ Docker installé avec succès !

Docker est maintenant installé et en cours d'exécution sur votre système.

## 🔧 Configuration initiale (À faire UNE FOIS)

### Activer Docker sans sudo

Pour éviter d'utiliser `sudo` à chaque commande Docker, vous avez été ajouté au groupe `docker`. 

**⚠️ IMPORTANT : Vous devez vous déconnecter et vous reconnecter** (ou redémarrer votre session) pour que cette modification prenne effet.

Pour activer immédiatement sans redémarrer :
```bash
newgrp docker
```

### Vérifier l'installation

```bash
# Vérifier la version de Docker
docker --version

# Tester Docker
docker run hello-world

# Vérifier Docker Compose
docker-compose --version
```

## 🚀 Démarrer le projet OpenSky Flight Tracker

### Option 1 : Avec Make (recommandé)
```bash
make up
```

### Option 2 : Avec Docker Compose directement
```bash
docker-compose up -d
```

### Option 3 : Voir les logs en temps réel
```bash
docker-compose up
```

## 📊 Accéder aux services

Une fois tous les services démarrés (patientez 2-3 minutes) :

- **Dashboard Streamlit** : http://localhost:8501
- **Kafka UI** : http://localhost:8080

## 🔍 Commandes utiles

### Voir l'état des conteneurs
```bash
docker-compose ps
# ou
make status
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f dashboard
docker-compose logs -f spark
docker-compose logs -f producer

# Avec Make
make logs
make logs service=dashboard
```

### Redémarrer les services
```bash
docker-compose restart
# ou
make restart
```

### Arrêter les services
```bash
docker-compose down
# ou
make down
```

### Nettoyer complètement (⚠️ supprime les données)
```bash
docker-compose down -v
# ou
make clean
```

## 🧪 Tester le déploiement

Un script de test automatique est disponible :
```bash
./test-docker.sh
```

Ce script vérifie :
- ✅ État des conteneurs
- ✅ Accessibilité des URLs
- ✅ Flux de données
- ✅ Création des fichiers Parquet

## 🐛 Dépannage

### Les conteneurs ne démarrent pas
```bash
# Voir les logs détaillés
docker-compose logs

# Reconstruire les images
docker-compose build --no-cache
docker-compose up -d
```

### Problème de permissions
```bash
# Si vous ne pouvez pas exécuter Docker sans sudo
newgrp docker

# Ou redémarrez votre session
```

### Ports déjà utilisés
Si les ports 8501 (Streamlit) ou 8080 (Kafka UI) sont déjà utilisés :

```bash
# Trouver quel processus utilise le port
sudo lsof -i :8501
sudo lsof -i :8080

# Arrêter le processus
sudo kill -9 <PID>
```

### Nettoyer Docker complètement
```bash
# Arrêter tous les conteneurs
docker stop $(docker ps -aq)

# Supprimer tous les conteneurs
docker rm $(docker ps -aq)

# Supprimer toutes les images
docker rmi $(docker images -q)

# Nettoyer les volumes et réseaux
docker system prune -a --volumes
```

## 📖 Documentation complète

Pour plus d'informations, consultez :
- `DOCKER.md` - Guide complet de déploiement
- `README.md` - Présentation du projet
- `Makefile` - Liste de toutes les commandes Make disponibles

## 🎯 Prochaines étapes

1. **Se déconnecter/reconnecter** pour activer le groupe docker
2. **Démarrer les services** : `make up`
3. **Tester le déploiement** : `./test-docker.sh`
4. **Ouvrir le dashboard** : http://localhost:8501

Bon vol avec OpenSky Flight Tracker ! ✈️
