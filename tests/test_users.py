from app import oauth2, models, rate_limit, config
from fastapi import Request
import os


def test_create_user(client):
    response = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@gmail.com"

def test_create_user_duplicate_email(client):

    response1 = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response1.status_code == 201  

    response2 = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response2.status_code == 409  

def test_login(client):

    response1 = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response1.status_code == 201 

    response2 = client.post("/login", data={
        "username": "test@gmail.com",
        "password": "test123"
    })
    assert response2.status_code == 403 

from app import oauth2

def test_verify_email(client, session):
    config.settings.rate_limit_requests = 1000
    response1 = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response1.status_code == 201

    token = oauth2.create_verification_token("test@gmail.com")

    response2 = client.get(f"/users/verify/{token}")

    assert response2.status_code == 200
    user = session.query(models.User).filter(models.User.email == "test@gmail.com").first()
    assert user.is_verified == True

def test_save_password(client):
    config.settings.rate_limit_requests = 1000
    response1 = client.post("/users/", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response1.status_code == 201

    token = oauth2.create_verification_token("test@gmail.com")

    response2 = client.get(f"/users/verify/{token}")

    assert response2.status_code == 200

    response3 = client.post("/login", data={
        "username": "test@gmail.com",
        "password": "test123"
    })
    assert response3.status_code == 200
    login_token = response3.json()["access_token"]

    response4 = client.post("/vault", json={
    "platform": "prod 1",
    "website_URL": "www.demo.com",
    "platform_username": "kumailx@gmail.com",
    "platform_password": "test12134"
    }, headers = {
         "Authorization": f"Bearer {login_token}"
    })

    assert response4.status_code == 201
    






    