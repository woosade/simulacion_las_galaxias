import simpy
import random

class Pasajero:
    def __init__(self, env, id_pasajero, origen, destino, tiempo_llegada):
        self.env = env
        self.id_pasajero = id_pasajero
        self.origen = origen
        self.destino = destino
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_abordaje = None  # Se asigna cuando sube al bus

class Parada:
    def __init__(self, env, nombre, demanda_paradas):
        self.env = env
        self.nombre = nombre
        self.cola = []
        self.total_pasajeros = 0
        self.pasajeros_no_atendidos = 0
        self.demanda_paradas = demanda_paradas
        self.env.process(self.generar_pasajeros())

    def generar_pasajeros(self):
        while True:
            llegada = self.demanda_paradas[self.nombre]['llegada']
            destinos = self.demanda_paradas[self.nombre]['destinos']

            # Si no hay destinos, no generar pasajeros en esta parada
            if not destinos:
                # Espera un tiempo antes de volver a chequear
                yield self.env.timeout(1)
                continue

            if llegada > 0:
                tiempo_llegada = random.expovariate(llegada)
                yield self.env.timeout(tiempo_llegada)
                destino = random.choice(destinos)
                pasajero = Pasajero(self.env, f"{self.nombre}_{self.total_pasajeros}", self.nombre, destino, self.env.now)
                self.cola.append(pasajero)
                self.total_pasajeros += 1
            else:
                yield self.env.timeout(1)  # Espera si no hay demanda

class Bus:
    def __init__(self, env, id_bus, ruta, capacidad, hora_salida, paradas_dict, tiempos_espera,
                 costo_multa=1000, tiempo_subida=2, tiempo_bajada=1):
        self.env = env
        self.id_bus = id_bus
        self.ruta = ruta
        self.capacidad = capacidad
        self.hora_salida = hora_salida
        self.paradas_dict = paradas_dict
        self.tiempos_espera = tiempos_espera
        self.costo_multa = costo_multa
        self.tiempo_subida = tiempo_subida
        self.tiempo_bajada = tiempo_bajada

        self.pasajeros = []
        self.registro_ocupacion = []
        self.tiempo_inicio = env.now
        self.multas_acumuladas = 0
        self.registro_multas = []
        self.registro_subidas = []
        self.registro_bajadas = []
        self.env.process(self.recorrer_ruta())

    def recorrer_ruta(self):
        # Esperar hasta la hora de salida
        yield self.env.timeout(self.hora_salida - self.env.now)
        tiempo_programado = self.hora_salida

        for parada in self.ruta:
            tiempo_llegada = self.env.now
            # Verificar atraso
            if tiempo_llegada > tiempo_programado:
                atraso = tiempo_llegada - tiempo_programado
                self.multas_acumuladas += self.costo_multa
                self.registro_multas.append({
                    'bus_id': self.id_bus,
                    'parada': parada['nombre'],
                    'tiempo_atraso': atraso,
                    'costo_multa': self.costo_multa,
                })
            # Bajada de pasajeros
            pasajeros_a_bajar = [p for p in self.pasajeros if p.destino == parada['nombre']]
            for pasajero in pasajeros_a_bajar:
                yield self.env.timeout(self.tiempo_bajada)
                self.pasajeros.remove(pasajero)
                self.registro_bajadas.append({
                    'bus_id': self.id_bus,
                    'tiempo': self.env.now,
                    'parada': parada['nombre'],
                    'pasajero_id': pasajero.id_pasajero
                })

            # Subida de pasajeros
            parada_obj = self.paradas_dict[parada['nombre']]
            while parada_obj.cola:
                if len(self.pasajeros) < self.capacidad:
                    pasajero = parada_obj.cola.pop(0)
                    pasajero.tiempo_abordaje = self.env.now
                    tiempo_espera_pasajero = pasajero.tiempo_abordaje - pasajero.tiempo_llegada
                    self.tiempos_espera.append(tiempo_espera_pasajero)
                    yield self.env.timeout(self.tiempo_subida)
                    self.pasajeros.append(pasajero)
                    self.registro_subidas.append({
                        'bus_id': self.id_bus,
                        'tiempo': self.env.now,
                        'parada': parada['nombre'],
                        'pasajero_id': pasajero.id_pasajero
                    })
                else:
                    # Bus lleno
                    parada_obj.pasajeros_no_atendidos += len(parada_obj.cola)
                    break

            ocupacion = len(self.pasajeros) / self.capacidad * 100
            self.registro_ocupacion.append({
                'bus_id': self.id_bus,
                'tiempo': self.env.now,
                'parada': parada['nombre'],
                'ocupacion': ocupacion,
                'pasajeros_a_bordo': len(self.pasajeros),
            })

            if parada['tiempo_hasta_siguiente'] > 0:
                tiempo_viaje = parada['tiempo_hasta_siguiente']
                tiempo_viaje *= random.uniform(0.8, 1.2)
                probabilidad_retraso = 0.1
                if random.random() < probabilidad_retraso:
                    retraso_adicional = random.expovariate(1/60)
                    tiempo_viaje += retraso_adicional
                yield self.env.timeout(tiempo_viaje)
                tiempo_programado += parada['tiempo_hasta_siguiente']
            else:
                # Última parada
                break
