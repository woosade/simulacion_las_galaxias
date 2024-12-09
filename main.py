import simpy
import matplotlib
matplotlib.use('Agg')  # Para no abrir ventanas de matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import os
import sys

from data_loader import DataLoader
from entities import Parada, Bus
from utils import es_horario_punta

# ----------------------------------------------------------
# CONFIGURACIONES DE ESCENARIO
#
# Puedes activar sólo uno de estos escenarios a la vez:
#
# ESCENARIO_BASE = True        -> Operación base sin buses adicionales ni ruta alternativa.
# ESCENARIO_FLOTA_AUMENTADA = False  -> Si True, se añaden más buses en punta/no punta.
# ESCENARIO_RUTA_ALTERNATIVA = False -> Si True, se usa la ruta alternativa (ej. aeropuerto).
#
# Ajusta estos valores antes de ejecutar.
# ----------------------------------------------------------

ESCENARIO_BASE = True
ESCENARIO_FLOTA_AUMENTADA = False
ESCENARIO_RUTA_ALTERNATIVA = False

# Determinar nombre del escenario
if ESCENARIO_BASE:
    scenario = "base"
elif ESCENARIO_FLOTA_AUMENTADA:
    scenario = "flota_aumentada"
elif ESCENARIO_RUTA_ALTERNATIVA:
    scenario = "ruta_alternativa"
else:
    scenario = "otro"

# Crear carpeta para guardar resultados del escenario
os.makedirs(f"escenarios/{scenario}", exist_ok=True)

# Opcional: Redirigir la salida estándar a un archivo de texto del escenario
log_path = f"escenarios/{scenario}/log.txt"
log_file = open(log_path, 'w')
orig_stdout = sys.stdout
sys.stdout = log_file

# ----------------------------------------------------------
# CONFIGURACIONES Y SUPUESTOS GENERALES
#
# Simulamos una semana (7 días)
# ----------------------------------------------------------
TIEMPO_SIMULACION = 7 * 24 * 3600  # 7 días

random.seed(42)
np.random.seed(42)

# Archivos reales (ajusta las rutas de los archivos si es necesario)
file_multas = 'Base de Multas Septiembre-Octubre 2024 depurada para estudiantes.xlsx'
file_pot = 'POT_VIII_GRAN+CONCEPCIÃ_N_UN80_NORMAL_2024_A1_5.xlsx'
file_rutas = 'Rutas_Operacion.xlsx'

data_loader = DataLoader(file_multas, file_pot, file_rutas)
data_loader.set_print_options(print_data=False, print_all=False, print_limit=5)
data_loader.load_all_data()

pot_parsed = data_loader.get_pot_parsed()
rutas_data = data_loader.get_rutas_data()

# Selección de un servicio (ejemplo: 80J IDA)
servicio_select = '80J'
rutas_servicios = rutas_data["Servicios"]
serv = rutas_servicios[rutas_servicios['Servicio'] == servicio_select].iloc[0]
origen = serv['Origen']
destino = serv['Destino']
distancia = serv['Distancia (km)']

# Supuestos de demanda según EOD: ALTA
tipo_demanda_ej = 'ALTA'
mapeo_demanda = {'BAJA': 0.5, 'MEDIA': 1.0, 'ALTA': 1.5}
base_tasa = 0.013  # Supuesto

tasa_llegada = base_tasa * mapeo_demanda[tipo_demanda_ej]

# Frecuencia base ALTA = 6 buses/hr
frecuencia_buses_hr = 6
intervalo_salida = 3600 / frecuencia_buses_hr

# Parámetros generales
CAPACIDAD_BUS = 50
TIEMPO_SUBIDA = 2
TIEMPO_BAJADA = 1
COSTO_MULTA = 1000
HORARIOS_PUNTA = [(7*3600, 9*3600), (17*3600, 19*3600)]
tiempo_por_km = 60
n_tramos = 3
tramo_s = (distancia * tiempo_por_km) / n_tramos

