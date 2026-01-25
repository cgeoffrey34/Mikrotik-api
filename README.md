# Mikrotik Management Platform

Interface web centralisee pour l'administration des routeurs Mikrotik via leur API.

## Fonctionnalites

### Gestion des routeurs
- Liste des routeurs enregistres (nom, etat, IP, modele, version)
- Ajout, modification et suppression de routeurs
- Test de connexion et verification de l'etat

### Monitoring
- Utilisation CPU en temps reel
- Memoire RAM (utilisee/totale)
- Espace disque
- Uptime
- Nombre de clients WiFi connectes
- Baux DHCP actifs
- Connexions actives

### Configuration
- **Interfaces**: Visualisation et activation/desactivation
- **DHCP**: Gestion des baux, ajout de baux statiques
- **WiFi**: Interfaces wireless et clients connectes
- **Firewall**: Regles de filtrage et NAT
- **DNS**: Entrees DNS statiques
- **Routes**: Table de routage
- **QoS**: Files d'attente simples
- **Systeme**: Logs, utilisateurs, sauvegarde, export de configuration

## Installation

### Prerequis
- Docker et Docker Compose installes sur la VM
- Acces reseau aux routeurs Mikrotik (port API 8728 ou 8729 pour SSL)

### Deploiement rapide

1. Cloner le depot :
```bash
git clone https://github.com/votre-repo/mikrotik-api.git
cd mikrotik-api
```

2. Configurer l'environnement :
```bash
cp .env.example .env
# Editer .env si necessaire
```

3. Lancer l'application :
```bash
docker-compose up -d
```

4. Acceder a l'interface :
```
http://votre-vm:8080
```

## Configuration

### Variables d'environnement (.env)

| Variable | Description | Defaut |
|----------|-------------|--------|
| `WEB_PORT` | Port de l'interface web | 8080 |
| `SECRET_KEY` | Cle secrete pour l'API | - |
| `STATS_POLLING_INTERVAL` | Intervalle de collecte des stats (sec) | 30 |

### Configuration Mikrotik

Sur chaque routeur Mikrotik, assurez-vous que :

1. L'API est activee :
```
/ip service enable api
```

2. (Optionnel) Pour SSL :
```
/ip service enable api-ssl
```

3. Un utilisateur avec les droits API existe :
```
/user add name=apiuser password=motdepasse group=full
```

## Architecture

```
mikrotik-api/
├── backend/           # API FastAPI (Python)
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── models/    # Modeles SQLAlchemy
│   │   ├── schemas/   # Schemas Pydantic
│   │   └── services/  # Service Mikrotik
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Interface Vue.js
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── stores/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Technologies

### Backend
- **FastAPI** - Framework API moderne et performant
- **SQLAlchemy** - ORM pour la base de donnees
- **SQLite** - Base de donnees legere
- **librouteros** - Client API Mikrotik

### Frontend
- **Vue.js 3** - Framework JavaScript reactif
- **Tailwind CSS** - Framework CSS utilitaire
- **Pinia** - Gestion d'etat
- **Vue Router** - Routage SPA

### Deploiement
- **Docker** - Conteneurisation
- **Nginx** - Serveur web et proxy

## API REST

Documentation automatique disponible a :
- Swagger UI : `http://votre-vm:8080/docs`
- ReDoc : `http://votre-vm:8080/redoc`

### Endpoints principaux

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/routers` | Liste des routeurs |
| POST | `/api/routers` | Ajouter un routeur |
| GET | `/api/routers/{id}` | Details d'un routeur |
| PUT | `/api/routers/{id}` | Modifier un routeur |
| DELETE | `/api/routers/{id}` | Supprimer un routeur |
| POST | `/api/routers/{id}/test` | Tester la connexion |
| POST | `/api/routers/{id}/refresh` | Actualiser les stats |
| GET | `/api/routers/{id}/dhcp/leases` | Baux DHCP |
| GET | `/api/routers/{id}/wifi/clients` | Clients WiFi |
| GET | `/api/routers/{id}/interfaces` | Interfaces |
| GET | `/api/routers/{id}/firewall/filter` | Regles firewall |

## Developpement

### Lancer en mode developpement

Backend :
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend :
```bash
cd frontend
npm install
npm run dev
```

## Securite

- Les mots de passe des routeurs sont stockes en base de donnees
- Il est recommande de :
  - Changer la `SECRET_KEY` en production
  - Utiliser HTTPS avec un reverse proxy
  - Restreindre l'acces reseau a l'application
  - Utiliser des comptes Mikrotik avec privileges limites

## Support

Pour les problemes et suggestions, ouvrir une issue sur le depot GitHub.

## Licence

MIT License
