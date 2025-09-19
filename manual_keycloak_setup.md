# Ручная настройка Keycloak для SOC Portal

## Шаг 1: Вход в Keycloak
1. Откройте браузер и перейдите на http://localhost:8080
2. Попробуйте войти с:
   - Логин: `admin`
   - Пароль: `admin`

Если не получается войти, попробуйте:
- Логин: `temp-admin`
- Пароль: `temp-admin`

## Шаг 2: Создание Realm
1. В админ-панели Keycloak нажмите "Create Realm"
2. Введите:
   - **Realm name:** `soc`
   - **Display name:** `SOC Portal`
3. Нажмите "Create"

## Шаг 3: Создание клиента
1. В левом меню выберите "Clients"
2. Нажмите "Create"
3. Введите:
   - **Client ID:** `soc-portal`
   - **Client Protocol:** `openid-connect`
4. Нажмите "Save"

### Настройка клиента:
1. В разделе "Settings":
   - **Access Type:** `public`
   - **Valid Redirect URIs:** `http://localhost:5173/*`
   - **Web Origins:** `http://localhost:5173`
2. Нажмите "Save"

## Шаг 4: Создание ролей
1. В левом меню выберите "Roles"
2. Создайте роли:
   - `admin`
   - `analyst`
   - `manager`
   - `user`

## Шаг 5: Создание пользователя
1. В левом меню выберите "Users"
2. Нажмите "Add user"
3. Введите:
   - **Username:** `testuser`
   - **Email:** `test@example.com`
   - **First Name:** `Test`
   - **Last Name:** `User`
4. Нажмите "Save"

### Настройка пароля:
1. Перейдите на вкладку "Credentials"
2. Введите:
   - **Password:** `password`
   - **Password Confirmation:** `password`
   - Снимите галочку "Temporary"
3. Нажмите "Set Password"

### Назначение роли:
1. Перейдите на вкладку "Role Mappings"
2. В разделе "Realm Roles" выберите `user`
3. Нажмите "Add selected"

## Шаг 6: Проверка
После настройки попробуйте войти в SOC Portal:
1. Откройте http://localhost:5173
2. Войдите с:
   - Логин: `testuser`
   - Пароль: `password`



