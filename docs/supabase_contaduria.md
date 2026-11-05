# Conectar la app de Contaduría con Supabase

La app de Contaduría usa **su propio proyecto de Supabase** (no el de Administración), para que los alumnos y
resultados de cada carrera no se mezclen. Son unos 10 minutos.

## 1. Crear el proyecto
1. En [supabase.com](https://supabase.com) → **New project** (organización propia o la misma que Administración).
2. Nombre: `fca-contaduria`. Región cercana a México. Guarda la contraseña de la base (no la usa la app).
3. Espera a que termine de crearse.

## 2. Crear las tablas y la seguridad
1. **SQL Editor → New query**.
2. Pega **todo** [`sql/00_instalacion_completa.sql`](../sql/00_instalacion_completa.sql) y pulsa **Run**.
3. Al final debe mostrar **5 tablas** (`alumnos`, `intentos_fallidos`, `progreso_tests`, `respuestas`, `resultados`)
   y `rls = true` en todas. Si alguna dice `false`, vuelve a ejecutar el archivo.

## 3. Copiar las claves
En **Project Settings → API**:
- **Project URL** → `[supabase] url`.
- **service_role** (secret) → `[supabase] service_role_key`. **Nunca** la subas al repositorio ni la uses en el navegador.
  No uses la clave `anon`: la app no la necesita y la base no permite nada con ella.

## 4. Secretos
Copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml` (está en `.gitignore`) y llena:

```toml
[supabase]
url = "https://XXXX.supabase.co"
service_role_key = "eyJ..."

[admin]
password = "una-contraseña-larga-y-unica"   # mínimo 12 caracteres; distinta a la de Administración

[app]
public_url = "https://TU-APP-CONTADURIA.streamlit.app"
MOSTRAR_RESULTADO_AL_ALUMNO = true
```

En Streamlit Community Cloud pega el mismo contenido en **Settings → Secrets**.

## 5. Probar
```bash
streamlit run app.py     # alumno en http://localhost:8501 · docente en /admin
```
Haz un registro de prueba y contesta los dos tests. Debe aparecer en **Table Editor → alumnos**, y en
`/admin → Avance`. Después borra la prueba:
```sql
delete from public.alumnos where matricula = '123456';
```

## 6. Publicar
Sigue «Publicar en Streamlit Community Cloud» del [README](../README.md) con **este** repositorio. Después,
genera el QR en `/admin → Código QR` y pruébalo con un iPhone y un Android.

## Notas
- Plan gratuito de Supabase: el proyecto se **pausa tras 7 días sin uso**; entra a verlo antes de la aplicación.
- Respaldo: antes de cerrar el ciclo, descarga el Excel concentrado de `/admin → Descargas`.
- Borrado de datos: ver «Privacidad y datos personales» del README.
