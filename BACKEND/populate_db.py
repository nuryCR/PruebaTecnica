import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker
import random

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="tasks_bd",
            user="postgres",
            password="123",  # Reemplázalo con tu contraseña real
            host="localhost",
            port="5435",
            options="-c client_encoding=UTF8",
            cursor_factory=RealDictCursor
        )
        logger.info("Connection to database established successfully.")
        return connection
    except Exception as error:
        logger.error(f"Error connecting to database: {error}")
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {error}")

def create_tables():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) CHECK (status IN ('pending', 'in progress', 'completed')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    user_id INT REFERENCES users(user_id) ON DELETE CASCADE
                );
            """)
            conn.commit()
            logger.info("Tables created successfully.")
    except Exception as error:
        conn.rollback()
        logger.error(f"Error creating tables: {error}")
        raise HTTPException(status_code=500, detail=f"Error creating tables: {error}")
    finally:
        conn.close()

# Insertar datos falsos
def insert_fake_data():
    conn = connect_to_db()
    fake = Faker('es_ES')  
    try:
        with conn.cursor() as cursor:
            # Insertar usuarios falsos
            for _ in range(5): 
                name = fake.name()
                cursor.execute("INSERT INTO users (name) VALUES (%s) RETURNING user_id;", (name,))
                user_id = cursor.fetchone()["user_id"]
                logger.info(f"🟢 Usuario creado: {name} (ID: {user_id})")

            # Insertar tareas falsas
            cursor.execute("SELECT user_id FROM users;")
            users = cursor.fetchall()
            user_ids = [u["user_id"] for u in users]
            statuses = ["pending", "in progress", "completed"]

            for _ in range(10):  # Insertar 10 tareas
                title = fake.sentence(nb_words=4)
                description = fake.paragraph()
                status = random.choice(statuses)
                user_id = random.choice(user_ids)

                cursor.execute(
                    "INSERT INTO tasks (title, description, status, user_id) VALUES (%s, %s, %s, %s);",
                    (title, description, status, user_id)
                )
                logger.info(f"📝 Tarea creada: {title} (Estado: {status}, Usuario: {user_id})")

            conn.commit()
            logger.info("✅ Datos falsos insertados correctamente.")
    except Exception as error:
        conn.rollback()
        logger.error(f"Error inserting fake data: {error}")
        raise HTTPException(status_code=500, detail=f"Error inserting fake data: {error}")
    finally:
        conn.close()

@app.on_event("startup")
def startup_event():
    create_tables()
    insert_fake_data()  

# Modelos Pydantic
class User(BaseModel):
    user_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True 

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str = Field("pending", pattern="^(pending|in progress|completed)$")
    created_at: datetime
    user_id: int  # Relación con User

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = Field("pending", pattern="^(pending|in progress|completed)$")
    user_id: int

# Endpoints
@app.get("/connect")
def connect():
    logger.info("Attempting to connect to the database.")
    conn = connect_to_db()
    if conn:
        conn.close()
        logger.info("Connection to database closed successfully.")
        return {"message": "Connection to database established successfully."}
    else:
        logger.error("Error connecting to database.")
        return {"message": "Error connecting to database."}

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application"}

@app.get("/users", response_model=List[User])
def get_users():
    logger.info("Fetching users from the database.")
    conn = connect_to_db()
    if not conn:
        logger.error("Database connection failed.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, name, created_at FROM users;")
            users = cursor.fetchall()
            logger.info(f"Fetched {len(users)} users.")
        return users
    finally:
        conn.close()

@app.get("/tasks", response_model=List[Task])
def get_tasks(user_id: Optional[int] = None):
    logger.info(f"Fetching tasks from the database for user_id: {user_id}.")
    conn = connect_to_db()
    if not conn:
        logger.error("Database connection failed.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT id, title, description, status, created_at, user_id FROM tasks WHERE user_id = %s;", (user_id,))
            else:
                cursor.execute("SELECT id, title, description, status, created_at, user_id FROM tasks;")
            tasks = cursor.fetchall()
            logger.info(f"Fetched {len(tasks)} tasks.")
        return tasks
    finally:
        conn.close()

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    logger.info(f"Creating a new task with title: {task.title}.")
    conn = connect_to_db()
    if not conn:
        logger.error("Database connection failed.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description, status, user_id, created_at) VALUES (%s, %s, %s, %s, NOW()) RETURNING id, title, description, status, created_at, user_id;",
                (task.title, task.description, task.status, task.user_id),
            )
            new_task = cursor.fetchone()
            conn.commit()
            logger.info(f"New task created: {new_task}")
        return new_task
    except Exception as error:
        conn.rollback()  
        logger.error(f"Error during task creation: {error}")
        raise HTTPException(status_code=500, detail="Error creating task")
    finally:
        conn.close()

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    logger.info(f"Updating task with id: {task_id}.")
    conn = connect_to_db()
    if not conn:
        logger.error("Database connection failed.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks SET title = %s, description = %s, status = %s WHERE id = %s RETURNING id, title, description, status, created_at, user_id;",
                (task.title, task.description, task.status, task_id),
            )
            updated_task = cursor.fetchone()
            conn.commit()
            logger.info(f"Task updated: {updated_task}")
        if not updated_task:
            logger.warning(f"Task with id {task_id} not found.")
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except Exception as error:
        conn.rollback() 
        logger.error(f"Error during task update: {error}")
        raise HTTPException(status_code=500, detail="Error updating task")
    finally:
        conn.close()

@app.get("/{path_name}")
def read_any(path_name: str):
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)