#!/usr/bin/env python3
"""
Скрипт для исправления настроек пользователя в Keycloak
"""
import requests
import json

# Настройки Keycloak
KC_BASE_URL = "http://localhost:8080"
KC_ADMIN_USER = "admin"
KC_ADMIN_PASSWORD = "admin123"
REALM_NAME = "soc"
USERNAME = "testuser"

def get_admin_token():
    """Получаем токен администратора"""
    url = f"{KC_BASE_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "username": KC_ADMIN_USER,
        "password": KC_ADMIN_PASSWORD,
        "grant_type": "password",
        "client_id": "admin-cli"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Ошибка получения токена: {response.text}")

def fix_user(token):
    """Исправляем настройки пользователя"""
    # Получаем ID пользователя
    url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users?username={USERNAME}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка поиска пользователя: {response.text}")
        return
    
    users = response.json()
    if not users:
        print(f"Пользователь {USERNAME} не найден")
        return
    
    user_id = users[0]["id"]
    print(f"Найден пользователь {USERNAME} с ID: {user_id}")
    
    # Обновляем настройки пользователя
    update_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
    user_data = {
        "emailVerified": True,
        "enabled": True,
        "email": "test@example.com"
    }
    
    update_response = requests.put(update_url, headers=headers, json=user_data)
    if update_response.status_code == 204:
        print("Настройки пользователя обновлены")
    else:
        print(f"Ошибка обновления пользователя: {update_response.text}")
    
    # Сбрасываем пароль
    password_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}/reset-password"
    password_data = {
        "type": "password",
        "value": "testpass123",
        "temporary": False
    }
    
    password_response = requests.put(password_url, headers=headers, json=password_data)
    if password_response.status_code == 204:
        print("Пароль пользователя сброшен")
    else:
        print(f"Ошибка сброса пароля: {password_response.text}")

def main():
    """Основная функция"""
    print("Исправление настроек пользователя в Keycloak...")
    
    try:
        token = get_admin_token()
        print("Токен администратора получен")
        
        fix_user(token)
        
        print("\nИсправление завершено!")
        print("Попробуйте войти снова: testuser / testpass123")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
