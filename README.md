# Application de Quiz à Choix Multiples

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv MyQuiz
```

2. Activer l'environnement virtuel :
- Windows : `.\MyQuiz\Scripts\activate`
- Linux/Mac : `source MyQuiz/bin/activate`

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

### Note importante concernant Pillow
Si vous avez besoin de traiter des images dans votre application, vous devrez installer Pillow séparément :
```bash
# Pour Windows
pip install --only-binary :all: Pillow

# Pour Linux/Mac
pip install Pillow
```

## Structure du Projet
```
quiz_app/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── quiz.py
│   │   └── score.py
│   ├── routes/
│   │   ├── main.py
│   │   ├── auth.py
│   │   └── scores.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       └── quiz/
├── migrations/
├── tests/
├── uploads/
├── .env
├── config.py
├── requirements.txt
└── run.py
```

## Configuration

1. Créer un fichier `.env` à la racine du projet avec les variables suivantes :
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

2. Initialiser la base de données :
```bash
flask init-db
```

## Démarrage

1. Activer l'environnement virtuel
2. Lancer l'application :
```bash
flask run
```

## Fonctionnalités

- Upload et parsing de fichiers PDF
- Création de quiz à choix multiples
- Système de scores et statistiques
- Interface utilisateur moderne
- Authentification des utilisateurs
- Base de données SQLite

## Déploiement

Pour déployer l'application :
1. Configurer les variables d'environnement de production
2. Installer les dépendances sur le serveur
3. Configurer un serveur web (Nginx/Apache)
4. Utiliser Gunicorn comme serveur WSGI

## Développement

Pour contribuer au développement :
1. Créer une branche pour votre fonctionnalité
2. Ajouter des tests pour les nouvelles fonctionnalités
3. Suivre les conventions de code Python
4. Mettre à jour la documentation

## Structure du Projet

### Backend (Python/Flask)
- `app.py` : Application principale Flask qui gère :
  - Le parsing des questions depuis un texte
  - La conversion des questions en format JSON
  - Les routes API pour l'interface web

### Frontend
- `index.html` et `index1.html` : Pages d'accueil
- `acceuil.html` : Page d'accueil alternative
- `create_quiz.html` : Interface de création de quiz
- `style.css` : Styles CSS pour l'interface utilisateur

### JavaScript
- `script.js` et `script1.js` : Logique frontend
- `analyse_quiz.js` : Analyse des quiz

### Données
- `questions.json` : Stockage des questions au format JSON
- `questions.py` et `nouvelleQuestions.py` : Gestion des questions

## Fonctionnalités Actuelles
1. Parsing de questions à partir de texte
2. Conversion des questions en format JSON
3. Interface web basique pour la création de quiz
4. Stockage des questions dans un fichier JSON

## Améliorations Suggérées

### 1. Gestion des Fichiers PDF
- Ajouter une fonctionnalité d'upload de fichiers PDF
- Implémenter un parser PDF pour extraire les questions
- Ajouter la validation du format des questions dans le PDF

### 2. Interface Utilisateur
- Moderniser l'interface avec un framework CSS (Bootstrap/Tailwind)
- Ajouter une page de visualisation des quiz
- Implémenter un système de prévisualisation des questions
- Ajouter un éditeur de questions en temps réel

### 3. Fonctionnalités de Quiz
- Ajouter un système de catégories pour les questions
- Implémenter un système de difficulté
- Ajouter des explications pour les réponses
- Créer un mode d'entraînement

### 4. Base de Données
- Migrer de JSON vers une base de données (SQLite/PostgreSQL)
- Ajouter un système d'authentification
- Permettre le partage de quiz entre utilisateurs

### 5. Fonctionnalités Avancées
- Ajouter un système de statistiques pour les quiz
- Implémenter un système de progression
- Ajouter la possibilité d'exporter les quiz en différents formats
- Créer un système de recherche de questions

### 6. Sécurité et Performance
- Ajouter la validation des entrées
- Implémenter la protection CSRF
- Optimiser le parsing des questions
- Ajouter des tests unitaires et d'intégration

## Prochaines Étapes Recommandées
1. Implémenter l'upload et le parsing de PDF
2. Moderniser l'interface utilisateur
3. Ajouter une base de données
4. Implémenter l'authentification
5. Ajouter les fonctionnalités de quiz avancées 