# Gateway

Единая входная точка для фронта и API.

## Компоненты

- **Nginx**: публичная точка входа на порту 80.
- **KrakenD**: API Gateway, маршрутизирует запросы к микросервисам.

## Потоки

- `GET /` и все страницы → Next.js (`frontend:3000`).
- `POST/GET /api/*` → KrakenD (`krakend:8080`).
- `GET /api/auth/docs` → auth напрямую (Swagger).

## Nginx

Файл: `gateway/nginx.conf`

- Проксирует `/api/*` в KrakenD.
- Проксирует `/api/auth/docs` в auth (мимо KrakenD).
- Добавляет базовые security headers.
- Rate limit для auth-эндпоинтов.
- CORS allowlist для dev.

## KrakenD

Конфиг: `gateway/krakend/krakend.tmpl.json`

- Используется Flexible Configuration (Go templates).
- Публичные эндпоинты: `partials/auth-public.tmpl` — register, login, logout, refresh, password-reset.
- Защищённые эндпоинты: `partials/auth-protected.tmpl` — /me, role-*, password-change.
- Profile эндпоинты: `partials/profile-public.tmpl` и `partials/profile-protected.tmpl`.
- JWT валидация: RS256 + JWKS от auth.

### Подключённые profile-роуты через KrakenD

- `PUT /api/profile/me`
- `GET /api/profile/me`
- `PATCH /api/profile/me`
- `POST /api/profile/me/upload`
- `GET /api/profile/user/{name}`
- `GET /api/profile/me/ignored`
- `POST /api/profile/me/ignored/{target_user_id}`
- `DELETE /api/profile/me/ignored/{target_user_id}`

### Важно про refresh

- Endpoint `/api/auth/refresh` публичный, но требуется cookie `refresh_token`.
- В KrakenD включён `input_headers: ["Cookie"]`, чтобы передавать cookie в auth.

## Проверка конфигурации KrakenD

```bash
docker run -it --rm \
  -v $(pwd)/gateway/krakend:/etc/krakend \
  devopsfaith/krakend:2.5 check -c /etc/krakend/krakend.tmpl.json
```

## Troubleshooting

- 502 при `/api/auth/docs` означает, что auth недоступен из nginx.
- 404 на `/api/auth/refresh` означает, что KrakenD не перечитал конфиг.

## Запуск

```bash
make up
```

Обе части запускаются через `infra/docker-compose.yml`.
