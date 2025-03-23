# How to Run the Project

Before the start make sure to adjust the following:
1. Make the following command and populate it with required data:
   ```bash
   cp .env.sample .env
   ```
2. _Optional_

   SQLAlchemy can try to connect to a PostgreSQL database using a user/role called `dispatch`, so create the dispatch role manually:
   ```bash
   psql -u postgres
   CREATE ROLE dispatch WITH LOGIN PASSWORD '<password>' ;
   ```
   Then run [update-example-data.sh](data%2Fupdate-example-data.sh)

## Required settings

1. **Set up a Python virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install project dependencies**:
   ```bash
   pip install -r requirements-base.txt
   ```
---

## Manually Running the Project

**Start the FastAPI application**:
   ```bash
   uvicorn src.dispatch.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be accessible at [http://0.0.0.0:8000/api/v1/docs](http://0.0.0.0:8000/api/v1/docs).

---

## Run project with PyCharm

1. Mark the `src` directory as root
2. Close all open code tabs
3. Restart `PyCharm`
4. Create a new Run Configuration
   - you can create a `FastAPI` configuration
   ![fastapi_configuration.png](assets%2Ffastapi_configuration.png)
   - or you can create a `Python` configuration
   ![python_configuration.png](assets%2Fpython_configuration.png)
5. Run the project via `PyCharm` and use breakpoints for debugging
   The API will be accessible at [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs).
