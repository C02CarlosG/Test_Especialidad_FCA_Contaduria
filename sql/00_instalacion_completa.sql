-- INSTALACIÓN COMPLETA (Contaduría Pública): esquema, alumnos autorizados, correo/envío del reporte y seguridad por filas, en un solo paso
-- (equivale a ejecutar 01 a 06 de esta carpeta, sin los pasos de migración).
-- Supabase → SQL Editor → New query → pega TODO este archivo → Run. Es seguro repetirlo.

-- Esquema del test vocacional. Ejecutar en Supabase: SQL Editor.
create extension if not exists "pgcrypto";

create table if not exists public.alumnos (
    id                uuid primary key default gen_random_uuid(),
    apellido_paterno  text not null,
    apellido_materno  text not null,
    nombres           text not null,
    matricula         text not null unique check (matricula ~ '^[0-9]{1,10}$'),
    edad              smallint not null check (edad between 18 and 99),
    tutor             text not null,   -- nombre del tutor / orientador
    semestre          smallint check (semestre between 1 and 8),  -- nulo en alumnos registrados antes de pedirlo
    acepto_privacidad boolean not null default false,
    acepto_en         timestamptz,
    estado            text not null default 'en_curso'
                      check (estado in ('en_curso', 'terminado')),
    creado_en         timestamptz not null default now(),
    correo            text,            -- a donde se envía el reporte en PDF
    reporte_estado    text not null default 'pendiente',
    reporte_enviado_en    timestamptz,
    reporte_reservado_en  timestamptz, -- cuándo se tomó la reserva del envío
    reporte_error     text,
    constraint acepto_requerido check (acepto_privacidad and acepto_en is not null),
    constraint alumnos_reporte_estado_check check (reporte_estado in ('pendiente', 'enviando', 'enviado', 'error')),
    constraint alumnos_correo_formato check (correo is null or correo ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$')
);

-- Lista de alumnos autorizados a contestar el test. Solo la matrícula decide el acceso;
-- el resto de las columnas es informativo. Se carga con scripts/importar_alumnos_autorizados.py.
create table if not exists public.alumnos_autorizados (
    matricula  text primary key check (matricula ~ '^[0-9]{1,10}$'),
    nombre     text not null,
    sexo       text,
    estatus    text,                   -- REGULAR | IRREGULAR, tal como viene en la lista
    cargado_en timestamptz not null default now()
);

-- Avance del alumno en cada test. El alumno los contesta en orden fijo.
create table if not exists public.progreso_tests (
    alumno_id    uuid not null references public.alumnos(id) on delete cascade,
    test_id      text not null,
    estado       text not null default 'en_curso' check (estado in ('en_curso', 'terminado')),
    version_test text not null,           -- hash del .xlsx con el que respondió
    iniciado_en  timestamptz not null default now(),
    terminado_en timestamptz,
    primary key (alumno_id, test_id)
);

create table if not exists public.respuestas (
    alumno_id   uuid not null references public.alumnos(id) on delete cascade,
    test_id     text not null,
    pregunta_id text not null,
    valor       integer,          -- NULL = "SE" (sin experiencia): dato faltante, no es 0
    unique (alumno_id, test_id, pregunta_id)
);

-- Un resultado por alumno y por test. La comparación entre tests se calcula al vuelo.
create table if not exists public.resultados (
    alumno_id               uuid not null references public.alumnos(id) on delete cascade,
    test_id                 text not null,
    puntajes                jsonb not null,
    afinidad                jsonb not null,
    -- NULL si el test no alcanzó a tener al menos 2 afinidades con datos (muchas respuestas "SE")
    especialidad_principal  text,
    especialidad_secundaria text,
    calculado_en            timestamptz not null default now(),
    unique (alumno_id, test_id)
);

-- Intentos fallidos persistentes (acceso con matrícula ajena / admin), para limitar fuerza bruta
-- aunque Streamlit reinicie la sesión.
create table if not exists public.intentos_fallidos (
    id        bigserial primary key,
    tipo      text not null check (tipo in ('acceso', 'admin')),
    clave     text not null,           -- matrícula o identificador de cliente
    creado_en timestamptz not null default now()
);

-- Índices
create index if not exists idx_alumnos_estado     on public.alumnos(estado);
create index if not exists idx_respuestas_alumno  on public.respuestas(alumno_id, test_id);
create index if not exists idx_progreso_alumno    on public.progreso_tests(alumno_id);
create index if not exists idx_intentos_busqueda  on public.intentos_fallidos(tipo, clave, creado_en desc);

-- ============ Seguridad por filas (RLS) ============
-- Row Level Security: activo en TODAS las tablas y SIN políticas.
-- Con RLS activo y sin políticas, los roles `anon` y `authenticated`
-- (clave pública) no pueden leer ni escribir nada.
-- La app usa la service_role key desde el servidor; ese rol omite RLS.
alter table public.alumnos           enable row level security;
alter table public.progreso_tests    enable row level security;
alter table public.respuestas        enable row level security;
alter table public.resultados        enable row level security;
alter table public.intentos_fallidos enable row level security;
alter table public.alumnos_autorizados enable row level security;

alter table public.alumnos           force row level security;
alter table public.progreso_tests    force row level security;
alter table public.respuestas        force row level security;
alter table public.resultados        force row level security;
alter table public.intentos_fallidos force row level security;
alter table public.alumnos_autorizados force row level security;

-- Defensa en profundidad: quitar privilegios directos a roles públicos.
revoke all on public.alumnos, public.progreso_tests, public.respuestas,
              public.resultados, public.intentos_fallidos, public.alumnos_autorizados from anon, authenticated;
revoke all on sequence public.intentos_fallidos_id_seq from anon, authenticated;

-- ============ Verificación (resultado esperado: 6 tablas, todas con rls = true) ============
select tablename, rowsecurity as rls
from pg_tables
where schemaname = 'public'
  and tablename in ('alumnos', 'progreso_tests', 'respuestas', 'resultados', 'intentos_fallidos', 'alumnos_autorizados')
order by tablename;
