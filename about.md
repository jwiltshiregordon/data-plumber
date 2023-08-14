# DataPlumber.app

DataPlumber.app is a web application that helps users get their data flowing by providing a tool to specify data formats, generate parsers, and validate data against these formats. The application is built with Vue 3 and Django, and uses XState for state management and Pyodide to run Python in the browser.

## Features

- Local File Processing: Users can input a CSV file, which is processed locally in the browser. No data is uploaded to the server.

- Column Management: Users can add, remove, and select columns from their data. The details of each column are editable, and users can send the Python code for a column's parser to the code editor.

- Code Editor: The application includes a code editor where users can define new parsers or redefine existing parsers using Python. The code is run in the browser using Pyodide.

- Parser Generation: The application generates Python parser code based on the user's input. This code can be copied to the clipboard.

- Data Validation: The application provides a feature to validate data against an existing format. The Python code for the saved parser is stored in the Django database, and a view sends this code back to the front end. Users can validate their data via a sharable URL.

## Usage

1. Load your CSV file into the file input field.
2. Add, remove, or select columns from your data.
3. Edit the details of each column and send the Python code for the column's parser to the code editor.
4. Run the code in the editor to define new parsers or redefine existing parsers.
5. Generate a Python parser and get a sharable URL for others to validate their data.
6. You can also "edit" the parser after it's been shared. This actually just creates a new version and the old version will point to it saying "there's a newer version available"

## Development

This application is built with Vue 3 and Django. State management is handled with XState, and Python code is run in the browser using Pyodide.
