# Evaluación Diagnóstica FCA · Contaduría Pública

App web (Streamlit + Supabase) para que alumnos de la Licenciatura en Contaduría Pública (FCA, UABJO) contesten
dos tests y reciban una guía de especialidad. Es una copia **independiente** de la versión de Administración
(mismo código, otros tests, otra base de datos). Lee el [README](README.md) antes de cambiar nada.

## Comandos
- `streamlit run app.py` — alumno en `/`, docente en `/admin` (necesita `.streamlit/secrets.toml`).
- `python -m pytest -q` — unas 535 pruebas; no necesitan Supabase.
- `python scripts/convertir_tests_contaduria.py` — regenera `config/tests/*.xlsx` desde `docs/referencia_contaduria/`.

## Qué es de Contaduría y qué no
- `config/tests/` = tests reales: Big Five (25 reactivos) y habilidades (28 reactivos, escala 0-4 + SE).
  Campos: CE (Contabilidades), AE (Auditorías), DF (Derecho Fiscal), AF (Administración Financiera).
- `tests/datos_admin/` = Excel de Administración, **solo datos de prueba** (los casos de `tests/golden/` se
  calcularon con ellos). No los edites ni los despliegues.
- `scripts/convertir_tests_reales.py` y `generar_golden_scoring.py` son de Administración (referencia).
- Cambiar preguntas o escala con alumnos contestando los bloquea (ver README, «Los tests»).

## Reglas
- Base de datos propia: `sql/00_instalacion_completa.sql` y `docs/supabase_contaduria.md`. Nunca uses las
  claves del proyecto de Administración ni subas `.streamlit/secrets.toml`.
- Modelo de calificación igual al de Administración (afinidad con pesos iguales, sin los pesos 0.4/0.3/0.3 de la
  plantilla). Cambiarlo toca `modules/scoring.py` e `interpretacion.py`.
- Los textos de los resultados son guía de orientación, no diagnóstico psicológico.
- Los commits se hacen solo cuando el usuario lo pide.
- Responde en español, breve y directo.
