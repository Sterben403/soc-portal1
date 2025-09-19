import os, httpx

KC_BASE = os.getenv("KC_BASE_URL", "http://keycloak:8080")
KC_REALM = os.getenv("KC_REALM", "soc")
KC_ADMIN_USER = os.getenv("KC_ADMIN_USER", "admin")
KC_ADMIN_PASS = os.getenv("KC_ADMIN_PASS", "admin123")

async def _admin_token() -> str:
    url = f"{KC_BASE}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": KC_ADMIN_USER,
        "password": KC_ADMIN_PASS,
    }
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(url, data=data)
        r.raise_for_status()
        return r.json()["access_token"]

async def _get_user_id(email: str, token: str) -> str:
    url = f"{KC_BASE}/admin/realms/{KC_REALM}/users"
    params = {"email": email, "exact": "true"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        items = r.json()
        if not items:
            raise RuntimeError(f"KC user not found: {email}")
        return items[0]["id"]

async def _get_realm_role(role_name: str, token: str) -> dict:
    url = f"{KC_BASE}/admin/realms/{KC_REALM}/roles/{role_name}"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.json()

async def assign_realm_role_to_email(email: str, role_name: str):
    token = await _admin_token()
    uid = await _get_user_id(email, token)
    role = await _get_realm_role(role_name, token)
    url = f"{KC_BASE}/admin/realms/{KC_REALM}/users/{uid}/role-mappings/realm"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(url, json=[{
            "id": role["id"], "name": role["name"]
        }], headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
