#!/usr/bin/env python3
"""
Простой скрипт для настройки Keycloak
"""
import requests
import json
import time

KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Получить токен администратора"""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "username": ADMIN_USER,
        "password": ADMIN_PASSWORD,
        "grant_type": "password",
        "client_id": "admin-cli"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Ошибка получения токена: {response.status_code} - {response.text}")
        return None

def create_realm(token):
    """Создать realm 'soc'"""
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "realm": "soc-portal",
        "enabled": True,
        "displayName": "SOC Portal"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ Realm 'socsoc-portal' создан успешно")
        return True
    elif response.status_code == 409:
        print("ℹ️ Realm 'soc-portal' уже существует")
        return True
    else:
        print(f"❌ Ошибка создания realm: {response.status_code} - {response.text}")
        return False

def create_client(token):
    """Создать client 'soc-portal'"""
    url = f"{KEYCLOAK_URL}/admin/realms/soc-portal/clients"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "clientId": "soc-portal",
        "enabled": True,
        "publicClient": True,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": True,
        "serviceAccountsEnabled": True,
        "redirectUris": ["http://localhost:3000/*", "http://localhost:5173/*"],
        "webOrigins": ["http://localhost:3000", "http://localhost:5173"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ Client 'soc-portal' создан успешно")
        return True
    elif response.status_code == 409:
        print("ℹ️ Client 'soc-portal' уже существует")
        return True
    else:
        print(f"❌ Ошибка создания client: {response.status_code} - {response.text}")
        return False

def create_user(token):
    """Создать тестового пользователя"""
    url = f"{KEYCLOAK_URL}/admin/realms/soc-portal/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "username": "testuser",
        "enabled": True,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "credentials": [{
            "type": "password",
            "value": "testpass123",
            "temporary": False
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ Тестовый пользователь создан успешно")
        return True
    elif response.status_code == 409:
        print("ℹ️ Тестовый пользователь уже существует")
        return True
    else:
        print(f"❌ Ошибка создания пользователя: {response.status_code} - {response.text}")
        return False

def main():
    print("🚀 Настройка Keycloak...")
    
    # Ждем пока Keycloak запустится
    print("⏳ Ожидание запуска Keycloak...")
    for i in range(30):
        try:
            response = requests.get(f"{KEYCLOAK_URL}/")
            if response.status_code == 200:
                break
        except:
            pass
        time.sleep(2)
        print(f"   Попытка {i+1}/30...")
    else:
        print("❌ Keycloak не запустился за 60 секунд")
        return
    
    print("✅ Keycloak запущен")
    
    # Получаем токен администратора
    print("🔑 Получение токена администратора...")
    token = get_admin_token()
    if not token:
        return
    
    print("✅ Токен получен")
    
    # Создаем realm
    print("🏰 Создание realm...")
    if not create_realm(token):
        return
    
    # Создаем client
    print("🔧 Создание client...")
    if not create_client(token):
        return
    
    # Создаем пользователя
    print("👤 Создание тестового пользователя...")
    if not create_user(token):
        return
    
    print("\n🎉 Настройка Keycloak завершена!")
    print("\n📋 Информация для входа:")
    print("   URL: http://localhost:8080")
    print("   Realm: soc-portal")
    print("   Client: soc-portal")
    print("   Тестовый пользователь: testuser / testpass123")
    print("   Админ: admin / admin123")

if __name__ == "__main__":
    main()
