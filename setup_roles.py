#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки ролей и тест-пользователей в Keycloak (только admin/analyst/manager/client)
а также для обновления клиента soc-portal (redirectUris, webOrigins, PKCE).

Запуск:
    python setup_roles.py
"""

import requests

# ===== НАСТРОЙКИ =====
KC_BASE_URL = "http://localhost:8080"
KC_ADMIN_USER = "admin"
KC_ADMIN_PASSWORD = "admin123"

REALM_NAME = "soc-portal"
CLIENT_ID = "soc-portal"

# Проекты/окружения: локалка и сервер по IP (как у тебя)
REDIRECT_URIS = [
    # prod / облако
    "http://5.63.120.30/*",
    "http://5.63.120.30",
    "http://5.63.120.30/auth/callback",
    # local dev
    "http://localhost:3000/*",
    "http://localhost:3000",
    "http://localhost:5173/*",
    "http://localhost:5173",
    "http://localhost:3000/auth/callback",
    "http://localhost:5173/auth/callback",
]

WEB_ORIGINS = [
    "http://5.63.120.30",
    "http://localhost:3000",
    "http://localhost:5173",
]

# Роли — только те, что ты попросил
ROLES = [
    {"name": "admin",   "description": "Администратор — полный доступ"},
    {"name": "analyst", "description": "Аналитик SOC — инциденты/тикеты/отчёты"},
    {"name": "manager", "description": "Менеджер — обзор/отчёты/чтение"},
    {"name": "client",  "description": "Клиент — свои инциденты/тикеты"},
]

# Тест-пользователи под каждую роль
TEST_USERS = [
    {"username": "admin",   "email": "admin@example.com",   "firstName": "Admin",   "lastName": "User",   "password": "admin123",   "role": "admin"},
    {"username": "analyst", "email": "analyst@example.com", "firstName": "SOC",     "lastName": "Analyst","password": "analyst123", "role": "analyst"},
    {"username": "manager", "email": "manager@example.com", "firstName": "Manager", "lastName": "User",   "password": "manager123", "role": "manager"},
    {"username": "client",  "email": "client@example.com",  "firstName": "Client",  "lastName": "User",   "password": "client123",  "role": "client"},
]


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_admin_token() -> str:
    """Получаем токен администратора master-realm."""
    url = f"{KC_BASE_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "username": KC_ADMIN_USER,
        "password": KC_ADMIN_PASSWORD,
        "grant_type": "password",
        "client_id": "admin-cli",
    }
    r = requests.post(url, data=data, timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]


def ensure_client(token: str):
    """Создаём/обновляем OIDC-клиент soc-portal (public, PKCE, redirect/webOrigins)."""
    h = _headers(token)

    # Пытаемся найти клиента по clientId
    r = requests.get(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/clients?clientId={CLIENT_ID}",
        headers=h, timeout=20
    )
    r.raise_for_status()
    items = r.json()

    body = {
        "clientId": CLIENT_ID,
        "protocol": "openid-connect",
        "enabled": True,
        "publicClient": True,
        "standardFlowEnabled": True,         # Authorization Code + PKCE
        "directAccessGrantsEnabled": False,  # ROPC выключен для SPA
        "serviceAccountsEnabled": False,
        "redirectUris": sorted(set(REDIRECT_URIS)),
        "webOrigins": sorted(set(WEB_ORIGINS)),
        "attributes": {
            "pkce.code.challenge.method": "S256",
        },
    }

    if items:
        client_id_internal = items[0]["id"]
        u = requests.put(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/clients/{client_id_internal}",
            headers=h, json=body, timeout=20
        )
        if u.status_code in (204, 201):
            print("♻️  Клиент soc-portal обновлён")
        else:
            raise RuntimeError(f"Ошибка обновления клиента: {u.status_code} {u.text}")
    else:
        c = requests.post(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/clients",
            headers=h, json=body, timeout=20
        )
        if c.status_code == 201:
            print("✅ Клиент soc-portal создан")
        elif c.status_code == 409:
            print("ℹ️  Клиент soc-portal уже существует (гонка) — ок")
        else:
            raise RuntimeError(f"Ошибка создания клиента: {c.status_code} {c.text}")


def ensure_roles(token: str):
    """Создаём роли (idempotent)."""
    h = _headers(token)
    for role in ROLES:
        r = requests.post(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/roles",
            headers=h, json=role, timeout=20
        )
        if r.status_code == 201:
            print(f"✅ Роль '{role['name']}' создана")
        elif r.status_code == 409:
            print(f"ℹ️  Роль '{role['name']}' уже существует")
        else:
            raise RuntimeError(f"Ошибка создания роли '{role['name']}': {r.status_code} {r.text}")


def get_realm_role(token: str, role_name: str) -> dict:
    """Возвращает JSON роли realm’а."""
    h = _headers(token)
    r = requests.get(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/roles/{role_name}",
        headers=h, timeout=20
    )
    r.raise_for_status()
    return r.json()


def get_or_create_user(token: str, username: str, email: str, first: str, last: str, password: str) -> str:
    """Ищем пользователя, иначе создаём. Возвращаем user_id."""
    h = _headers(token)
    # поиск
    s = requests.get(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users?username={username}",
        headers=h, timeout=20
    )
    s.raise_for_status()
    items = s.json()
    if items:
        user_id = items[0]["id"]
        # синхронизируем основные поля
        u = requests.put(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}",
            headers=h,
            json={"email": email, "firstName": first, "lastName": last, "enabled": True, "emailVerified": True},
            timeout=20
        )
        if u.status_code not in (204, 201):
            raise RuntimeError(f"Ошибка обновления пользователя {username}: {u.status_code} {u.text}")
    else:
        # создаём
        c = requests.post(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users",
            headers=h,
            json={
                "username": username,
                "email": email,
                "firstName": first,
                "lastName": last,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": password, "temporary": False}],
                "requiredActions": []
            },
            timeout=20
        )
        if c.status_code not in (201, 409):
            raise RuntimeError(f"Ошибка создания пользователя {username}: {c.status_code} {c.text}")
        # повторный поиск для получения id
        s2 = requests.get(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users?username={username}",
            headers=h, timeout=20
        )
        s2.raise_for_status()
        items = s2.json()
        if not items:
            raise RuntimeError(f"Не удалось получить id пользователя {username} после создания")
        user_id = items[0]["id"]

    # сброс пароля (на всякий)
    rp = requests.put(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}/reset-password",
        headers=h,
        json={"type": "password", "value": password, "temporary": False},
        timeout=20
    )
    if rp.status_code not in (204, 201):
        raise RuntimeError(f"Ошибка сброса пароля {username}: {rp.status_code} {rp.text}")

    return user_id


def assign_realm_role(token: str, user_id: str, role_name: str):
    """Назначаем пользователю роль realm’а (idempotent)."""
    h = _headers(token)
    role = get_realm_role(token, role_name)
    a = requests.post(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm",
        headers=h, json=[role], timeout=20
    )
    if a.status_code in (204, 201):
        print(f"👤 Назначена роль '{role_name}' пользователю id={user_id}")
    elif a.status_code == 409:
        print(f"ℹ️  Роль '{role_name}' уже была у пользователя id={user_id}")
    else:
        raise RuntimeError(f"Ошибка назначения роли '{role_name}': {a.status_code} {a.text}")


def create_test_users(token: str):
    """Создаём/синхронизируем тестовых пользователей и назначаем им роли."""
    for u in TEST_USERS:
        uid = get_or_create_user(
            token,
            username=u["username"],
            email=u["email"],
            first=u["firstName"],
            last=u["lastName"],
            password=u["password"]
        )
        assign_realm_role(token, uid, u["role"])


def main():
    print("🔧 Настройка Keycloak (roles/users/client) для REALM:", REALM_NAME)
    try:
        token = get_admin_token()
        print("✅ Токен администратора получен")

        print("🔧 Обновление/создание клиента…")
        ensure_client(token)

        print("📋 Создание ролей…")
        ensure_roles(token)

        print("👥 Создание тестовых пользователей и назначение ролей…")
        create_test_users(token)

        print("\n🎉 Готово!")
        print("Роли:", ", ".join([r["name"] for r in ROLES]))
        print("Тест-пользователи:", ", ".join([u["username"] for u in TEST_USERS]))
        print(f"Админка: {KC_BASE_URL}/admin  | Realm: {REALM_NAME} | Client: {CLIENT_ID}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
