#!/usr/bin/env python3
"""
Полный скрипт для исправления всех настроек пользователя в Keycloak
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

def delete_and_recreate_user(token):
    """Удаляем и пересоздаем пользователя"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Ищем существующего пользователя
    search_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users?username={USERNAME}"
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        if users:
            user_id = users[0]["id"]
            print(f"Удаляем существующего пользователя {USERNAME} с ID: {user_id}")
            
            # Удаляем пользователя
            delete_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            if delete_response.status_code == 204:
                print("Пользователь удален")
            else:
                print(f"Ошибка удаления пользователя: {delete_response.text}")
    
    # Создаем нового пользователя
    create_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users"
    user_data = {
        "username": USERNAME,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {
                "type": "password",
                "value": "testpass123",
                "temporary": False
            }
        ],
        "requiredActions": []  # Убираем все обязательные действия
    }
    
    create_response = requests.post(create_url, headers=headers, json=user_data)
    if create_response.status_code == 201:
        print(f"Пользователь {USERNAME} создан заново")
        
        # Получаем ID нового пользователя
        search_response = requests.get(search_url, headers=headers)
        if search_response.status_code == 200:
            users = search_response.json()
            if users:
                user_id = users[0]["id"]
                print(f"ID нового пользователя: {user_id}")
                
                # Назначаем роль user
                role_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/roles/user"
                role_response = requests.get(role_url, headers=headers)
                if role_response.status_code == 200:
                    role = role_response.json()
                    assign_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm"
                    assign_response = requests.post(assign_url, headers=headers, json=[role])
                    if assign_response.status_code == 204:
                        print("Роль 'user' назначена")
                    else:
                        print(f"Ошибка назначения роли: {assign_response.text}")
                
                # Дополнительно обновляем настройки
                update_url = f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
                update_data = {
                    "emailVerified": True,
                    "enabled": True,
                    "requiredActions": []
                }
                update_response = requests.put(update_url, headers=headers, json=update_data)
                if update_response.status_code == 204:
                    print("Дополнительные настройки применены")
                else:
                    print(f"Ошибка обновления настроек: {update_response.text}")
    else:
        print(f"Ошибка создания пользователя: {create_response.text}")

def main():
    """Основная функция"""
    print("Полное исправление пользователя в Keycloak...")
    
    try:
        token = get_admin_token()
        print("Токен администратора получен")
        
        delete_and_recreate_user(token)
        
        print("\nИсправление завершено!")
        print("Попробуйте войти снова: testuser / testpass123")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
