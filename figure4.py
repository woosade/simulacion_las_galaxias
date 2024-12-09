from graphviz import Digraph

dot = Digraph(comment='Esquema de la Ruta Base y Alternativa')

# Ruta Base
dot.node('H', 'Hualqui (Santa Josefina)', shape='ellipse', color='blue')
dot.node('C', 'Chiguayante', shape='ellipse', color='blue')
dot.node('Con', 'Concepción', shape='ellipse', color='blue')
dot.node('SV', 'San Vicente', shape='ellipse', color='blue')
dot.node('T', 'Talcahuano', shape='ellipse', color='blue')

# Ruta Alternativa
dot.node('Aero', 'Aeropuerto', shape='ellipse', color='red')
dot.node('Final', 'San Vicente', shape='ellipse', color='blue')  # Reutilizando SV

# Conexiones Ruta Base
dot.edge('H', 'C', label='Ruta Base', color='blue')
dot.edge('C', 'Con', label='Ruta Base', color='blue')
dot.edge('Con', 'SV', label='Ruta Base', color='blue')
dot.edge('SV', 'T', label='Ruta Base', color='blue')

# Conexiones Ruta Alternativa
dot.edge('H', 'Aero', label='Ruta Alternativa', color='red')
dot.edge('Aero', 'SV', label='Ruta Alternativa', color='red')

# Renderizar el diagrama
dot.render('figura4_esquema_ruta', view=True)
