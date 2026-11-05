"""Tests de Contaduría Pública (config/tests): carga, contenido y cálculo contra la plantilla."""
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import openpyxl
import pytest

from fakes import alumno
from modules.config_loader import load_all_tests
from modules.interpretacion import construir
from modules.reports import excel_individual, pdf_individual
from modules.scoring import calificar

RAIZ = Path(__file__).resolve().parent.parent
REF = RAIZ / "docs" / "referencia_contaduria"
TEST1, TEST2 = load_all_tests(RAIZ / "config" / "tests")


def test_contenido_de_los_dos_tests():
    assert (TEST1.id, TEST2.id) == ("1_test_big_five", "2_test_orientacion_especialidades")
    assert len(TEST1.preguntas) == 25 and len(TEST2.preguntas) == 28
    assert [e.codigo for e in TEST2.especialidades] == ["CE", "AE", "DF", "AF"]
    assert [a.codigo for a in TEST1.afinidades] == ["CE", "AE", "DF", "AF"]
    assert TEST2.sin_experiencia and (TEST2.valor_min, TEST2.valor_max) == (0, 4)
    assert (TEST1.valor_min, TEST1.valor_max) == (1, 5)
    assert {p.especialidad_codigo for p in TEST2.preguntas} == {"CE", "AE", "DF", "AF"}


def test_los_resultados_coinciden_con_la_plantilla_de_excel():
    wb = openpyxl.load_workbook(REF / "test_orientacion_especialidades_contaduria-v5.xlsx")
    ws = wb["Test_Orientación"]
    resp = {ws.cell(r, 3).value: (None if ws.cell(r, 5).value == "SE" else int(ws.cell(r, 5).value))
            for r in range(23, 51)}
    r2 = calificar(TEST2, resp)
    por = {e.codigo: e for e in r2.especialidades}
    for nombre, cod in (("Contabilidades Especializadas", "CE"), ("Auditorías Especializadas", "AE"),
                        ("Derecho Fiscal", "DF"), ("Administración Financiera", "AF")):
        obt = sum(v for p in TEST2.preguntas if p.especialidad_codigo == cod and (v := resp[p.id]) is not None)
        validas = sum(1 for p in TEST2.preguntas if p.especialidad_codigo == cod and resp[p.id] is not None)
        assert por[cod].obtenido == obt and por[cod].maximo == validas * 4, nombre


def test_big_five_de_la_plantilla_da_los_mismos_puntajes_y_afinidades():
    ws = openpyxl.load_workbook(REF / "plantilla_orientacion_y_big_five_contaduria-v2.xlsx")["Test 2 - Big Five"]
    resp = {f"BF{int(ws.cell(r, 1).value):02d}": int(ws.cell(r, 3).value) for r in range(5, 30)}
    r1 = calificar(TEST1, resp)
    crudo = {c: sum(resp[p.id] for p in TEST1.preguntas if p.especialidad_codigo == c) for c in
             ("APERTURA", "RESPONSABILIDAD", "EXTRAVERSION", "AMABILIDAD", "ESTABILIDAD")}
    assert {e.codigo: e.obtenido for e in r1.especialidades} == crudo
    esperado = {"CE": ("RESPONSABILIDAD", "ESTABILIDAD"), "AE": ("RESPONSABILIDAD", "ESTABILIDAD", "APERTURA"),
                "DF": ("RESPONSABILIDAD", "APERTURA"), "AF": ("RESPONSABILIDAD", "ESTABILIDAD", "EXTRAVERSION")}
    for a in r1.afinidades:
        assert a.obtenido == sum(crudo[c] for c in esperado[a.codigo]) and a.maximo == 25 * len(esperado[a.codigo])


def test_informe_pdf_y_excel_de_contaduria():
    r1 = calificar(TEST1, {p.id: 4 for p in TEST1.preguntas})
    r2 = calificar(TEST2, {p.id: (3 if i % 5 else None) for i, p in enumerate(TEST2.preguntas)})
    inf = construir([TEST1, TEST2], [r1, r2])
    assert {c.codigo for c in inf.campos} == {"CE", "AE", "DF", "AF"}
    pdf = pdf_individual(alumno(), [TEST1, TEST2], [r1, r2], datetime(2026, 10, 15))
    assert pdf.startswith(b"%PDF")
    if shutil.which("pdftotext"):
        texto = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, capture_output=True,
                               check=True).stdout.decode()
        assert "Derecho Fiscal" in texto and "Mercadotecnia" not in texto
    assert excel_individual(alumno(), [TEST1, TEST2], [r1, r2], datetime(2026, 10, 15))[:2] == b"PK"
