# RPG Backend Project (MySQL + Django + MongoDB Migration)

<p align="center"> <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" /> <img src="https://img.shields.io/badge/Django-5.0-green?logo=django" /> <img src="https://img.shields.io/badge/REST%20API-DRF-red?logo=django" /> <img src="https://img.shields.io/badge/MySQL-Database-blue?logo=mysql" /> <img src="https://img.shields.io/badge/MongoDB-NoSQL-success?logo=mongodb" /> <img src="https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker" /> </p>

Created by: Sofie Thorlund and Viktor Bach

Course: Databases for Developers

## Overview

This project is an RPG (Role-Playing Game) backend system built as part of the Databases for Developers course.

It demonstrates:

* A fully designed relational SQL database (MySQL)

* A Django REST API providing CRUD operations for all RPG entities

* Authentication & Authorization (Token + JWT)

* API documentation using Swagger / OpenAPI

* A data migration tool that copies SQL data into MongoDB using Docker

* Use of triggers, events, views, stored procedures (inside SQL)

* ORM mapping and secure backend implementation

The system supports RPG gameplay logic such as characters, inventory, items, quests, skills, NPCs, battles, and transactions.

-------

## Project Structure

```bash
DB-project/
│
├── rpg_backend/          # Django project
│   ├── rpg/              # Django app containing models, views, serializers, etc.
│   │   ├── models/       # Character, Item, Skill, Quest, etc.
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           └── migrate_to_mongo.py   # SQL → MongoDB migrator
│   ├── admin.py
│   ├── apps.py
│   ├── permissions.py    # User permissions for authentication and authorization 
│   ├── settings.py
│   └── urls.py
│
├── SQL-scripts/          # DB schema, test data, stored procedures, triggers, events
├── venv
└── README.md
```

-------

## Architecture Diagram

```pgsql
                ┌───────────────────────────────┐
                │         REST Clients           │
                │ Postman / Browser / Swagger    │
                └───────────────┬───────────────┘
                                │
                     JSON over HTTP (CRUD)
                                │
                 ┌─────────────▼─────────────┐
                 │      Django Backend       │
                 │  DRF + Authentication     │
                 └─────────────┬─────────────┘
                      ORM      │       Migrator
                     (Read/Write)      │
                                │       │
                 ┌─────────────▼───────▼─────────────┐
                 │         MySQL (rpgdb)              │
                 │  Characters, Items, Quests, etc.   │
                 └─────────────────────────────────────┘
                                │
                                │  Copy data -> documents
                                ▼
                 ┌─────────────────────────────────────┐
                 │      MongoDB (Docker)               │
                 │  NoSQL collections per model        │
                 └─────────────────────────────────────┘
```

-------

## MySQL Database (Relational Model)

The project uses a MySQL database named rpgdb.
It was fully created manually using:

* Conceptual, Logical, Physical ERD

* SQL scripts

* Foreign keys & constraints

* Indexes

* Views

* Stored procedures & functions

 Triggers

* Events

* Test data generation

### Main RPG Tables

* users (Django auth users)

* rpg_character

* rpg_inventory

* rpg_item

* rpg_skill

* rpg_quest

* rpg_npc

* rpg_guild

* rpg_battle

* rpg_transaction

### Many-to-many relation tables

* rpg_character_skills

* rpg_character_quests

* rpg_character_battles

* rpg_inventory_items

### Advanced SQL Features Implemented

* Triggers for logging and automatic updates

* Views for summarizing game data

* Stored procedures for advanced operations

* Events for timed maintenance tasks

* This ensures a robust and realistic SQL system.

-------

## Django Backend

We implemented a Django REST framework backend that connects directly to MySQL using:

```makefile
ENGINE: mysql.connector.django
```
Django models map 1:1 to SQL tables.
CRUD operations, foreign keys, and M2M relations are exposed through REST API endpoints.

### Security Implemented

* Token Authentication

* JWT Authentication (djangorestframework-simplejwt)

