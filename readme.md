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

------

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

7. Run Migrator (optional)
```bash
python manage.py migrate_to_mongo
```

-----

Group Members

* Sofie Amalie Thorlund

* Viktor Mekis Bach

