# ABRXOS Builders + Canon R6

Repositorio fuente para dos aplicaciones locales independientes y el canon audiovisual/editorial R6.

## Apps

- `apps/brand-builder/` — **ABRXOS X · Brand Builder V1**. Información de marca + Branding Method + Brand Adapter → AI Brand Package.
- `apps/content-builder/` — **ABRXOS Content Builder V1**. Transcript/plan + Project Config + Brand Adapter + Canon R6 → AI Content Package.

Ambas apps son Package Builders: **no ejecutan IA directamente**.

## Canon

- `canon/r6/json/` — schemas, templates, prompts y librerías machine-readable usadas por Content Builder.
- `canon/r6/txt/` — documentación normativa humana de XR, Motion, CINE, SFX, Music, Captions, timing, QA, Geometra, etc.

## Documentación

- `docs/system/` — mapa general y fronteras.
- `docs/apps/brand-builder/` — canon de la app, componentes, datos, export, reparación, QA.
- `docs/apps/content-builder/` — idem para Content Builder.
- `tutorials/` — tutoriales por caso.

## Instalación macOS

Ver `install/INSTALAR_AMBAS_APPS.command` y `docs/github/03_INSTALL_MAC.txt`.

## GitHub

Ver `docs/github/00_REPO_MAP.txt` y `docs/github/01_SUBIR_A_GITHUB.txt`.

## Fuente externa del Branding Method

El PDF original **no está incluido en el repo**. `references/BRANDING_METHOD_SOURCE_NOTE.txt` explica cómo usarlo como referencia aportada por el usuario sin duplicarlo.

## Fuente de verdad

El JSON canónico manda para herramientas; los TXT explican la intención humana. Si hay contradicción, corregir ambos en el mismo cambio y añadir changelog/migración.
