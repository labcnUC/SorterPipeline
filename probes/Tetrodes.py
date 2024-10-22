import numpy as np
from probeinterface.plotting import plot_probe
from probeinterface import io
from probeinterface import Probe, ProbeGroup

def create_probe_matrix(contact_ids, channel_ids, Headstage):
    # Obtener la cantidad de grupos de contactos
    num_groups = len(np.unique(contact_ids))

    # Verificar si el número total de canales coincide con el tamaño del contacto
    if len(contact_ids) != len(channel_ids):
        print("Error: El tamaño del vector de contactos no coincide con el número total de canales.")
        return None

    # Crear matrices vacías para almacenar los canales y los IDs de contactos
    channel_matrix = np.empty((4, 4), dtype=int)
    contact_matrix = np.empty((4, 4), dtype=object)

    # Poblar la matriz con los ID de canal y de contacto en orden
    for i, contact_id in enumerate(np.unique(contact_ids)):
        row = i // 2
        col = i % 2
        start_index = i * num_groups
        end_index = start_index + num_groups
        channel_matrix[row * 2:row * 2 + 2, col * 2:col * 2 + 2] = np.reshape(channel_ids[start_index:end_index], (2, 2))
        contact_matrix[row * 2:row * 2 + 2, col * 2:col * 2 + 2] = np.char.add(np.char.add(np.char.add(np.full((2, 2), str(Headstage[0])), '-'), 
                                                                               np.reshape(contact_ids[start_index:end_index], (2, 2)).astype(str)),
                                                                               np.char.add(np.full((2, 2), '-'), np.reshape(channel_ids[start_index:end_index], (2, 2)).astype(str)))
                                
    return contact_matrix, channel_matrix

def create_and_print_probe(channel_ids, contact_ids, headstage):
    contact_matrix, channel_matrix = create_probe_matrix(contact_ids, channel_ids, headstage)
    probe = create_probe_from_matrix(channel_matrix, contact_matrix)
    print("Matriz de contactos:")
    print(contact_matrix)
    print("\nMatriz de canales:")
    print(channel_matrix)
    return probe

def create_probe_from_matrix(channel_matrix, contact_matrix):
    # Creamos una instancia de la clase Probe
    probe = Probe(ndim=2, si_units='um')

    # Configuramos las propiedades de los contactos utilizando la matriz
    positions = []
    shapes = []
    shape_params = []
    channel = []
    ID = []

    # Iteramos sobre la matriz para obtener la información de cada contacto
    for row in range(channel_matrix.shape[0]):
        for col in range(channel_matrix.shape[1]):
            x = col * 33  # Espaciamiento horizontal de 100 micrómetros
            y = row * 33  # Espaciamiento vertical de 100 micrómetros
            
            # Agregamos la posición del contacto
            positions.append([x, y])
            channel.append(channel_matrix[row][col])
            ID.append(contact_matrix[row][col])
            # Agregamos la forma del contacto (en este caso, un círculo)
            shapes.append('circle')

            # Agregamos los parámetros de la forma (diámetro de 30 micrómetros)
            shape_params.append({'radius': 15})

    # Establecemos los contactos en la sonda
    probe.set_contacts(positions=positions, shapes=shapes, shape_params=shape_params, contact_ids=ID)
    probe.set_device_channel_indices(channel_indices=channel)
    
    return probe

def write_probe(probe_name, probegroup):
    
    writer = io.write_probeinterface(file=(probe_name + "_probe.json"), probe_or_probegroup=probegroup)
    return writer
