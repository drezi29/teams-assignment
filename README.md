# Team assignments

Team assignments app is a FastAPI-based web application that uses a PostgreSQL database for data storage. It allows to assign teams to experiment.

## Local Setup

Follow these steps to set up and run app locally:

### 1. Create a Python Virtual Environment

Create a new virtual environment using Python 3.10:

```bash
python3.10 -m venv venv/
```

### 2. Activate the Virtual Environment

Activate the newly created virtual environment:

```bash
source venv/bin/activate
```

### 3. Install requirements

Upgrade pip to the latest version:

```bash
pip install --upgrade pip
```

Install the required Python packages:

```bash 
pip install -r requirements.txt
```

### 4. Install PostgreSQL

Install and start PostgreSQL version 14 in your operating system.

For Mac:

* Install using Homebrew:

```bash
brew install postgresql@14
```

* Start the PostgreSQL service:

```bash
brew services start postgresql
```

For Windows:

* Download PostgreSQL Installer:

Go to the official PostgreSQL download page [https://www.postgresql.org/download/windows/] and download the installer for your version of Windows.

* Run the Installer:

Follow the prompts in the installer. It will guide you through the installation process, including setting up a database superuser and a password.

* Start PostgreSQL Service:

Press Win + R to open the Run dialog.
Type services.msc and press Enter.
Look for "PostgreSQL" in the list of services and ensure it is running.

### 5. Create a PostgreSQL Role and database

Open the PostgreSQL shell:

```bash
psql postgres
```

Then, create a new role named `fastapiapp` with login privileges and a password of `fastapiapp` and create 

```sql
CREATE ROLE fastapiapp WITH LOGIN PASSWORD 'fastapiapp';
ALTER ROLE fastapiapp CREATEDB;
CREATE DATABASE fastapiapp_db;
GRANT ALL PRIVILEGES ON DATABASE fastapiapp_db TO fastapiapp;
ALTER DATABASE fastapiapp_db OWNER TO fastapiapp;
```

### 6. Set Up Environment Variables

Create a .env file in the project root and add the following:
DATABASE_URL=postgresql://fastapiapp:fastapiapp@localhost/fastapiapp_db


### 7. Run the FastAPI Development Server

Start the FastAPI development server:

```bash
uvicorn src.main:app --reload
```
Now, you should be able to access the app application by navigating to [http://localhost:8000](http://localhost:8000) in your web browser.
