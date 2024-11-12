import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import h5py
import scipy.io
import spikeinterface as si
import spikeinterface.preprocessing as prep
import spikeinterface.widgets as sw
import spikeinterface.sorters as ss
import spikeinterface.exporters as exp
import probeinterface as pi
from spikeinterface.extractors import read_intan
from probeinterface import Probe, ProbeGroup
import os  # Agregado

# Configura Jupyter para usar widgets (esto debe estar en una celda separada en Jupyter)

def read_rhd(rhd_folder):
    rhd_folder_path = Path(rhd_folder)
    rhd_files = list(rhd_folder_path.rglob('*.rhd'))  # Usa rglob para buscar recursivamente si es necesario
    recordings =[]
    
    if not rhd_files:
        print("No se encontraron archivos .rhd en la carpeta.")
        return None
    else:
        recordings = [read_intan(file, stream_name='RHD2000 amplifier channel') for file in rhd_files]
    
    if len(recordings) > 1:
        recording = si.concatenate_recordings(recordings)
        print(f"Concatenados {len(rhd_files)} archivos .rhd.")
    else:
        recording = recordings[0]
        print(f"Procesado 1 archivo .rhd.")
    
    return recording


def get_recording(excel_file, probegroup_file):
    try:
        df = pd.read_excel(Path(excel_file))
        probegroup = pi.read_probeinterface(probegroup_file)
        
        recordings = []
        diferencias = []
        
        for row in df.itertuples(index=False):
            file_data_folder = Path(row.data_folder)
            recording = read_rhd(file_data_folder)

            # frecuencia de sampleo registro original.
            
            sn=recording.get_num_samples()
            td=recording.get_total_duration()
            fs = (int(sn/ td))

            if recording is None:
                continue

            list_triggers, ms_before, ms_after = process_artifacts(row.artifacts, row.data_folder, fs)

            recording = prep.bandpass_filter(recording, freq_min=500., freq_max=9000.)
            recording = recording.set_probegroup(probegroup, group_mode='by_probe')
            if len(list_triggers) > 0:
                recording = prep.remove_artifacts(
                    recording=recording,
                    list_triggers=list_triggers,
                    mode="zeros"
                )
            
            recordings.append(recording)
        
        if len(recordings) > 1:
            final_recording = si.concatenate_recordings(recordings)
            print("Concatenados los siguientes registros:")
            for i, rec in enumerate(recordings, 1):
                print(f"Registro {i}: {rec}")
        elif recordings:
            final_recording = recordings[0]
            print("Solo un registro disponible para concatenar.")
        else:
            final_recording = None
            print("No se procesaron registros.")
        
        print("Procesamiento de archivos completado")
        return final_recording
    
    except Exception as e:
        print(f"Error crítico en el procesamiento de archivos: {e}")
        return None

def check_concatenation(record_maze, record_sleep):
    # Concatenar ambos registros
    if record_maze is not None and record_sleep is not None:
        # se igualan los ID de Maze y sueño, para esto se copian los ID de maze y se renombran los de sueño
        chan_ids=record_maze.get_channel_ids() 
        newid_sleep=newid_sleep.rename_channels(chan_ids)
        final_recording = si.concatenate_recordings([record_maze, newid_sleep])
        print("Registros de Maze y Sueño concatenados exitosamente.")
    else:
        final_recording = record_maze if record_maze is not None else record_sleep
        if final_recording is not None:
            print("Solo un registro disponible para concatenar.")
        else:
            print("No hay registros disponibles para concatenar.")
    return final_recording

