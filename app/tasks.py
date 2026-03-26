import os
import requests
import csv
from celery import shared_task
from .worker import celery_app

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 5))


@celery_app.task(name="master_fetch_task")
def master_fetch_task():
    url = "https://jsonplaceholder.typicode.com/users"
    users = requests.get(url).json()

    chunks = [users[i:i + CHUNK_SIZE] for i in range(0, len(users), CHUNK_SIZE)]

    with open("users_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "email"])

    # Запускаем дочерние задачи для каждой пачки
    for chunk in chunks:
        save_chunk_to_csv.delay(chunk)

    return f"Dispatched {len(chunks)} chunk tasks."


@celery_app.task(name="save_chunk_to_csv")
def save_chunk_to_csv(user_chunk):
    with open("users_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for user in user_chunk:
            writer.writerow([user['id'], user['name'], user['email']])
    return f"Saved {len(user_chunk)} users"