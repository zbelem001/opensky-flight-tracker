#!/bin/bash

echo "🧹 Nettoyage et démarrage du projet OpenSky Flight Tracker..."

# Arrêter les conteneurs existants
echo "⏹️  Arrêt des conteneurs..."
sudo docker-compose -f docker-compose.hub.yml down

# Nettoyer les données Spark/Parquet dans le volume
echo "🗑️  Nettoyage des anciennes données..."
sudo docker volume rm opensky-flights-data 2>/dev/null || true
sudo docker volume rm opensky-checkpoint 2>/dev/null || true

# Démarrer les services
echo "🚀 Démarrage des services..."
sudo docker-compose -f docker-compose.hub.yml up -d

# Attendre que les services démarrent
echo "⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

# Vérifier le statut
echo ""
echo "📊 Statut des services:"
sudo docker-compose -f docker-compose.hub.yml ps

echo ""
echo "✅ Projet démarré !"
echo "📍 Dashboard disponible sur: http://localhost:8501"
echo "📍 Kafka UI disponible sur: http://localhost:8080"
echo ""
echo "💡 Patientez 30-40 secondes pour voir les premières données..."