def process_artifacts(artifacts, base_folder, fs):
    # Listar todos los archivos en el folder base
    all_files = os.listdir(base_folder)
    lan_file = [lan_file for lan_file in all_files if lan_file.startswith('LAN') and lan_file.endswith('500.mat')]
    
    if not lan_file:
        print("No se encontró ningún archivo LAN en el directorio especificado.")
        print("\033[31mSe omite la remoción de artefactos\033[0m")
        return [], [], []  # Retornar listas vacías y continuar
        
    path_lan = os.path.join(base_folder, lan_file[0])
    print (path_lan)
    # Leer el archivo HDF5
    with h5py.File(path_lan, 'r') as LAN:
        LAN = LAN['LAN']
        sf_ref = LAN['srate']
        srate = sf_ref[()][0]
        selected_ref = LAN[artifacts]
        
        # Procesar los artefactos
        selected = ~selected_ref[:]
        selected = selected.astype(int)
        selected_0 = np.insert(selected, 0, 0)
        dif = np.diff(selected_0)
        ind_ini = np.where(dif == 1)[0]
        ind_fin = np.where(dif == -1)[0]
        
        # Ajustar índices para que cada inicio tenga un fin correspondiente
        while len(ind_ini) != len(ind_fin):
            if ind_ini[-1] > ind_fin[-1]:
                ind_ini = ind_ini[:-1]
            if ind_fin[0] < ind_ini[0]:
                ind_fin = ind_fin[1:]
        
        # Calcular los triggers
        list_ini = np.array(ind_ini / srate)
        list_ini = list_ini * fs
        list_ini = list_ini.astype(int)

        list_fin = np.array(ind_fin / srate)
        list_fin = list_fin * fs
        list_fin = list_fin.astype(int)
        
        list_triggers = []
  
        list_triggers = crear_vectores_acumulados(0.1*fs,list_ini,list_fin)

        # Tiempos antes y después del artefacto
        ms_before = 0 #  zero before trigger
        ms_after = 500 # 500 ms after trigger <- punto para cambiar los segmentos que componen el artefacto.
        
    return list_triggers, ms_before, ms_after
    

def crear_vectores_acumulados(distancia, inicios, fines):
    # Lista para almacenar los valores acumulados de todos los vectores
    valores_acumulados = []
    
    # Iteramos sobre cada par de inicio y fin
    for inicio, fin in zip(inicios, fines):
        # Creamos el vector para el par actual
        vector = np.arange(inicio, fin, distancia)
        # Convertimos cada valor del vector a entero antes de añadirlo
        valores_acumulados.extend(vector.astype(int).tolist())  # Convertimos a int y luego extendemos
    
    # Convertimos la lista final a un array de NumPy de enteros
    return np.array(valores_acumulados, dtype=int)

def espigas(sorter):
    sorting = sorter

# Obtener el número de clusters
    unit_ids = sorter.get_unit_ids()
    num_clusters = len(unit_ids)

# Obtener el número total de espigas
    total_spikes = sum([len(sorting.get_unit_spike_train(unit_id)) for unit_id in unit_ids])
    return num_clusters, total_spikes

def sorting_analyzer(sorting, recording, output_folder):
    try:
        sorting_analyzer = si.create_sorting_analyzer(sorting=sorting, 
                                                      recording=recording, 
                                                      sparse=True,
                                                      format="binary_folder",
                                                      folder=output_folder)

        # Compute necessary metrics
        sorting_analyzer.compute(['random_spikes', 'waveforms', 'templates', 'noise_levels'])
        sorting_analyzer.compute(['principal_components', 'spike_amplitudes', 'template_similarity', 'unit_locations', 'correlograms'],)
        
        # Compute quality metrics
        sorting_analyzer.compute('quality_metrics', metric_names=["snr", "firing_rate"], skip_pc_metrics=True)
        
        return sorting_analyzer
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_folders(base_name, group=False):
    prefix = 'group_' if group else ''
    sorter_folder = Path(f'output/AN/kilosort/{prefix}sorter_{base_name}')
    analyzer_folder = Path(f'output/AN/kilosort/{prefix}analyzer_{base_name}')
    phy_output_folder = Path(f'output/AN/kilosort/{prefix}phy_{base_name}')
    
    return sorter_folder, analyzer_folder, phy_output_folder
