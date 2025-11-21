# 🚀 Architecture Big Data – Pipeline d’Ingestion de Logs

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Hadoop](https://img.shields.io/badge/Apache_Hadoop-66CCFF?style=for-the-badge&logo=apachehadoop&logoColor=black)
![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?style=for-the-badge&logo=opensearch&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Ce projet met en place une **architecture Big Data complète**, entièrement conteneurisée avec **Docker**, permettant :

- l’ingestion de logs applicatifs,
- leur stockage distribué dans **Hadoop HDFS**,
- leur transformation via un script **Python ETL**,
- leur indexation dans **OpenSearch**,
- leur visualisation via **OpenSearch Dashboards**.

---

## 📑 Table des Matières
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Structure du Projet](#-structure-du-projet)
- [Installation et Démarrage](#-installation-et-démarrage)
- [Utilisation du Pipeline](#-utilisation-du-pipeline)
- [Visualisation](#-visualisation)
- [Auteur](#-auteur)

---

## 🏗 Architecture

L’infrastructure repose sur un réseau Docker unique (`tp-network`) composé de :

### 🔷 Cluster Hadoop (3 nœuds)
- **NameNode + ResourceManager**
  - Gestion des métadonnées HDFS
  - Supervision YARN
- **2× DataNodes + NodeManagers**
  - Stockage distribué
  - Exécution des tâches YARN

### 🔷 Cluster OpenSearch (2 nœuds)
- Stockage indexé des logs transformés
- Recherche rapide full-text

### 🔷 OpenSearch Dashboards
- Interface graphique pour l’exploration et la création de visualisations  
  *(http://localhost:5601)*

### 🔷 Script ETL Python (conteneur éphémère)
- **Extract** : lecture des fichiers depuis HDFS  
- **Transform** : parsing via Regex  
- **Load** : indexation dans OpenSearch  

---

## 🛠 Prérequis

- Docker & Docker Compose
- Windows, Linux ou macOS
- 8–16 Go de RAM recommandés
- Sur Linux/WSL, configurer :
  ```bash
  sudo sysctl -w vm.max_map_count=262144

  # Projet ETL de Logs (Hadoop & OpenSearch)

Ce projet déploie un pipeline complet pour l'ingestion, le traitement et la visualisation de logs d'accès web en utilisant **Hadoop (HDFS)** pour le stockage et **OpenSearch** pour l'indexation et l'analyse.

## 📂 Structure du Projet

```
tp-final/
├── docker-compose.yml   # Déploiement complet Hadoop + OpenSearch
├── hadoop.env           # Configuration des services Hadoop
├── etl.py               # Script Python ETL
├── access.log           # Fichier de logs source
└── README.md            # Documentation
```

## 🚀 Installation et Démarrage

### 1️⃣ Lancer les services

Utilisez Docker Compose pour démarrer tous les conteneurs nécessaires (NameNode, DataNode, OpenSearch, etc.).

```bash
docker-compose up -d
```

> ⏳ **Attendre 2 à 3 minutes** avant utilisation (le temps d'initialisation du NameNode et d'OpenSearch est crucial).

### 2️⃣ Vérifier l’état

Vérifiez que tous les services sont en cours d'exécution.

```bash
docker-compose ps
```

## 🔄 Utilisation du Pipeline

### 🧮 Étape 1 — Générer un fichier de logs (exemple PowerShell)

Pour simuler des données de logs, exécutez ces commandes (ou leurs équivalents dans votre shell) pour créer un fichier `access.log`.

```powershell
Set-Content access.log "192.168.1.10 - - [21/Nov/2025:10:00:00 +0000] ""GET /index.html HTTP/1.1"" 200 1024"
Add-Content access.log "192.168.1.11 - - [21/Nov/2025:10:05:00 +0000] ""POST /login HTTP/1.1"" 403 512"
Add-Content access.log "192.168.1.12 - - [21/Nov/2025:10:10:00 +0000] ""GET /dashboard HTTP/1.1"" 200 2048"
Add-Content access.log "192.168.1.13 - - [21/Nov/2025:10:15:00 +0000] ""GET /missing-page HTTP/1.1"" 404 128"
Add-Content access.log "192.168.1.10 - - [21/Nov/2025:10:20:00 +0000] ""DELETE /user/1 HTTP/1.1"" 500 0"
```

### 🗂 Étape 2 — Copier le fichier dans HDFS

Transférez le fichier `access.log` local dans le système de fichiers distribué Hadoop (HDFS).

```bash
# Copier le fichier local vers le conteneur NameNode
docker cp access.log namenode:/tmp/access.log

# Créer le répertoire dans HDFS
docker exec namenode hdfs dfs -mkdir -p /user/logs_tp

# Placer le fichier dans HDFS (utilisation de -f pour forcer l'écrasement si déjà présent)
docker exec namenode hdfs dfs -put -f /tmp/access.log /user/logs_tp/
```

### ⚙️ Étape 3 — Exécuter le script ETL

Exécutez le script Python `etl.py` pour lire les logs depuis HDFS, les transformer et les indexer dans OpenSearch.

```bash
docker run --rm -it --network=tp-final_tp-network -v "${PWD}/etl.py:/etl.py" python:3.9-slim bash -c "pip install hdfs opensearch-py && python /etl.py"
```

Si l'exécution est réussie, vous devriez voir une sortie similaire à :

```
✅ Log indexé : ...
🎉 Migration terminée avec succès !
```

## 📊 Visualisation

Accédez à OpenSearch Dashboards pour visualiser les données indexées.

### Accès

Ouvrez votre navigateur et accédez à :

```
http://localhost:5601
```

### Création de l'Index Pattern

1.  Allez dans **Stack Management** → **Index Patterns**.
2.  Cliquez sur **Create index pattern**.
3.  Entrez le pattern suivant :

```
logs-app-*
```

### Exploration et Dashboards

* **Menu Discover :**
    * Explorez les logs indexés pour vérifier la bonne ingestion des données.
* **Menu Visualize :**
    * Créez vos dashboards personnalisés (par exemple : un histogramme des codes HTTP, une carte des adresses IP, etc.).
