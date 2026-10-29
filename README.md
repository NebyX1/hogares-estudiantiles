# Solicitudes de Hogares Estudiantiles

Sistema web de la Dirección General de Servicios Sociales de la Intendencia de Lavalleja para solicitudes de beca de alojamiento en Minas, Mariscala y Montevideo.

## Componentes

- `src/`: frontend React, TypeScript, Vite, Tailwind 4 y DaisyUI.
- `backend/`: API Flask, validación, cifrado, MariaDB (`hogares_db`) y MinIO.
- `compose.coolify.yml`: despliegue completo con frontend, backend, MariaDB, Redis y MinIO.
- `sample-frontend/` y `sample-backend/`: proyectos de referencia, no forman parte de las imágenes.

## Landing y seguimiento

La portada usa el diseño de [hogares-landing-temp](https://github.com/IntendenciaDeLavalleja/hogares-landing-temp)
(referencia `b936b6a1dd38dd365629d91e5cf9027f11567351`), con componentes en
`src/features/landing/`. El botón principal abre el formulario existente y conserva los casos de
continuar una solicitud o ver un comprobante. El seguimiento consulta la misma API del proyecto.

El tema visual se aplica solo a la portada (`data-theme="lavalleja"`); el formulario y el comprobante
conservan su diseño. Archivo, Instrument Serif e IBM Plex Mono se sirven localmente desde el build,
sin dependencias de Google Fonts ni cambios en la CSP de producción.

## Desarrollo frontend

```bash
npm install
npm run dev
```

Vite redirige `/api` al backend local en el puerto 5000.

## Despliegue Coolify

La guía completa está en [docs/COOLIFY.md](docs/COOLIFY.md).

1. Generar las variables privadas: `python scripts/generate_coolify_env.py --url https://TU-DOMINIO --year 2027`.
2. Completar SMTP en `.env.coolify` y cargar las variables en Coolify.
3. Seleccionar Docker Compose desde el repositorio y usar `compose.coolify.yml`.
4. Asignar el dominio HTTPS a `frontend`, puerto interno `8080`, y desplegar.
5. Dentro del backend: `flask check-services --smtp`, crear el primer administrador y configurar el contacto institucional.

Las migraciones se aplican automáticamente al arrancar. No publicar puertos de base de datos,
Redis, backend ni MinIO. Mantener las claves y volúmenes persistentes en cada actualización.

## Verificaciones

```bash
npm ci
npx playwright install chromium
npm run check
npm audit
cd backend
pip install -r requirements-dev.txt
pytest
ruff check app tests scripts ../scripts
pip-audit -r requirements.txt
```

Hay 28 casos compartidos que verifican la misma documentación en cliente y servidor,
y pruebas de navegador para escritorio y móvil. `.github/workflows/check.yml` ejecuta las
verificaciones y construye el stack completo con un buzón SMTP local para comprobar
inscripción, segundo factor, dashboard, CSV y PDF. Ver la guía para ejecutar ese stack localmente.

## Seguridad y almacenamiento

- Las imágenes se optimizan a WebP en cliente y se recodifican nuevamente en servidor.
- El servidor valida contenido real, dimensiones y tamaño; no confía solo en extensión o MIME.
- Los PDF se inspeccionan, no pueden estar cifrados ni contener acciones automáticas.
- MinIO usa un bucket privado, credenciales de aplicación limitadas al bucket, claves de objeto aleatorias y contenido cifrado por la aplicación.
- Los formularios se cifran antes de persistirse.
- Redis aplica límites de frecuencia compartidos.
- Los contenedores de aplicación se ejecutan sin privilegios.
