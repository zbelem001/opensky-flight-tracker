# 🐳 Guide de Déploiement Docker

Ce guide explique comment déployer le projet OpenSky Flight Tracker avec Docker.

## 📋 Prérequis

- Docker Engine 20.10+
- Docker Compose 2.0+
- Au moins 4 GB de RAM disponible
- Connexion Internet (pour télécharger les images et les données OpenSky)

## 🚀 Démarrage Rapide

### 1. Lancer tous les services

```bash
docker-compose up -d
```

Cette commande va :
- Démarrer Zookeeper et Kafka
- Lancer le Producer pour récupérer les données OpenSky
- Démarrer Spark pour traiter les données
- Lancer le dashboard Streamlit

### 2. Vérifier l'état des services

```bash
docker-compose ps
```

Tous les services doivent être en état "Up" ou "running".

### 3. Accéder aux interfaces

- **Dashboard Streamlit** : http://localhost:8501
- **Kafka UI** : http://localhost:8080

### 4. Voir les logs

Pour voir les logs de tous les services :
```bash
docker-compose logs -f
```

Pour un service spécifique :
```bash
docker-compose logs -f dashboard
docker-compose logs -f producer
docker-compose logs -f spark-consumer
```

### 5. Arrêter les services

```bash
docker-compose down
```

Pour arrêter ET supprimer les volumes (données) :
```bash
docker-compose down -v
```

## 🏗️ Build des Images

Si vous avez modifié le code, reconstruisez les images :

```bash
docker-compose build
```

Pour forcer la reconstruction sans cache :
```bash
docker-compose build --no-cache
```

## 🔧 Configuration

### Variables d'environnement

Vous pouvez créer un fichier `.env` à la racine du projet pour personnaliser les paramètres :

```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_TOPIC=flights-data

# Producer
FETCH_INTERVAL=30

# Paths
FLIGHTS_DATA_PATH=/data/flights_data

# Streamlit
STREAMLIT_SERVER_PORT=8501
```

### Modifier l'intervalle de récupération

Éditez le `docker-compose.yml` :

```yaml
producer:
  environment:
    FETCH_INTERVAL: 60  # Changez la valeur (en secondes)
```

## 📊 Volumes Docker

Le projet utilise des volumes nommés pour persister les données :

- `opensky-flights-data` : Données des vols en format Parquet
- `opensky-checkpoint` : Checkpoints Spark pour la récupération

### Gérer les volumes

Lister les volumes :
```bash
docker volume ls
```

Inspecter un volume :
```bash
docker volume inspect opensky-flights-data
```

Nettoyer un volume :
```bash
docker volume rm opensky-flights-data
```

## 🔍 Dépannage

### Le dashboard ne s'affiche pas

1. Vérifiez que tous les services sont démarrés :
   ```bash
   docker-compose ps
   ```

2. Vérifiez les logs du dashboard :
   ```bash
   docker-compose logs dashboard
   ```

3. Vérifiez que le port 8501 n'est pas déjà utilisé :
   ```bash
   lsof -i :8501
   ```

### Kafka ne démarre pas

1. Vérifiez que Zookeeper est démarré :
   ```bash
   docker-compose logs zookeeper
   ```

2. Attendez quelques secondes que Kafka démarre complètement
3. Vérifiez les logs Kafka :
   ```bash
   docker-compose logs kafka
   ```

### Spark Consumer plante

1. Vérifiez la mémoire disponible :
   ```bash
   docker stats
   ```

2. Augmentez la mémoire allouée à Docker dans les paramètres Docker Desktop

3. Vérifiez les logs :
   ```bash
   docker-compose logs spark-consumer
   ```

### Aucune donnée dans le dashboard

1. Vérifiez que le Producer fonctionne :
   ```bash
   docker-compose logs producer | grep "Vol envoyé"
   ```

2. Vérifiez que Spark traite les données :
   ```bash
   docker-compose logs spark-consumer | grep "Batch:"
   ```

3. Vérifiez les fichiers Parquet :
   ```bash
   docker-compose exec dashboard ls -lh /data/flights_data/
   ```

## 🌐 Déploiement sur un Serveur

### Avec Docker Compose

1. Copiez le projet sur votre serveur
2. Modifiez les ports si nécessaire dans `docker-compose.yml`
3. Lancez avec :
   ```bash
   docker-compose up -d
   ```

### Configuration du Firewall

Ouvrez les ports nécessaires :
- 8501 (Streamlit Dashboard)
- 8080 (Kafka UI - optionnel)

```bash
# UFW
sudo ufw allow 8501/tcp
sudo ufw allow 8080/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### Avec un Reverse Proxy (Nginx)

Configuration Nginx exemple :

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 Sécurité

Pour un déploiement en production :

1. **Activez l'authentification Streamlit** : Ajoutez un fichier `.streamlit/secrets.toml`
2. **Utilisez HTTPS** : Configurez un certificat SSL (Let's Encrypt)
3. **Limitez l'accès aux ports** : N'exposez que le port 8501
4. **Mettez à jour régulièrement** : `docker-compose pull && docker-compose up -d`

## 📦 Déploiement sur le Cloud

### Streamlit Cloud

1. Poussez votre code sur GitHub
2. Connectez-vous à [share.streamlit.io](https://share.streamlit.io)
3. Déployez depuis votre repository GitHub
4. **Note** : Vous devrez déployer Kafka et Spark séparément

### AWS / Azure / GCP

Utilisez leurs services de containers :
- **AWS** : ECS ou EKS
- **Azure** : Container Instances ou AKS
- **GCP** : Cloud Run ou GKE

### Docker Swarm / Kubernetes

Le fichier `docker-compose.yml` peut être converti pour ces orchestrateurs.

## 🔄 Mise à jour

Pour mettre à jour le projet :

```bash
# Arrêter les services
docker-compose down

# Récupérer les dernières modifications
git pull

# Reconstruire les images
docker-compose build

# Redémarrer
docker-compose up -d
```

## 📝 Logs et Monitoring

### Centraliser les logs

Ajoutez à `docker-compose.yml` :

```yaml
services:
  dashboard:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring avec Prometheus

Vous pouvez ajouter Prometheus et Grafana pour monitorer les services.

## 🆘 Support

En cas de problème :
1. Consultez les logs : `docker-compose logs`
2. Vérifiez l'état : `docker-compose ps`
3. Redémarrez les services : `docker-compose restart`
4. Ouvrez une issue sur GitHub

## 📚 Ressources

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Kafka](https://kafka.apache.org/documentation/)
