# med-platform

## Запуск
docker compose up -d --build --force-recreate

## Миграции
docker compose exec api alembic upgrade head

## Smoke-тесты
curl http://localhost:8000/api/v1/health
# регистрация
$body = '{"email":"u1@example.com","password":"secret123"}'
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/register' -Method Post -Body $body -ContentType 'application/json'
# логин
$login = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -Body $body -ContentType 'application/json'
$headers = @{ Authorization = "Bearer " + $login.access_token }
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/users/me' -Headers $headers