# Ruta base
RUTA_PARADAS = []
for i in range(n_tramos+1):
    nombre_parada = f"Parada {i+1} ({origen if i==0 else (destino if i==n_tramos else 'Intermedia')})"
    next_time = tramo_s if i < n_tramos else 0
    RUTA_PARADAS.append({'nombre': nombre_parada, 'tiempo_hasta_siguiente': next_time})

# Ruta alternativa (ej: aeropuerto)
RUTA_ALTERNATIVA = [
    {'nombre': f"Parada 1 ({origen})", 'tiempo_hasta_siguiente': tramo_s},
    {'nombre': 'Parada Aeropuerto', 'tiempo_hasta_siguiente': tramo_s+200},
    {'nombre': f"Parada Final ({destino})", 'tiempo_hasta_siguiente': 0}
]

DEMANDA_PARADAS = {}
for p in RUTA_PARADAS:
    if 'Intermedia' in p['nombre']:
        factor = mapeo_demanda['MEDIA']
    elif 'Dest' in p['nombre']:
        factor = mapeo_demanda['BAJA']
    else:
        factor = mapeo_demanda[tipo_demanda_ej]
    DEMANDA_PARADAS[p['nombre']] = {
        'llegada': tasa_llegada * factor,
        'destinos': [RUTA_PARADAS[-1]['nombre']] if p != RUTA_PARADAS[-1] else []
    }

DEMANDA_PARADAS_ALTERNATIVA = {}
for p in RUTA_ALTERNATIVA:
    if 'Aeropuerto' in p['nombre']:
        factor = mapeo_demanda['MEDIA']
    elif 'Final' in p['nombre']:
        factor = mapeo_demanda['BAJA']
    else:
        factor = mapeo_demanda[tipo_demanda_ej]

    DEMANDA_PARADAS_ALTERNATIVA[p['nombre']] = {
        'llegada': tasa_llegada * factor,
        'destinos': [RUTA_ALTERNATIVA[-1]['nombre']] if p != RUTA_ALTERNATIVA[-1] else []
    }

if ESCENARIO_RUTA_ALTERNATIVA:
    ruta_sim = RUTA_ALTERNATIVA
    demanda_sim = DEMANDA_PARADAS_ALTERNATIVA
else:
    ruta_sim = RUTA_PARADAS
    demanda_sim = DEMANDA_PARADAS

env = simpy.Environment()
paradas_dict = {}
for p in demanda_sim.keys():
    paradas_dict[p] = Parada(env, p, demanda_sim)

tiempos_espera = []
lista_buses = []

def programa_buses(env):
    tiempo_actual = 0
    bus_id = 0
    while tiempo_actual < TIEMPO_SIMULACION:
        if ESCENARIO_BASE:
            buses_adicionales = 0
        elif ESCENARIO_FLOTA_AUMENTADA:
            if es_horario_punta(tiempo_actual, HORARIOS_PUNTA):
                buses_adicionales = 2
            else:
                buses_adicionales = 1
        else:
            if es_horario_punta(tiempo_actual, HORARIOS_PUNTA):
                buses_adicionales = 2
            else:
                buses_adicionales = 1

        for _ in range(1 + buses_adicionales):
            bus = Bus(env, bus_id, ruta_sim, CAPACIDAD_BUS, tiempo_actual, paradas_dict, tiempos_espera,
                      COSTO_MULTA, TIEMPO_SUBIDA, TIEMPO_BAJADA)
            lista_buses.append(bus)
            bus_id += 1

        tiempo_actual += intervalo_salida
        yield env.timeout(0)

env.process(programa_buses(env))
env.run(until=TIEMPO_SIMULACION)

# Análisis de resultados
datos_ocupacion = []
datos_subidas = []
datos_bajadas = []
datos_multas = []
total_multas = 0
for bus in lista_buses:
    datos_ocupacion.extend(bus.registro_ocupacion)
    datos_subidas.extend(bus.registro_subidas)
    datos_bajadas.extend(bus.registro_bajadas)
    datos_multas.extend(bus.registro_multas)
    total_multas += bus.multas_acumuladas

