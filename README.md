# ML Server App

Ce projet est une application serveur Django pour le traitement de ML (Machine Learning).

## Installation

1. Cloner le dépôt
2. Activer l'environnement virtuel:
   ```
   source venv/bin/activate
   ```
3. Installer les dépendances:
   ```
   pip install -r ml_server_app/requirements.txt
   ```

## Démarrage du serveur

```
cd ml_server_app
python manage.py runserver
```

Le serveur sera accessible à l'adresse: http://127.0.0.1:8000/

## Points d'API

- `/api/` - Point d'entrée principal de l'API