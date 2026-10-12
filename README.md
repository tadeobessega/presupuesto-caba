# Presupuesto CABA 2027 en perspectiva · CEER

Tablero que compara el Proyecto de Presupuesto 2027 de la Ciudad de Buenos Aires con los presupuestos y ejecuciones desde 1995, en pesos constantes, y evalúa las promesas del Ejecutivo.

## Estructura

| Ruta | Qué es |
|---|---|
| `index.html` | El sitio (un solo archivo, datos embebidos). Es lo que publica GitHub Pages. |
| `site/template.html` | Plantilla del sitio; `__DATA__` y los logos se reemplazan al construir. |
| `data/dashboard.json` | Datos que usa el sitio (cubos de gasto, CAIF, recaudación, deflactores, proyecto 2027). |
| `bases/base_gasto_CABA_trimestral_2019-2026.csv.gz` | Base de gasto 2019–2026 T2, por año y trimestre, hasta partida subparcial (543 mil filas, pesos corrientes). |
| `bases/CAIF+deuda_actualizado.xlsx` | Libro CAIF+deuda con la hoja `dataset- CAIF corriente` actualizada a 1995–2025 y proyecto 2027, IPC extendido y hojas nuevas de IDECBA. |
| `bases/recursos_CABA_CAIF_y_aperturas.xlsx` | Recursos por tipo (CAIF), recaudación mensual por concepto 1997–2026, IIBB por régimen, rubros 2027 y deflactores. |
| `pipeline/` | Scripts de Python y fuentes crudas (IDECBA, planillas 2027, agregados trimestrales). |

## Publicar

1. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Cada push a `main` publica el sitio en `https://tadeobessega.github.io/presupuesto-caba/`.

## Metodología (resumen)

- **Pesos de hoy**: IPCBA (IDECBA) septiembre de 2026. Promedios anuales desde 2013; 1995–2012 con la serie alternativa de la base CEER (IPC provincias), porque el IPC del INDEC 2007–2015 no es confiable.
- **Pesos de 2027**: pesos de hoy × 1,02³ (oct–dic 2026 al 2% mensual) × 1,18 (pauta de inflación 2027 del proyecto).
- **Gasto**: presupuesto ejecutado trimestral de BA Data (2019–2026 T2; 2020 y 2021 al cierre desde la base propia). Las amortizaciones de deuda se separan para comparar con el proyecto 2027.
- **Proyecto 2027**: Planillas Anexas (3, 4, 11, 16), presentación del 30/9/2026 y versión taquigráfica de la Comisión de Presupuesto del 7/10/2026.

## Reconstruir

```bash
cd pipeline/scripts
python3 build_gasto.py     # base de gasto (necesita raw/gasto y la Sheet1 propia)
python3 prep.py            # deflactores, CAIF, planillas 2027
python3 reca.py            # recaudación mensual
python3 build_data.py      # data/dashboard.json
python3 build_site.py      # index.html
```
Los scripts usan rutas de la sesión de trabajo original (`/home/claude/work`); ajustarlas antes de correrlos.
