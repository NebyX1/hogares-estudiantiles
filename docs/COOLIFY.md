# Desplegar Hogares Estudiantiles en Coolify

## Preparar las variables una vez

Desde la raíz del proyecto, con Python instalado:

```bash
python scripts/generate_coolify_env.py --url https://solicitudes.TU-DOMINIO --year 2027
```

En Windows se puede usar `backend/.venv/Scripts/python.exe` en lugar de `python`.
El comando crea `.env.coolify` con claves diferentes y aleatorias; no sobrescribe un archivo
existente. Completar los valores `MAIL_*` con el SMTP real. Elegir TLS (normalmente puerto 587)
o SSL (normalmente 465), sin activar ambos. Conservar una copia privada de las variables.

`PUBLIC_URL` es la URL pública sin el puerto interno de Coolify. `APPLICATION_YEAR` configura
la convocatoria tanto en el frontend compilado como en el backend. Cambiarlo requiere recompilar.
Si se importan datos de una instalación anterior, conservar sus claves de cifrado originales.

## Crear el recurso

1. Subir el proyecto a un repositorio Git privado, sin `.env`, entornos virtuales ni datos de pruebas.
2. En Coolify, crear una aplicación desde ese repositorio y seleccionar **Docker Compose**.
3. Directorio base: `/`. Ubicación del Compose: `/compose.coolify.yml`.
4. Cargar las variables de `.env.coolify` en las variables del recurso.
5. En dominios, seleccionar el servicio **frontend**, protocolo **HTTPS**, dominio propio y
   puerto interno **8080**. En versiones con un único campo, usar `https://DOMINIO:8080`.
6. Apuntar el DNS al servidor y desplegar. Solo el frontend recibe tráfico público; los demás
   servicios se comunican por la red interna. No hace falta desplegar Nginx ni bases por separado.

La definición contiene los volúmenes persistentes, dependencias y healthchecks. El backend
aplica las migraciones y arranca Gunicorn como usuario sin privilegios. Mantener una réplica
del backend durante las migraciones.

Referencia: [Docker Compose en Coolify](https://coolify.io/docs/applications/builds/docker-compose).

## Verificar y crear la cuenta inicial

En la terminal del servicio **backend** de Coolify:

```bash
flask check-services --smtp
flask db current
flask create-admin "Nombre Admin" admin@TU-DOMINIO "UNA-CONTRASEÑA-PROPIA-SEGURA" true
```

La primera comprobación conecta a MariaDB, Redis, MinIO y SMTP, negocia TLS y comprueba la
autenticación sin enviar correos. El login administrativo sí envía un código 2FA.

Abrir `https://DOMINIO/admin/login`, completar el acceso y comprobar el dashboard. En
**Contacto institucional**, configurar el correo al que el Ministerio del Interior enviará
los certificados de buena conducta.

- `GET /health`: Nginx responde `ok`.
- `GET /health/ready`: debe devolver `200`, con base de datos, Redis y almacenamiento disponibles.
- `/solicitud`: formulario público; `/admin/login`: panel administrativo.

Las cookies administrativas son Secure en producción. La redirección HTTPS la gestiona el
proxy de Coolify; el healthcheck interno usa HTTP. No desactivar las cookies Secure para
resolver un dominio HTTP: configurar el dominio con HTTPS.

## Prueba completa antes de publicar

`npm run check` ejecuta las pruebas de lógica, lint, compilación y navegador en escritorio/móvil.
En `backend/`, `pytest` incluye autenticación, formularios, filtros, CSV, PDF, certificados y
el ciclo de migraciones. `flask db check` verifica que los modelos coincidan con la base instalada.

Para ejecutar el stack real de pruebas, con Docker activo, desde la raíz:

```bash
python scripts/generate_coolify_env.py --url https://pruebas.example.uy --output .env.smoke
docker compose --env-file .env.smoke -p hogares-smoke -f compose.coolify.yml -f compose.smoke.yml up --build -d --wait --wait-timeout 240
docker compose --env-file .env.smoke -p hogares-smoke -f compose.coolify.yml -f compose.smoke.yml exec -T backend flask check-services --smtp
```

Este stack tiene volúmenes separados y un buzón local Mailpit: frontend en
`http://127.0.0.1:18088`, correos en `http://127.0.0.1:18028`. **No usar `compose.smoke.yml` en producción**:
captura correos y permite cookies por HTTP para las pruebas locales.

Con las dependencias del backend instaladas, configurar `SMOKE_EMAIL=aspirante@example.uy`
en el entorno de la terminal y ejecutar:

```bash
python backend/scripts/smoke_e2e.py http://127.0.0.1:18088
docker compose --env-file .env.smoke -p hogares-smoke -f compose.coolify.yml -f compose.smoke.yml exec -T backend flask create-admin "Admin Pruebas" admin@example.uy "PruebaIntegracion!2027" true
python backend/scripts/smoke_auth.py http://127.0.0.1:18088 http://127.0.0.1:18028 admin@example.uy "PruebaIntegracion!2027"
```

Las credenciales anteriores son exclusivas del stack aislado. La prueba crea una inscripción
ficticia con imágenes/PDF, valida el segundo factor contra Mailpit, el dashboard HTML,
exportaciones CSV/PDF y la revocación de sesión. El workflow de GitHub realiza estos pasos.

Para detener y limpiar **solo ese stack de pruebas**:

```bash
docker compose --env-file .env.smoke -p hogares-smoke -f compose.coolify.yml -f compose.smoke.yml down --volumes
```

## Actualizaciones

Volver a desplegar desde el repositorio conservando variables y volúmenes. Respaldar MariaDB,
MinIO y las claves de cifrado antes de cambios de esquema; las claves son necesarias para
recuperar la información. No regenerarlas en cada deploy. No borrar volúmenes de producción.
Programar `flask cleanup-drafts --limit 500` para retirar borradores vencidos.
