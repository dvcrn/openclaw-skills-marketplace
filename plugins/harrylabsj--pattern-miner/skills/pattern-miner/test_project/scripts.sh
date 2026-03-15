#!/bin/bash

# Common setup pattern
setup_project() {
    echo "Setting up project..."
    mkdir -p "$1"
    cd "$1"
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

# Another setup pattern
init_workspace() {
    echo "Initializing workspace..."
    mkdir -p "$1"
    cd "$1"
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
}

# Deployment pattern
deploy_app() {
    echo "Deploying application..."
    git pull origin main
    pip install -r requirements.txt
    python manage.py migrate
    sudo systemctl restart app.service
}

# Another deployment pattern
deploy_service() {
    echo "Deploying service..."
    git pull origin main
    pip install -r requirements.txt
    python manage.py migrate
    sudo systemctl restart service.service
}
