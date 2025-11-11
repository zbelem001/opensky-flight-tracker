# 🔄 Action requise : Mise à jour des images Docker Hub

## ⚠️ Problème identifié

La fonction de **nettoyage automatique** (`cleanup_old_data()`) qui évite les conflits de cache Spark n'est **pas présente** dans les images Docker Hub actuelles.

Cette fonction est importante car elle :
- ✅ Nettoie automatiquement les anciens fichiers Parquet au démarrage
- ✅ Évite les conflits de checkpoint Spark
- ✅ Garantit que le dashboard affiche des données fraîches

## 📋 Ce qui doit être fait

### Option 1 : Mise à jour rapide (Recommandé) ⚡

Utilisez le script automatique :

```bash
./update-and-publish.sh
```

Ce script va :
1. Committer les modifications
2. Pusher vers GitHub
3. Rebuilder les images Docker
4. Les publier sur Docker Hub

**Temps estimé** : 10-15 minutes

### Option 2 : Mise à jour manuelle 🛠️

Si vous préférez faire étape par étape :

#### 1. Committer les modifications
```bash
git add .
git commit -m "feat: Add automatic cleanup on Spark startup"
git push origin main
```

#### 2. Rebuilder les images
```bash
docker-compose build producer
docker-compose build spark-consumer
docker-compose build dashboard
```

#### 3. Tagger les images
```bash
docker tag opensky-flight-tracker_producer zbelem001/opensky-producer:latest
docker tag opensky-flight-tracker_spark-consumer zbelem001/opensky-spark:latest
docker tag opensky-flight-tracker_dashboard zbelem001/opensky-dashboard:latest
```

#### 4. Pusher sur Docker Hub
```bash
# Se connecter si nécessaire
docker login

# Pusher les images
docker push zbelem001/opensky-producer:latest
docker push zbelem001/opensky-spark:latest
docker push zbelem001/opensky-dashboard:latest
```

## 🎯 Pour votre professeur

Une fois les images mises à jour, votre professeur pourra :

```bash
# Télécharger les dernières versions
docker-compose -f docker-compose.hub.yml pull

# Lancer le projet
docker-compose -f docker-compose.hub.yml up -d
```

Le nettoyage automatique sera alors intégré et le dashboard fonctionnera immédiatement sans problème de cache !

## 📝 Modifications apportées

### Dans `spark_consumer.py`

```python
def cleanup_old_data(self):
    """Nettoie les anciens fichiers Parquet et checkpoint au démarrage"""
    data_path = os.getenv('FLIGHTS_DATA_PATH', '/tmp/flights_data')
    checkpoint_path = os.getenv('CHECKPOINT_PATH', '/data/checkpoint')
    
    for path in [data_path, checkpoint_path]:
        if os.path.exists(path):
            try:
                logger.info(f"🧹 Nettoyage de {path}...")
                shutil.rmtree(path)
                logger.info(f"✅ {path} nettoyé avec succès")
            except Exception as e:
                logger.warning(f"⚠️  Impossible de nettoyer {path}: {e}")
    
    # Recréer les répertoires
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(checkpoint_path, exist_ok=True)
```

Cette fonction est appelée automatiquement dans `__init__()`.

## ⏰ Timing

Si vous ne pouvez pas mettre à jour maintenant, votre professeur peut utiliser le workaround :

```bash
# Au lieu de juste up -d
docker-compose -f docker-compose.hub.yml down -v  # Nettoie les volumes
docker-compose -f docker-compose.hub.yml up -d    # Redémarre proprement
```

Ou utiliser le script fourni :
```bash
./start-clean.sh
```

Mais il est **fortement recommandé** de mettre à jour les images pour que tout fonctionne automatiquement ! ✨

## 🚀 Status de mise à jour

- [ ] Modifications committées sur GitHub
- [ ] Images Docker reconstruites
- [ ] Images publiées sur Docker Hub
- [ ] Guides mis à jour (GUIDE_PROFESSEUR_SIMPLE.md, DEMARRAGE_RAPIDE.md)
- [ ] Testé localement avec `docker-compose.hub.yml`

---

**Date** : 11 novembre 2025  
**Action** : Mise à jour nécessaire avant remise du projet
