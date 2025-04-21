# KahootAssist

KahootAssist est un projet en Python conçu pour assister dans la réponse aux questions des quiz Kahoot. Il utilise Selenium pour l'automatisation web et s'intègre à l'API Ollama pour traiter et répondre aux questions. **Le projet est actuellement en cours de développement et n'est pas encore terminé.**

## Fonctionnalités

- **Réponse automatique** : Sélectionne automatiquement la réponse la plus appropriée en fonction de la réponse de l'API Ollama.
- **Mise en surbrillance des réponses** : Met en vert la bonne réponse et en rouge les mauvaises.
- **Modèles de prompts personnalisables** : Permet de personnaliser le prompt envoyé à l'API Ollama.
- **Interface utilisateur (UI)** : Comprend une interface graphique (GUI) construite avec Tkinter pour une interaction facile.

## Limitations actuelles

- **Projet incomplet** : Certaines fonctionnalités ne sont pas encore implémentées.
- **Fichiers HTML** : Les fichiers HTML inclus sont uniquement là pour tester et comprendre le fonctionnement des boutons et des éléments de l'interface Kahoot.
- **Questions à choix multiples** : La gestion des questions à choix multiples n'est pas encore implémentée.
- **Gestion des erreurs** : Certaines parties du code nécessitent encore des améliorations pour mieux gérer les erreurs.

## Prérequis

- Python 3.8 ou supérieur
- Selenium
- `webdriver_manager`
- Tkinter (préinstallé avec Python)
- `termcolor`
- Navigateur Chrome

## Installation

1. Clonez le dépôt et accédez au répertoire du projet.

2. Installez Ollama sur votre système pour permettre l'intégration avec l'API.

3. Assurez-vous que le navigateur Chrome est installé et que ChromeDriver est correctement configuré.

4. Installez les dépendances Python nécessaires, notamment Selenium, webdriver-manager, termcolor, et configurez l'API Ollama.

5. Lan

## Description des fichiers `.py`

- **`sendtoollama.py`** : Ce fichier a été utilisé pour tester l'intégration avec l'API Ollama. Il contient des tests simples pour envoyer des requêtes à l'API et vérifier les réponses.

- **`mainmarche.py`** : Il s'agit de la première version fonctionnelle du projet. Cette version ne prend pas en charge les questions à choix multiples et se concentre uniquement sur les questions simples.

- **`main.py`** : C'est la version actuelle du projet. Elle inclut un début d'implémentation pour gérer les questions à choix multiples, mais cette fonctionnalité n'est pas encore complètement opérationnelle.