* Custom permissions:

    * IsOwner

    * IsAdminOrReadOnly

-------

## Swagger / API Documentation

The project includes complete interactive documentation via Swagger UI using drf-yasg.

### Access Swagger

Start Django and visit:
```arduino
http://127.0.0.1:8000/swagger/
```

or:
```arduino
http://127.0.0.1:8000/redoc/
```

### Authentication in Swagger

Swagger supports:

* Token Authentication
```makefile
Authorization: Token <token>
```

* JWT Authentication
```makefile
Authorization: Bearer <access_token>
```

Use the Authorize button to authenticate and interact with protected endpoints.

### What Swagger Shows

* All API endpoints

* Request/response schemas

* Field descriptions

* * Authentication requirements

Models & relationships

* Try-it-out console

-------

### API Documentation

* Swagger / drf-yasg:

    * /swagger/

    * /redoc/

* Includes:

    * schemas

    * endpoint descriptions

    * authentication integration

-------

## REST API Endpoints (Examples)

Below is a summary of the main endpoint groups.

### Characters
```bash
GET     /api/characters/
POST    /api/characters/
GET     /api/characters/{id}/
PUT     /api/characters/{id}/
DELETE  /api/characters/{id}/
```

### Inventory
```bash
GET     /api/inventories/
POST    /api/inventories/
GET     /api/inventories/{id}/
PUT     /api/inventories/{id}/
PATCH   /api/inventories/{id}/
DELETE  /api/inventories/{id}/
```

### Items
```bash
GET     /api/items/
POST    /api/items/        (admin only)
GET     /api/items/{id}/
PUT     /api/items/{id}/   (admin only)
PATCH   /api/items/{id}/   (admin only)
DELETE  /api/items/{id}/   (admin only)
```

### Battles
```bash
GET     /api/battles/
POST    /api/battles/
GET     /api/battles/{id}/
PUT     /api/battles/{id}/
PATCH   /api/battles/{id}/
DELETE  /api/battles/{id}/
```

### Skills
```bash
GET     /api/skills/
POST    /api/skills/       (admin only)
GET     /api/skills/{id}/
PUT     /api/skills/{id}/  (admin only)
PATCH   /api/skills/{id}/  (admin only)
DELETE  /api/skills/{id}/  (admin only)
```

### Quests
```bash
GET     /api/quests/
POST    /api/quests/       (admin only)
GET     /api/quests/{id}/
PUT     /api/quests/{id}/  (admin only)
PATCH   /api/quests/{id}/  (admin only)
DELETE  /api/quests/{id}/  (admin only)
```

### NPCs
```bash
GET     /api/npcs/
POST    /api/npcs/         (admin only)
GET     /api/npcs/{id}/
PUT     /api/npcs/{id}/    (admin only)
PATCH   /api/npcs/{id}/    (admin only)
DELETE  /api/npcs/{id}/    (admin only)
```

### Guilds
```bash
GET     /api/guilds/
POST    /api/guilds/       (admin only)
GET     /api/guilds/{id}/
PUT     /api/guilds/{id}/  (admin only)
PATCH   /api/guilds/{id}/  (admin only)
DELETE  /api/guilds/{id}/  (admin only)
```

### Transactions
```bash
GET     /api/transactions/
POST    /api/transactions/
GET     /api/transactions/{id}/
PUT     /api/transactions/{id}/
PATCH   /api/transactions/{id}/
DELETE  /api/transactions/{id}/
```

All endpoints require authentication unless read-only.

-----

## Neo4j Graph Database API

The project includes a complete CRUD API for the Neo4j graph database, matching the MongoDB implementation pattern.

### Neo4j API Endpoints

All Neo4j endpoints follow the pattern: `/api/neo4j/{resource}/`

#### Characters
```bash
GET     /api/neo4j/characters/
POST    /api/neo4j/characters/
GET     /api/neo4j/characters/{id}/
PUT     /api/neo4j/characters/{id}/
DELETE  /api/neo4j/characters/{id}/
```

