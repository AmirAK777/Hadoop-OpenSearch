import re
import sys
from hdfs import InsecureClient
from opensearchpy import OpenSearch

# --- CONFIGURATION ---
HDFS_URL = 'http://namenode:9870'
HDFS_USER = 'root'
HDFS_FILE_PATH = '/user/logs_tp/access.log'

OPENSEARCH_HOST = 'opensearch-node1'
OPENSEARCH_PORT = 9200
INDEX_NAME = 'logs-app-20251121'

# --- 1. CONNEXIONS ---
print(f"🔌 Connexion à HDFS ({HDFS_URL})...")
try:
    # Connexion au NameNode via WebHDFS
    hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)
    # Vérification simple : lister le dossier
    print(f"   Fichiers trouvés : {hdfs_client.list('/user/logs_tp/')}")
except Exception as e:
    print(f"❌ Erreur HDFS : {e}")
    sys.exit(1)

print(f"🔌 Connexion à OpenSearch ({OPENSEARCH_HOST})...")
os_client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False
)

# --- 2. LECTURE ET TRANSFORMATION ---
print("🚀 Démarrage du traitement...")

# Regex pour parser une ligne de log Apache standard
# Ex: 192.168.1.10 - - [21/Nov/2025...] "GET /index.html..." 200 1024
LOG_PATTERN = re.compile(r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) (\d+)')

# On lit le fichier depuis HDFS (streaming)
with hdfs_client.read(HDFS_FILE_PATH, encoding='utf-8') as reader:
    for line in reader:
        line = line.strip()
        if not line: continue

        match = LOG_PATTERN.match(line)
        if match:
            # Transformation en JSON
            ip, timestamp, request, status, size = match.groups()
            
            # Petit nettoyage de la date ou méthode si besoin
            method = request.split()[0] if len(request.split()) > 0 else "UNKNOWN"
            url = request.split()[1] if len(request.split()) > 1 else "UNKNOWN"

            doc = {
                "client_ip": ip,
                "raw_timestamp": timestamp, # Idéalement à convertir en format ISO
                "method": method,
                "url": url,
                "status": int(status),
                "size": int(size),
                "original_log": line
            }

            # --- 3. CHARGEMENT DANS OPENSEARCH ---
            response = os_client.index(
                index=INDEX_NAME,
                body=doc,
                refresh=True # Pour que ce soit visible tout de suite
            )
            print(f"✅ Log indexé : {method} {url} (Status: {status})")
        else:
            print(f"⚠️  Ligne ignorée (format incorrect) : {line}")

print("🎉 Migration terminée avec succès !")