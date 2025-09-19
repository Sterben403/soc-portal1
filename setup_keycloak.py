#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автонастройка Keycloak для SOC Portal:
 - Realm: soc-portal (создать/обновить, включить verifyEmail при наличии SMTP)
 - Client: soc-portal (OIDC public, PKCE, Redirect URIs/Web Origins)
 - Roles: admin, analyst, manager, client
 - Test users: admin/admin123, analyst/analyst123, manager/manager123, client/client123 (с назначением ролей)

Запуск:
    python setup_keycloak.py
"""

import time
import requests

# ========= НАСТРОЙКИ =========
KC_BASE_URL = "http://localhost:8080"
KC_ADMIN_USER = "admin"
KC_ADMIN_PASSWORD = "admin123"

REALM_NAME = "soc-portal"
CLIENT_ID = "soc-portal"

# SPA редиректы/происхождения: локально и по IP-серверу
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

# ===== Email-проверка =====
# Если включишь EMAIL_VERIFICATION_ENABLED=True, но SMTP ниже не заполнен,
# скрипт НЕ будет принудительно включать verifyEmail (чтобы не «сломать» вход).
EMAIL_VERIFICATION_ENABLED = True

# Заполни эти поля, если хочешь реальную проверку email из Keycloak
SMTP_HOST = ""              # напр. "smtp.gmail.com"
SMTP_PORT = ""              # напр. "587"
SMTP_FROM = ""              # напр. "no-reply@yourdomain.com"
SMTP_FROM_NAME = "SOC Portal"
SMTP_USER = ""              # логин SMTP
SMTP_PASSWORD = ""          # пароль SMTP
SMTP_STARTTLS = True        # обычно True

# Роли, которые нужны в проекте
ROLES = [
    {"name": "admin",   "description": "Администратор — полный доступ"},
    {"name": "analyst", "description": "Аналитик SOC — инциденты/тикеты/отчёты"},
    {"name": "manager", "description": "Менеджер — обзор/отчёты/чтение"},
    {"name": "client",  "description": "Клиент — свои инциденты/тикеты"},
]

# Тест-пользователи
TEST_USERS = [
    {"username": "admin",   "email": "admin@example.com",   "firstName": "Admin",   "lastName": "User",   "password": "admin123",   "role": "admin"},
    {"username": "analyst", "email": "analyst@example.com", "firstName": "SOC",     "lastName": "Analyst","password": "analyst123", "role": "analyst"},
    {"username": "manager", "email": "manager@example.com", "firstName": "Manager", "lastName": "User",   "password": "manager123", "role": "manager"},
    {"username": "client",  "email": "client@example.com",  "firstName": "Client",  "lastName": "User",   "password": "client123",  "role": "client"},
]


# ========= УТИЛИТЫ =========
def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def wait_for_keycloak(timeout_sec: int = 120) -> bool:
    print("⏳ Ожидание старта Keycloak…")
    until = time.time() + timeout_sec
    while time.time() < until:
        try:
            r = requests.get(KC_BASE_URL, timeout=2)
            if r.status_code == 200:
                print("✅ Keycloak отвечает")
                return True
        except Exception:
            pass
        time.sleep(2)
    return False

def get_admin_token() -> str:
    r = requests.post(
        f"{KC_BASE_URL}/realms/master/protocol/openid-connect/token",
        data={
            "username": KC_ADMIN_USER,
            "password": KC_ADMIN_PASSWORD,
            "grant_type": "password",
            "client_id": "admin-cli",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["access_token"]


# ========= НАСТРОЙКА REALM =========
def _smtp_config_present() -> bool:
    return all([SMTP_HOST, SMTP_PORT, SMTP_FROM])

def _realm_body_for_create_or_update() -> dict:
    body = {
        "realm": REALM_NAME,
        "enabled": True,
        # Логин-настройки
        "registrationAllowed": False,
        "loginWithEmailAllowed": True,
        "duplicateEmailsAllowed": False,
        # verifyEmail зависит от smtp
        "verifyEmail": EMAIL_VERIFICATION_ENABLED and _smtp_config_present(),
        # brute force пороги — по вкусу, можно не трогать
        "bruteForceProtected": True,
        "failureFactor": 30,
        "maxFailureWaitSeconds": 900,
        "waitIncrementSeconds": 60,
        "quickLoginCheckMilliSeconds": 1000,
        "minimumQuickLoginWaitSeconds": 60,
        "displayName": "SOC Portal",
        "displayNameHtml": "<div class='kc-logo-text'><span>SOC Portal</span></div>",
    }

    if _smtp_config_present():
        body["smtpServer"] = {
            "host": SMTP_HOST,
            "port": SMTP_PORT,
            "from": SMTP_FROM,
            "fromDisplayName": SMTP_FROM_NAME,
            "auth": "true" if SMTP_USER and SMTP_PASSWORD else "false",
            "user": SMTP_USER or "",
            "password": SMTP_PASSWORD or "",
            "starttls": "true" if SMTP_STARTTLS else "false",
        }
    return body

def ensure_realm(token: str):
    h = _headers(token)

    # Проверяем, есть ли realm
    r = requests.get(f"{KC_BASE_URL}/admin/realms/{REALM_NAME}", headers=h, timeout=20)
    if r.status_code == 200:
        # Обновим настройки (verifyEmail, smtp, и пр.)
        body = _realm_body_for_create_or_update()
        u = requests.put(f"{KC_BASE_URL}/admin/realms/{REALM_NAME}", headers=h, json=body, timeout=30)
        if u.status_code in (204, 201):
            print("♻️  Realm обновлён")
        else:
            raise RuntimeError(f"Ошибка обновления realm: {u.status_code} {u.text}")
    elif r.status_code == 404:
        # Создадим новый
        body = _realm_body_for_create_or_update()
        c = requests.post(f"{KC_BASE_URL}/admin/realms", headers=h, json=body, timeout=30)
        if c.status_code == 201:
            print("✅ Realm создан")
        elif c.status_code == 409:
            print("ℹ️  Realm уже существует — ок")
        else:
            raise RuntimeError(f"Ошибка создания realm: {c.status_code} {c.text}")
    else:
        r.raise_for_status()

    if EMAIL_VERIFICATION_ENABLED and not _smtp_config_present():
        print("⚠️  Включить автоматическую проверку email НЕ удалось: SMTP не настроен.")
        print("    Скрипт оставил verifyEmail выключенным, чтобы логин не ломался.")
        print("    Варианты:")
        print("    • Настрой SMTP в Keycloak → включи verifyEmail.")
        print("    • Или ставь проверку вручную для пользователя (Required actions → VERIFY_EMAIL).")


# ========= НАСТРОЙКА КЛИЕНТА =========
def ensure_client(token: str):
    h = _headers(token)
    # Ищем клиент по clientId
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
        "standardFlowEnabled": True,         # Code + PKCE
        "directAccessGrantsEnabled": False,  # ROPC выключен
        "serviceAccountsEnabled": False,
        "redirectUris": sorted(set(REDIRECT_URIS)),
        "webOrigins": sorted(set(WEB_ORIGINS)),
        "attributes": {
            "pkce.code.challenge.method": "S256",
        },
    }

    if items:
        internal_id = items[0]["id"]
        u = requests.put(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/clients/{internal_id}",
            headers=h, json=body, timeout=30
        )
        if u.status_code in (204, 201):
            print("♻️  Client soc-portal обновлён")
        else:
            raise RuntimeError(f"Ошибка обновления клиента: {u.status_code} {u.text}")
    else:
        c = requests.post(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/clients",
            headers=h, json=body, timeout=30
        )
        if c.status_code == 201:
            print("✅ Client soc-portal создан")
        elif c.status_code == 409:
            print("ℹ️  Client soc-portal уже существует — ок")
        else:
            raise RuntimeError(f"Ошибка создания клиента: {c.status_code} {c.text}")


# ========= РОЛИ И ПОЛЬЗОВАТЕЛИ =========
def ensure_roles(token: str):
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
    h = _headers(token)
    r = requests.get(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/roles/{role_name}",
        headers=h, timeout=20
    )
    r.raise_for_status()
    return r.json()

def get_or_create_user(token: str, username: str, email: str, first: str, last: str, password: str) -> str:
    h = _headers(token)
    s = requests.get(
        f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users?username={username}",
        headers=h, timeout=20
    )
    s.raise_for_status()
    items = s.json()

    need_verify = EMAIL_VERIFICATION_ENABLED and _smtp_config_present()

    if items:
        user_id = items[0]["id"]
        # синхронизируем поля
        u = requests.put(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users/{user_id}",
            headers=h,
            json={
                "email": email,
                "firstName": first,
                "lastName": last,
                "enabled": True,
                "emailVerified": False if need_verify else True,
                "requiredActions": (["VERIFY_EMAIL"] if need_verify else []),
            },
            timeout=20
        )
        if u.status_code not in (204, 201):
            raise RuntimeError(f"Ошибка обновления пользователя {username}: {u.status_code} {u.text}")
    else:
        # создаём
        payload = {
            "username": username,
            "email": email,
            "firstName": first,
            "lastName": last,
            "enabled": True,
            "emailVerified": False if need_verify else True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
            "requiredActions": (["VERIFY_EMAIL"] if need_verify else []),
        }
        c = requests.post(
            f"{KC_BASE_URL}/admin/realms/{REALM_NAME}/users",
            headers=h, json=payload, timeout=20
        )
        if c.status_code not in (201, 409):
            raise RuntimeError(f"Ошибка создания пользователя {username}: {c.status_code} {c.text}")

        # получим id
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
        headers=h, json={"type": "password", "value": password, "temporary": False}, timeout=20
    )
    if rp.status_code not in (204, 201):
        raise RuntimeError(f"Ошибка сброса пароля {username}: {rp.status_code} {rp.text}")

    return user_id

def assign_realm_role(token: str, user_id: str, role_name: str):
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
    for u in TEST_USERS:
        uid = get_or_create_user(
            token,
            username=u["username"],
            email=u["email"],
            first=u["firstName"],
            last=u["lastName"],
            password=u["password"],
        )
        assign_realm_role(token, uid, u["role"])


# ========= MAIN =========
def main():
    print("🚀 Настройка Keycloak для SOC Portal…")
    if not wait_for_keycloak():
        raise SystemExit("❌ Keycloak не поднялся вовремя")

    try:
        token = get_admin_token()
        print("🔑 Admin токен получен")

        print("🏰 Realm…")
        ensure_realm(token)

        print("🔧 Client…")
        ensure_client(token)

        print("🧩 Роли…")
        ensure_roles(token)

        print("👥 Пользователи…")
        create_test_users(token)

        print("\n🎉 Готово!")
        print(f"Админка: {KC_BASE_URL}/admin | Realm: {REALM_NAME} | Client: {CLIENT_ID}")
        if EMAIL_VERIFICATION_ENABLED:
            if _smtp_config_present():
                print("✉️  Проверка email включена (SMTP настроен).")
            else:
                print("⚠️  Проверка email не включена, т.к. SMTP не настроен. Можно включить вручную позже.")
                print("    Варианты: настроить SMTP и включить Verify Email в настройках Realm, либо ставить VERIFY_EMAIL вручную на пользователя.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