#### Items
```bash
GET     /api/neo4j/items/
POST    /api/neo4j/items/
GET     /api/neo4j/items/{id}/
PUT     /api/neo4j/items/{id}/
DELETE  /api/neo4j/items/{id}/
```

#### Skills
```bash
GET     /api/neo4j/skills/
POST    /api/neo4j/skills/
GET     /api/neo4j/skills/{id}/
PUT     /api/neo4j/skills/{id}/
DELETE  /api/neo4j/skills/{id}/
```

#### Quests
```bash
GET     /api/neo4j/quests/
POST    /api/neo4j/quests/
GET     /api/neo4j/quests/{id}/
PUT     /api/neo4j/quests/{id}/
DELETE  /api/neo4j/quests/{id}/
```

#### Guilds
```bash
GET     /api/neo4j/guilds/
POST    /api/neo4j/guilds/
GET     /api/neo4j/guilds/{id}/
PUT     /api/neo4j/guilds/{id}/
DELETE  /api/neo4j/guilds/{id}/
```

#### NPCs
```bash
GET     /api/neo4j/npcs/
POST    /api/neo4j/npcs/
GET     /api/neo4j/npcs/{id}/
PUT     /api/neo4j/npcs/{id}/
DELETE  /api/neo4j/npcs/{id}/
```

#### Battles
```bash
GET     /api/neo4j/battles/
POST    /api/neo4j/battles/
GET     /api/neo4j/battles/{id}/
PUT     /api/neo4j/battles/{id}/
DELETE  /api/neo4j/battles/{id}/
```

#### Transactions
```bash
GET     /api/neo4j/transactions/
POST    /api/neo4j/transactions/
GET     /api/neo4j/transactions/{id}/
PUT     /api/neo4j/transactions/{id}/
DELETE  /api/neo4j/transactions/{id}/
```

#### Users
```bash
GET     /api/neo4j/users/
GET     /api/neo4j/users/{id}/
```

### Neo4j API Features

* **Graph relationships**: GET requests include related data (e.g., characters return their user, guild, skills, quests)
* **Cypher queries**: All operations use optimized Cypher queries
* **Automatic ID generation**: POST requests auto-increment IDs
* **Relationship management**: Creating entities automatically creates relationships if foreign keys are provided
* **No authentication required**: All endpoints are public (matching MongoDB implementation)

### Example Usage

Get all characters with relationships:
```bash
curl http://localhost:8000/api/neo4j/characters/
```

Create a new character:
```bash
curl -X POST http://localhost:8000/api/neo4j/characters/ \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Thorin",
    "level": 10,
    "hp": 200,
    "mana": 100,
    "user_id": 1,
    "guild_id": 2
  }'
```

Update a character:
```bash
curl -X PUT http://localhost:8000/api/neo4j/characters/1/ \
  -H "Content-Type: application/json" \
  -d '{"level": 15, "hp": 250}'
```

-----

## SQL → MongoDB Migration Tool

As required in Assignment 2, we created a migrator app using a Django management command.
This tool automatically copies all data from MySQL into MongoDB.

### How It Works

* Fetches all RPG models dynamically

* Reads SQL rows using Django ORM

* Connects to MongoDB using pymongo

* Converts:

    * Foreign keys → integers

    * ManyToMany → lists

* Writes each model to a separate MongoDB collection

* Does not modify the SQL database

### Location
```swift
rpg_backend/rpg/management/commands/migrate_to_mongo.py
```

### Run MongoDB in Docker
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongo-data:/data/db \
  mongo:6.0