df_ocupacion = pd.DataFrame(datos_ocupacion)
df_subidas = pd.DataFrame(datos_subidas)
df_bajadas = pd.DataFrame(datos_bajadas)
df_multas = pd.DataFrame(datos_multas)

print("\n=== RESULTADOS DE LA SIMULACIÓN ===")
print(f"Escenario: {scenario}")
print(f"Total de pasajeros atendidos: {len(tiempos_espera)}")
tiempos_espera_min = [t/60 for t in tiempos_espera]
pasajeros_no_atendidos = {p.nombre: p.pasajeros_no_atendidos for p in paradas_dict.values()}

# Guardar datos en CSV
df_ocupacion.to_csv(f"escenarios/{scenario}/datos_ocupacion.csv", index=False)
df_subidas.to_csv(f"escenarios/{scenario}/datos_subidas.csv", index=False)
df_bajadas.to_csv(f"escenarios/{scenario}/datos_bajadas.csv", index=False)
df_multas.to_csv(f"escenarios/{scenario}/datos_multas.csv", index=False)

# También guardar tiempos_espera y pasajeros_no_atendidos
pd.DataFrame({'tiempo_espera_min': tiempos_espera_min}).to_csv(f"escenarios/{scenario}/tiempos_espera.csv", index=False)
pd.DataFrame(list(pasajeros_no_atendidos.items()), columns=['parada','no_atendidos']).to_csv(f"escenarios/{scenario}/pasajeros_no_atendidos.csv", index=False)

if not df_ocupacion.empty:
    ocupacion_promedio = df_ocupacion.groupby('parada')['ocupacion'].mean()
    print("\nOcupación promedio por parada (%):")
    print(ocupacion_promedio)
    plt.figure()
    ocupacion_promedio.plot(kind='bar')
    plt.xlabel('Parada')
    plt.ylabel('Ocupación promedio (%)')
    plt.title('Ocupación promedio por parada')
    plt.tight_layout()
    plt.savefig(f"escenarios/{scenario}/ocupacion_promedio_por_parada.png", bbox_inches='tight')
    plt.close()

if tiempos_espera_min:
    print("\nEstadísticas de tiempos de espera (min):")
    desc_espera = pd.Series(tiempos_espera_min).describe()
    print(desc_espera)
    plt.figure()
    plt.hist(tiempos_espera_min, bins=50, edgecolor='black')
    plt.xlabel('Tiempo de espera (min)')
    plt.ylabel('Número de pasajeros')
    plt.title('Distribución de tiempos de espera')
    plt.tight_layout()
    plt.savefig(f"escenarios/{scenario}/distribucion_tiempos_espera.png", bbox_inches='tight')
    plt.close()

if not df_multas.empty:
    multas_por_parada = df_multas['parada'].value_counts()
    print("\nMultas por atraso por parada:")
    print(multas_por_parada)
    plt.figure()
    multas_por_parada.plot(kind='bar')
    plt.xlabel('Parada')
    plt.ylabel('Número de multas')
    plt.title('Multas por atraso por parada')
    plt.tight_layout()
    plt.savefig(f"escenarios/{scenario}/multas_por_parada.png", bbox_inches='tight')
    plt.close()
else:
    print("No se registraron multas durante la simulación.")

print(f"\nTotal de multas acumuladas: {total_multas} unidades monetarias")
print("Pasajeros no atendidos por parada:")
for parada, cantidad in pasajeros_no_atendidos.items():
    print(f"{parada}: {cantidad}")

print("\n=== FIN DE LA SIMULACIÓN ===")
print("Nota: Todos los supuestos y simplificaciones han sido documentados en el código.")
print("Favor referirse al informe para mayor detalle y justificación de dichos supuestos.")

# Restaurar stdout
sys.stdout = orig_stdout
log_file.close()

print(f"Simulación finalizada. Resultados y logs en 'escenarios/{scenario}'")
