from graphviz import Digraph

dot = Digraph(comment='Diagrama de Flujo del Modelo de Simulación')

# Entidades
dot.node('P', 'Pasajero')
dot.node('Par', 'Parada')
dot.node('B', 'Bus')

# Procesos
dot.node('GP', 'Generación de Pasajeros')
dot.node('AB', 'Abordaje/Bajada de Pasajeros')
dot.node('RB', 'Recorrido del Bus')

# Conexiones Correctas
dot.edge('P', 'GP')        # Pasajero -> Generación de Pasajeros
dot.edge('GP', 'Par')      # Generación de Pasajeros -> Parada
dot.edge('Par', 'AB')      # Parada -> Abordaje/Bajada de Pasajeros
dot.edge('AB', 'B')        # Abordaje/Bajada de Pasajeros -> Bus
dot.edge('B', 'RB')        # Bus -> Recorrido del Bus
dot.edge('RB', 'Par')      # Recorrido del Bus -> Parada siguiente

# Renderizar el diagrama
dot.render('figura3_diagrama_flujo_simulacion', view=True)
