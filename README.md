# dataplumber.app

# Setup
Make the python venv for the backend

    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

and the node modules for the backend

    cd ../frontend
    npm install
    
We serve pyodide as well, so get the files

    wget https://github.com/pyodide/pyodide/releases/download/0.23.4/pyodide-0.23.4.tar.bz2
    tar -xjf pyodide-0.23.4.tar.bz2
    rm pyodide-0.23.4.tar.bz2

# Run locally

    docker compose build
    python backend/manage.py runserver

# Deploy
Check cloudformation.yaml for info on the deployment to aws us-east-1.