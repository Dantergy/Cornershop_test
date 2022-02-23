# ETL and API project
## Requirements
- Python 3.9
- Pip
- Heroku
- Docker

## Setup
### Credentials
First it's necessary to create a file called `credentials.py` in the main folder with the following information:
```
GRAND_TYPE = "client_credentials"
CLIENT_ID = "mRkZGFjM"
CLIENT_SECRET = "ZGVmMjMz"
BASE_URL = "LINK_TO_HEROKU_SERVER"
```
### Virtual VENV
Create a Python VirtualEnv and use` requirements.txt` to install the required libraries
```
pip install -r requirements.txt
```
### Server
To configure the server, please follow the instructions in the` Readme.md` inside `integration-skill-test-server-master`

## Running the project
Run the file `main.py` to start the ETL process.
```
python main.py
```

### Unit testing
The ETL process has unit tests using the `Pytest` python library, use the following command to run them:
```
pytest
```
