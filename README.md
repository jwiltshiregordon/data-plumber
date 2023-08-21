# dataplumber.app
A tool for helping less-technical team members submit valid data.

There are two sides to the app: definition and validation. These workflows are often undertaken by different users.
The definer specifies a csv schema using `/format-builder/` and the validator uses the workflow at `/format-checker/`.

## Format builder
The format builder workflow is for schema definition and publication.

1. (optional) supply a valid csv to autodetect column headers and datatypes
2. add/remove columns, specify datatypes
3. publish the format and generate a public url for the checker workflow.
4. (optional) generate a python parser for the schema for use in your own app

## Format checker
The format checker workflow is for detecting and correcting errors in a csv

1. visit the url supplied by the format builder
2. load your csv
3. find all problem cells and their error messages

If the format builder uses the generated parser, then parsing of a csv that passes the format checker is guaranteed to
succeed.

## Features

- Local File Processing: Users can input a CSV file, which is processed locally in the browser. No data is uploaded to the server.

- Column Management: Users can add, remove, and edit columns. The details of each column are editable, and users can send the Python code for a column's parser to the code editor.

- Code Editor: The application includes a code editor where users can define new parsers or redefine existing parsers using Python. The code is run in the browser using Pyodide.

- Parser Generation: The application generates Python parser code based on the user's input. This code can be copied to the clipboard.

- Data Validation: The application provides a feature to validate data against an existing format. The Python code for the saved parser is stored in the Django database, and a view sends this code back to the front end. Users can validate their data via a sharable URL.


## Development
The application is built with Vue 3 and Django, and uses XState for state management and Pyodide to run Python in the browser.

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

### Run locally

    python backend/manage.py runserver

### Deploy
Check cloudformation.yaml for info on the deployment to aws us-east-1.