```

### Run the Migrator
```bash
python manage.py migrate_to_mongo
```

### Result

MongoDB database: rpg_mongo
Collections:
* item
* inventory
* guild
* npc
* skill
* quest
* character
* battle
* transaction

-------

## Testing with MongoDB Compass

1. Install Compass: https://www.mongodb.com/try/download/compass

2. Connect using:
```arduino
mongodb://localhost:27017
```

3. Select database rpg_mongo

4. Browse all migrated collections

-------

## SQL → Neo4j Migration Tool

As an alternative to MongoDB, we also created a Neo4j graph database migrator.
This tool copies all data from MySQL into Neo4j as nodes and relationships.

### How It Works

* Fetches all RPG models dynamically

* Reads SQL rows using Django ORM

* Connects to Neo4j using the neo4j driver

* Converts:

    * SQL rows → graph nodes (labeled by model name)

    * Foreign keys → directed relationships

    * ManyToMany → directed relationships

* Creates nodes and relationships without modifying the SQL database

### Location
```swift
rpg_backend/rpg/management/commands/migrate_to_neo4j.py
```

### Run Neo4j in Docker

Start Neo4j with a custom password:
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password_here \
  neo4j:5.10
```

Replace `your_password_here` with a secure password. This will be your login credentials.

Inspect:
```bash
docker ps
```

View logs (to confirm startup):
```bash
docker logs neo4j
```

### Run the Migrator

Set environment variables:
```bash
export NEO4J_URI='bolt://localhost:7687'
export NEO4J_USER='neo4j'
export NEO4J_PASSWORD='your_password_here'
```

Then run:
```bash
python manage.py migrate_to_neo4j
```

### Result

Neo4j database will contain nodes for:

* Character

* Item

* Skill

* Quest

* NPC

* Guild

* Battle

* Transaction

* User

With relationships between them:

* `Character -[:USER]-> User`

* `Character -[:GUILD]-> Guild`

* `Character -[:SKILLS]-> Skill` (M2M)

* `Character -[:QUESTS]-> Quest` (M2M)

* `Battle -[:CHARACTER]-> Character`

* `Quest -[:NPC]-> NPC`

* And more based on your data model

-------

## Accessing Neo4j Browser

1. Open your browser and navigate to:
```
http://localhost:7474
```

2. Login with:
   * Username: `neo4j`
   * Password: `your_password_here` (the one you set in the Docker ENV)

3. Run example queries to explore the graph:

```cypher
// View all nodes
MATCH (n) RETURN n LIMIT 20

// Find all characters and their skills
MATCH (c:Character)-[:SKILLS]->(s:Skill) 
RETURN c.character_name, s.name

// Find character's guild
MATCH (c:Character)-[:GUILD]->(g:Guild) 
RETURN c.character_name, g.guild_name

// View all relationship types
MATCH ()-[r]->() 
RETURN type(r), count(*) 
ORDER BY count(*) DESC

// Find a specific character and related data
MATCH (c:Character {character_name: 'Aelric'})
MATCH (c)-[r]->(related)
RETURN c, type(r), related
```

4. Stop Neo4j when done:
```bash
docker stop neo4j
```

5. Restart later:
```bash
docker start neo4j
```

6. Remove container completely:
```bash
docker rm neo4j
```

-------

## Running MongoDB via Docker (Required)

Start MongoDB:
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongo-data:/data/db \
  mongo:6.0
```

Inspect:
```bash
docker ps
```

Stop/start:
```bash
docker stop mongodb
docker start mongodb
```

### Run the Migrator
```bash
python manage.py migrate_to_mongo
```

MongoDB will now contain:

* character

* item

* inventory

* quest

* npc

* guild

* skill

* battle

* transaction

-------

## Installation Instructions
1. Clone repository
```bash
git clone <repo-url>
cd DB-project
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run MySQL server

(Create database & import SQL scripts)

5. Run MongoDB (Docker)
```bash
docker run -d --name mongodb -p 27017:27017 -v mongo-data:/data/db mongo:6.0
```

6. Start Django server
```bash
python manage.py runserver
```

7. Run Migrator 
```bash
python manage.py migrate_to_mongo
```

-----

Group Members

* Sofie Amalie Thorlund

* Viktor Mekis Bach

