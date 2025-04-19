#!/bin/bash

# Ajouter le fichier requirements.txt
git add requirements.txt

# Commiter avec un message
git commit -m "Fix Flask/Werkzeug versions"

# Pousser les changements vers le dépôt distant
git push
