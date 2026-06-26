# all-jar-guess-the-word-cli

## Required Python version

python 3.14.6

If `pipenv` shows not found run `pyenv global 3.14.6` to set your global python version to the correct one.

## Dependency Installation and setup

```Bash
pipenv install --dev
pipenv shell
```

## Bash Scripting Wurdal Command

Add this line to your ```~/.zshrc``` file.
```export PATH=$PATH:~/path/to/workspace/all-jar-guess-the-word-cli/bin```
Then open a new terminal and you should be good to run the cmd.

## CLI run command

cd into src of the project before running.
`wurdal <cmd>`

## API Development Commands

### Set up location of database

- create a file called `.env` in the root of your project
- add the following: ```DATABASE_URL=postgresql+psycopg://localhost/players```

### Start the development server

```bash
pipenv run dev
```

Runs the FastAPI app with uvicorn on http://localhost:8000

### Run database migrations

```bash
pipenv run alembic upgrade head
```

Apply pending database migrations

### Create a new migration

```bash
pipenv run alembic revision --autogenerate -m "description"
```

Generate a new migration file based on model changes

### Run tests

```bash
pipenv run pytest
```

Run your test suite

### View API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
