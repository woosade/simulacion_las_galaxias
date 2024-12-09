# Simulación - Modelación y Simulación de Operaciones de Transporte Público: Análisis de la Línea "Las Galaxias"

**Fecha:** 09 de diciembre de 2024  
**Grupo 11**  
- José Patricio Galaz Norambuena (2019901010)  
- Gabriela Paz Flores Hormazábal (2021450556)  
- Francisca Andrea Molina Torres (2021044019)  
- Krishna Belén Riquelme Balboa (2021445625)  
- Cristóbal Emilio Game Jiménez (2021433708)

---

## Descripción General

Este repositorio contiene un proyecto de modelación y simulación dirigido a comprender y analizar la operación de la línea de transporte público “Las Galaxias”. Se busca simular la operación durante una semana completa, considerando datos reales (plan de operación, multas, rutas) y realizando supuestos justificados sobre la demanda y otros parámetros. La simulación se ejecuta principalmente en Python, utilizando la biblioteca `simpy` para la modelación de eventos discretos y `matplotlib` para la generación de gráficos.

Se incluye el análisis de escenarios adicionales a la situación actual:
- **Escenario de flota aumentada**: Añadir buses adicionales en horas punta y no punta, comparando el desempeño con el escenario base.
- **Escenario de ruta alternativa (aeropuerto)**: Modificar la ruta original para incluir un desvío hacia el aeropuerto, evaluando el impacto en las métricas de servicio.

Los principales indicadores calculados incluyen:
- Cantidad de pasajeros atendidos por parada y expedición.
- Tasa de ocupación promedio de los buses.
- Distribución de tiempos de espera de los pasajeros.
- Pasajeros no atendidos por parada.
- Multas acumuladas por atrasos (identificando nodos críticos).

Este modelo puede servir como herramienta de apoyo a la toma de decisiones sobre el diseño de la operación del transporte público, la gestión de flotas y el análisis de nuevas variantes de ruta.

---

## Estructura del Repositorio

- **`main.py`**:  
  Archivo principal de la simulación. Aquí se configuran los escenarios (base, flota aumentada, ruta alternativa) a través de variables booleanas.  
  - Simula 7 días (TIEMPO_SIMULACION ajustable).  
  - Carga datos reales (multas, POT, rutas) y aplica supuestos en demanda.  
  - Ejecuta el modelo y genera resultados (CSV y gráficos PNG).  
  - Guarda resultados en la carpeta `escenarios/<nombre_scenario>`.

- **`main_basic.py`**:  
  Una versión más sencilla del main, sin guardado automático de gráficos ni logs. Útil para demostraciones rápidas.

- **`data_loader.py`**:  
  Contiene la clase `DataLoader` para cargar y parsear datos desde archivos Excel (multas, POT, Rutas). Facilita el acceso estandarizado a la información.

- **`entities.py`**:  
  Define las entidades centrales del modelo:
  - `Pasajero`: Objeto que representa a un usuario del transporte, con origen, destino y tiempos registrados.
  - `Parada`: Genera pasajeros según una tasa de llegada, mantiene una cola y registra pasajeros no atendidos.
  - `Bus`: Simula el recorrido de un bus por la ruta, maneja subidas/bajadas de pasajeros, registra tiempos de espera, ocupación, multas por atraso.

- **`utils.py`**:  
  Funciones auxiliares como `es_horario_punta(...)` que determina si un tiempo dado corresponde a horario punta.

- **`figure3.py`**:  
  Script para generar la **Figura 3: Diagrama de Flujo del Modelo de Simulación**. Utiliza la biblioteca `graphviz` para crear y exportar el diagrama en formato PDF.  
  - **Uso**: Ejecutar el script para generar el diagrama.
  - **Salida**: `figura3_diagrama_flujo_simulacion.pdf` en el directorio actual.

- **`figure4.py`**:  
  Script para generar la **Figura 4: Esquema de la Ruta Base y Alternativa**. Emplea `graphviz` para ilustrar las rutas operativas de la línea “Las Galaxias”, incluyendo la ruta alternativa hacia el aeropuerto.  
  - **Uso**: Ejecutar el script para generar el esquema de rutas.
  - **Salida**: `figura4_esquema_ruta.pdf` en el directorio actual.

- **Datos de entrada**:
  - `Base de Multas Septiembre-Octubre 2024 depurada para estudiantes.xlsx`
  - `POT_VIII_GRAN+CONCEPCIÃ_N_UN80_NORMAL_2024_A1_5.xlsx`
  - `Rutas_Operacion.xlsx`
  - (Opcional) Documentos PDF informativos y EOD.

- **`requirements.txt`**:  
  Lista de dependencias de Python necesarias para ejecutar el proyecto. Incluye `simpy`, `pandas`, `matplotlib`, `graphviz`.

- **`escenarios/`**:  
  Carpeta donde se generan subcarpetas según el escenario ejecutado (por ejemplo `escenarios/base`, `escenarios/flota_aumentada`, `escenarios/ruta_alternativa`), guardando:
  - `log.txt`: registro de la salida estándar del programa.
  - Archivos CSV con datos de ocupación, subidas, bajadas, tiempos de espera, pasajeros no atendidos, multas.
  - Gráficos PNG generados.

---

## Requisitos y Preparación del Entorno

**Requerimientos:**
- Python 3.8 o superior.

**Instalación de dependencias:**
```bash
pip install -r requirements.txt
