.PHONY: help build up down restart logs clean test

# Couleurs pour l'affichage
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)OpenSky Flight Tracker - Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Construit les images Docker
	@echo "$(BLUE)🏗️  Construction des images Docker...$(NC)"
	docker-compose build

up: ## Démarre tous les services
	@echo "$(BLUE)🚀 Démarrage des services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services démarrés$(NC)"
	@echo "$(BLUE)Dashboard: http://localhost:8501$(NC)"
	@echo "$(BLUE)Kafka UI: http://localhost:8080$(NC)"

down: ## Arrête tous les services
	@echo "$(BLUE)🛑 Arrêt des services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services arrêtés$(NC)"

restart: down up ## Redémarre tous les services

logs: ## Affiche les logs de tous les services
	docker-compose logs -f

logs-producer: ## Affiche les logs du producer
	docker-compose logs -f producer

logs-spark: ## Affiche les logs de Spark
	docker-compose logs -f spark-consumer

logs-dashboard: ## Affiche les logs du dashboard
	docker-compose logs -f dashboard

logs-kafka: ## Affiche les logs de Kafka
	docker-compose logs -f kafka

ps: ## Affiche l'état des services
	@docker-compose ps

clean: ## Nettoie les conteneurs et images
	@echo "$(RED)⚠️  Nettoyage des conteneurs et images...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

clean-volumes: ## Supprime les volumes de données
	@echo "$(RED)⚠️  Suppression des volumes...$(NC)"
	docker volume rm opensky-flights-data opensky-checkpoint 2>/dev/null || true
	@echo "$(GREEN)✓ Volumes supprimés$(NC)"

rebuild: clean build up ## Nettoie, reconstruit et démarre

dev-up: ## Démarre en mode développement (sans cache)
	docker-compose build --no-cache
	docker-compose up

shell-producer: ## Ouvre un shell dans le container producer
	docker-compose exec producer /bin/bash

shell-spark: ## Ouvre un shell dans le container spark
	docker-compose exec spark-consumer /bin/bash

shell-dashboard: ## Ouvre un shell dans le container dashboard
	docker-compose exec dashboard /bin/bash

test: ## Teste que tous les services fonctionnent
	@echo "$(BLUE)🧪 Test des services...$(NC)"
	@docker-compose ps | grep -q "Up" && echo "$(GREEN)✓ Services actifs$(NC)" || echo "$(RED)✗ Certains services sont arrêtés$(NC)"
	@curl -s http://localhost:8501 > /dev/null && echo "$(GREEN)✓ Dashboard accessible$(NC)" || echo "$(RED)✗ Dashboard inaccessible$(NC)"
	@curl -s http://localhost:8080 > /dev/null && echo "$(GREEN)✓ Kafka UI accessible$(NC)" || echo "$(RED)✗ Kafka UI inaccessible$(NC)"

stats: ## Affiche les statistiques des conteneurs
	docker stats --no-stream

backup: ## Sauvegarde les données
	@echo "$(BLUE)💾 Sauvegarde des données...$(NC)"
	mkdir -p backups
	docker run --rm -v opensky-flights-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/flights-data-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "$(GREEN)✓ Sauvegarde créée dans ./backups/$(NC)"

restore: ## Restaure les données (usage: make restore FILE=backup.tar.gz)
	@if [ -z "$(FILE)" ]; then echo "$(RED)Erreur: Spécifiez FILE=backup.tar.gz$(NC)"; exit 1; fi
	@echo "$(BLUE)♻️  Restauration des données...$(NC)"
	docker run --rm -v opensky-flights-data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(FILE) -C /
	@echo "$(GREEN)✓ Données restaurées$(NC)"

update: ## Met à jour le projet
	@echo "$(BLUE)🔄 Mise à jour...$(NC)"
	git pull
	docker-compose pull
	docker-compose build
	docker-compose up -d
	@echo "$(GREEN)✓ Projet mis à jour$(NC)"
