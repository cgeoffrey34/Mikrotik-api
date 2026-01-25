# Installation sur Debian 13 (Trixie)

Guide complet pour deployer la plateforme Mikrotik Manager sur Debian 13.

## Prerequis

- Debian 13 (Trixie) installe
- Acces root ou utilisateur avec sudo
- Connexion internet
- Au minimum 1 Go de RAM et 10 Go d'espace disque

## Etape 1 : Mise a jour du systeme

```bash
sudo apt update && sudo apt upgrade -y
```

## Etape 2 : Installation des dependances

```bash
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    git \
    lsb-release
```

## Etape 3 : Installation de Docker

### Ajouter le depot Docker officiel

```bash
# Creer le repertoire pour les cles
sudo install -m 0755 -d /etc/apt/keyrings

# Telecharger la cle GPG Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Ajouter le depot Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

> **Note**: Si Debian 13 (Trixie) n'est pas encore supporte par Docker, utilisez "bookworm" a la place de "$VERSION_CODENAME"

### Installer Docker

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Configurer Docker pour l'utilisateur courant (optionnel)

```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Appliquer les changements (ou se deconnecter/reconnecter)
newgrp docker
```

### Verifier l'installation

```bash
docker --version
docker compose version
```

## Etape 4 : Installation de Mikrotik Manager

### Cloner le depot

```bash
cd /opt
sudo git clone https://github.com/cgeoffrey34/Mikrotik-api.git mikrotik-manager
sudo chown -R $USER:$USER /opt/mikrotik-manager
cd /opt/mikrotik-manager
```

### Configurer l'application

```bash
# Copier le fichier de configuration
cp .env.example .env

# Editer la configuration (optionnel)
nano .env
```

Configuration disponible dans `.env` :
```env
# Port d'acces web (defaut: 8080)
WEB_PORT=8080

# Cle secrete pour l'API (generer une cle unique)
SECRET_KEY=votre-cle-secrete-unique

# Intervalle de collecte des stats en secondes
STATS_POLLING_INTERVAL=30
```

Pour generer une cle secrete :
```bash
openssl rand -hex 32
```

### Lancer l'application

```bash
docker compose up -d
```

### Verifier le deploiement

```bash
# Voir les conteneurs
docker compose ps

# Voir les logs
docker compose logs -f
```

## Etape 5 : Configuration du pare-feu (optionnel)

Si vous utilisez ufw :

```bash
sudo apt install -y ufw
sudo ufw allow 8080/tcp
sudo ufw enable
```

Si vous utilisez nftables/iptables :

```bash
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

## Etape 6 : Acces a l'interface

Ouvrez votre navigateur et accedez a :

```
http://IP-DE-VOTRE-VM:8080
```

## Etape 7 : Demarrage automatique

Docker est configure pour demarrer automatiquement. Pour s'en assurer :

```bash
sudo systemctl enable docker
```

Les conteneurs redemarreront automatiquement grace a la politique `restart: unless-stopped` dans docker-compose.yml.

---

## Commandes utiles

### Gestion de l'application

```bash
cd /opt/mikrotik-manager

# Demarrer
docker compose up -d

# Arreter
docker compose down

# Redemarrer
docker compose restart

# Voir les logs
docker compose logs -f

# Voir les logs d'un service specifique
docker compose logs -f backend
docker compose logs -f frontend

# Reconstruire apres modification
docker compose up -d --build
```

### Mise a jour

```bash
cd /opt/mikrotik-manager

# Arreter l'application
docker compose down

# Recuperer les mises a jour
git pull

# Reconstruire et relancer
docker compose up -d --build
```

### Sauvegarde de la base de donnees

```bash
# La base SQLite est dans le volume Docker
docker compose cp backend:/data/mikrotik.db ./backup-$(date +%Y%m%d).db
```

### Restauration

```bash
docker compose cp ./backup.db backend:/data/mikrotik.db
docker compose restart backend
```

---

## Depannage

### Les conteneurs ne demarrent pas

```bash
# Verifier les logs
docker compose logs

# Verifier l'espace disque
df -h

# Verifier la memoire
free -m
```

### Impossible de se connecter a l'interface

1. Verifier que les conteneurs tournent :
```bash
docker compose ps
```

2. Verifier le pare-feu :
```bash
sudo ufw status
```

3. Verifier que le port est ouvert :
```bash
sudo ss -tlnp | grep 8080
```

### Erreur de connexion aux routeurs Mikrotik

1. Verifier que l'API est activee sur le routeur :
```
/ip service print
```

2. Verifier la connectivite reseau :
```bash
ping IP-DU-ROUTEUR
telnet IP-DU-ROUTEUR 8728
```

3. Verifier les identifiants et le port API

---

## Configuration HTTPS avec Nginx (recommande pour la production)

### Installer Nginx et Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Configurer le reverse proxy

```bash
sudo nano /etc/nginx/sites-available/mikrotik-manager
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Activer le site

```bash
sudo ln -s /etc/nginx/sites-available/mikrotik-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Obtenir un certificat SSL

```bash
sudo certbot --nginx -d votre-domaine.com
```

Le certificat sera renouvele automatiquement.

---

## Resume des commandes d'installation rapide

```bash
# Installation complete en une seule commande (a executer en root)
apt update && apt upgrade -y && \
apt install -y ca-certificates curl gnupg git && \
install -m 0755 -d /etc/apt/keyrings && \
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
chmod a+r /etc/apt/keyrings/docker.gpg && \
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
apt update && \
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && \
cd /opt && \
git clone https://github.com/cgeoffrey34/Mikrotik-api.git mikrotik-manager && \
cd mikrotik-manager && \
cp .env.example .env && \
docker compose up -d
```

Accedez ensuite a `http://IP-DE-VOTRE-VM:8080`
