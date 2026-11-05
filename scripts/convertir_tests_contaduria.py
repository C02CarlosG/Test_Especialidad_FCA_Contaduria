"""Convierte las calculadoras de Contaduría Pública de docs/referencia_contaduria/ al formato del
cargador (config/tests/*.xlsx).

Uso:  python scripts/convertir_tests_contaduria.py

Fuentes:
  - plantilla_orientacion_y_big_five_contaduria-v2.xlsx: Big Five (hoja «Test 2 - Big Five») y las
    combinaciones OCEAN de cada especialidad (hoja «Resumen y Diagnostico» y «Guia de Tutoria y Alineacion»).
  - test_orientacion_especialidades_contaduria-v5.xlsx: test de habilidades (28 reactivos, escala 0-4 + SE).
Solo copia texto de las calculadoras; los textos de los rasgos son los mismos que en Administración.
"""
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import convertir_tests_reales as base  # noqa: E402  (reutiliza el formato de salida y los textos de los rasgos)

RAIZ = base.RAIZ
REF = RAIZ / "docs" / "referencia_contaduria"
DESTINO = RAIZ / "config" / "tests"
CODIGOS = {"Contabilidades Especializadas": "CE", "Auditorías Especializadas": "AE",
           "Derecho Fiscal": "DF", "Administración Financiera": "AF"}
DIMENSIONES = {  # texto de la plantilla -> código
    "Apertura a la Experiencia": "APERTURA", "Responsabilidad / Tesón": "RESPONSABILIDAD",
    "Extraversión": "EXTRAVERSION", "Amabilidad / Cordialidad": "AMABILIDAD", "Estabilidad Emocional": "ESTABILIDAD"}
RASGO = {"Apertura": "APERTURA", "Responsabilidad": "RESPONSABILIDAD", "Extraversión": "EXTRAVERSION",
         "Amabilidad": "AMABILIDAD", "Estabilidad": "ESTABILIDAD"}


def test_1() -> None:
    wb = openpyxl.load_workbook(REF / "plantilla_orientacion_y_big_five_contaduria-v2.xlsx")
    ws, res, guia = wb["Test 2 - Big Five"], wb["Resumen y Diagnostico"], wb["Guia de Tutoria y Alineacion"]
    por_dim = {d: c for d, c in DIMENSIONES.items()}
    preguntas = []
    for r in range(5, 30):
        dim = ws.cell(r, 4).value.rsplit(" (", 1)[0]  # «Apertura a la Experiencia (O)» -> sin la letra
        preguntas.append((f"BF{int(ws.cell(r, 1).value):02d}", ws.cell(r, 2).value.strip(), por_dim[dim]))
    esp = [(c, n, base.DESCRIPCION_RASGOS[c], "") for n, c in DIMENSIONES.items()]
    escala = []
    for parte in ws["A2"].value.replace("Escala Likert:", "").split("|"):
        valor, etiqueta = parte.split("=")
        escala.append((int(valor), etiqueta.strip().capitalize().replace(" En ", " en ")))
    # Perfil OCEAN de cada especialidad: «Alta Responsabilidad + Estabilidad + Apertura» (hoja de la guía, col. E).
    afinidades = []
    for r in range(6, 10):
        nombre = guia.cell(r, 1).value
        perfil = guia.cell(r, 5).value.replace("Alta ", "").replace("Alto ", "")
        comps = "+".join(RASGO[t.strip().split()[0]] for t in perfil.split("+"))
        descripcion = next(res.cell(k, 2).value for k in range(39, 43) if res.cell(k, 1).value == nombre)
        afinidades.append((CODIGOS[nombre], nombre, comps, descripcion))
    # La plantilla no define umbrales propios del Big Five: se usan los de la calculadora de rasgos (Administración).
    niveles = [("categoria", 0.72, "Alto"), ("categoria", 0.56, "Medio"), ("categoria", 0, "Área de Desarrollo"),
               ("afinidad", 0.76, "Alta Afinidad"), ("afinidad", 0.56, "Afinidad Media"),
               ("afinidad", 0, "Desarrollo Requerido")]
    instrucciones = ("Evalúa cada afirmación indicando qué tan identificado/a te sientes en tu desempeño "
                     "académico y profesional.")
    base.escribir(DESTINO / "1_test_big_five.xlsx", "Test 1: The Big Five", instrucciones, esp, preguntas, escala,
                  niveles, afinidades)


def test_2() -> None:
    wb = openpyxl.load_workbook(REF / "test_orientacion_especialidades_contaduria-v5.xlsx")
    ws, guia = wb["Test_Orientación"], wb["Guía_Tutoría"]
    preguntas = [(ws.cell(r, 3).value.strip(), ws.cell(r, 4).value.strip(), CODIGOS[ws.cell(r, 2).value])
                 for r in range(23, 51)]
    esp = []
    for r in range(3, 7):
        nombre = guia.cell(r, 1).value
        perfil = f"DISC: {guia.cell(r, 2).value} Holland: {guia.cell(r, 3).value} HBDI: {guia.cell(r, 4).value}"
        esp.append((CODIGOS[nombre], nombre, guia.cell(r, 5).value, perfil))
    escala = [(int(ws.cell(r, 1).value), ws.cell(r, 2).value) for r in range(14, 19)]
    escala.append(("SE", ws.cell(19, 2).value))
    niveles = [("categoria", 0.8, "ALTO (Perfil Fuerte)"), ("categoria", 0.5, "MEDIO (En Desarrollo)"),
               ("categoria", 0, "BAJO (Baja Afinidad)")]
    base.escribir(DESTINO / "2_test_orientacion_especialidades.xlsx", "Test 2: Especialidades Lic. en Contaduría Pública",
                  ws["A10"].value.strip(), esp, preguntas, escala, niveles)


if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    test_1()
    test_2()
    print("Listo:", *sorted(p.name for p in DESTINO.glob("*.xlsx")), sep="\n- ")
