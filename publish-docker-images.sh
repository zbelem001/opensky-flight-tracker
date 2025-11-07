#!/bin/bash
# Script pour publier les images Docker sur Docker Hub

set -e  # Arrêter si erreur

echo "🐳 Publication des images OpenSky Flight Tracker sur Docker Hub"
echo "================================================================"
echo ""

# Vérifier si connecté à Docker Hub
echo "🔐 Vérification de la connexion Docker Hub..."
if ! sudo docker info | grep -q "Username"; then
    echo "❌ Vous n'êtes pas connecté à Docker Hub"
    echo "📝 Veuillez vous connecter avec : sudo docker login"
    exit 1
fi

# Votre username Docker Hub (à modifier si différent)
DOCKER_USERNAME="zbelem001"

echo "✅ Connecté à Docker Hub"
echo ""

# Vérifier que les images existent
echo "🔍 Vérification des images locales..."
if ! sudo docker images | grep -q "opensky-flight-tracker_producer"; then
    echo "❌ Image producer non trouvée. Construisez d'abord avec : docker-compose build"
    exit 1
fi

echo "✅ Images locales trouvées"
echo ""

# Tagger les images
echo "🏷️  Tagging des images..."
echo "  → Producer..."
sudo docker tag opensky-flight-tracker_producer ${DOCKER_USERNAME}/opensky-producer:latest

echo "  → Spark Consumer..."
sudo docker tag opensky-flight-tracker_spark-consumer ${DOCKER_USERNAME}/opensky-spark:latest

echo "  → Dashboard..."
sudo docker tag opensky-flight-tracker_dashboard ${DOCKER_USERNAME}/opensky-dashboard:latest

echo "✅ Images taguées"
echo ""

# Push sur Docker Hub
echo "📤 Push des images sur Docker Hub..."
echo "⏳ Cela peut prendre quelques minutes..."
echo ""

echo "  → Pushing producer..."
sudo docker push ${DOCKER_USERNAME}/opensky-producer:latest

echo "  → Pushing spark-consumer..."
sudo docker push ${DOCKER_USERNAME}/opensky-spark:latest

echo "  → Pushing dashboard..."
sudo docker push ${DOCKER_USERNAME}/opensky-dashboard:latest

echo ""
echo "🎉 SUCCÈS ! Toutes les images sont publiées sur Docker Hub"
echo ""
echo "📋 Vos images :"
echo "  • ${DOCKER_USERNAME}/opensky-producer:latest"
echo "  • ${DOCKER_USERNAME}/opensky-spark:latest"
echo "  • ${DOCKER_USERNAME}/opensky-dashboard:latest"
echo ""
echo "🔗 Voir sur Docker Hub : https://hub.docker.com/u/${DOCKER_USERNAME}"
echo ""
echo "✅ Votre prof peut maintenant lancer le projet avec :"
echo "   docker-compose -f docker-compose.hub.yml up -d"
