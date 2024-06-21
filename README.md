# Team assignments

Team assignments app is a FastAPI-based web application that uses a PostgreSQL database for data storage. It allows to assign teams to experiment.

## Setup

### Run with Docker
<details>
<summary>Follow these steps to set up and run app with Docker</summary>

#### 1. Install Docker and Docker Compose

To run this app, you will need to install Docker and Docker Compose.

Install Docker Desktop for your OS <https://www.docker.com/products/docker-desktop/>

Follow the installation instructions and start Docker Desktop.

#### 2. Clone the repository

Clone the repository to your local machine:

```bash
git clone https://github.com/drezi29/teams-assignment.git
cd team-assignment
```

#### 3. Create Environment Variables file

Create a .env file in the project root and add the following:

```plaintext
DATABASE_URL=postgresql://fastapiapp:fastapiapp@db:5432/fastapiapp_db
TEST_DATABASE_URL = "postgresql://fastapiapp:fastapiapp@db:5432/fastapiapp_test"
POSTGRES_USER=fastapiapp
POSTGRES_PASSWORD=fastapiapp
POSTGRES_DB=fastapiapp_db
```

#### 4. Build and run the Docker containers

Use Docker Compose to build the Docker images and run the containers:

```bash
docker-compose up --build
```

#### 5. Access the application

Now, you should be able to access the application by navigating to http://localhost:8000 in your web browser.

#### 6. (Optional) Stopping the containers and remove volumes

If you need to stop the containers, you can use the following command:

```bash
docker-compose down
```

This command will stop and remove the containers, but the data in the PostgreSQL volume will persist. If you want to remove the volumes as well (e.g., to start fresh), you can use this command insted above one:

```bash
docker-compose down -v
```

</details>

### Setup with local database and development server 

<details>
<summary>Follow these steps to set up and run app locally</summary>

#### 1. Create a Python Virtual Environment

Create a new virtual environment using Python 3.10:

```bash
python3.10 -m venv venv/
```

#### 2. Activate the Virtual Environment

Activate the newly created virtual environment:

```bash
source venv/bin/activate
```

#### 3. Install requirements

Upgrade pip to the latest version:

```bash
pip install --upgrade pip
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

#### 4. Install PostgreSQL

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

#### 5. Create a PostgreSQL Role and database

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

#### 6. Set Up Environment Variables

Create a .env file in the project root and add the following:
DATABASE_URL=postgresql://fastapiapp:fastapiapp@localhost/fastapiapp_db


#### 7. Run the FastAPI Development Server

Start the FastAPI development server:

```bash
uvicorn src.main:app --reload
```
Now, you should be able to access the app application by navigating to [http://localhost:8000](http://localhost:8000) in your web browser.
</details>