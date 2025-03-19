## Fastapi middleware/backend component

- Leverages DMART as the backend data store.
- Access to DMART api is made with privileged user defined on the backend component
- Declares own initial set of apis to register/create user and login/logout with forgot/reset password


## Installation
- clone the repo
- cd to the project folder
- `pip install -r requirements.txt`
- On Dmart service
- - To deal with the new `spaces` folder by updating `SPACES_FOLDER` env var in Dmart itself
- - If the `active_data_db=file` then recreate Redis DB by calling `./create_index.py --flushall`
- - If the `active_data_db=sql` then perform migration by calling `./data_adapters/sql/json_to_db_migration.py`
- - [Optional] run Dmart tests to make sure everything configured successfully `cd tests && pytest`
- create the logs folder `mkdir ../logs`
- run the server `./main.py`