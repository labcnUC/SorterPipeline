# Configura Jupyter para usar widgets (esto debe estar en una celda separada en Jupyter)
# Dec 05 2024: Germán: se modifica la subrutina Analyzer para que no guarde el analisis del sorting, buscando evitar el error 22 que ocurre en algunos sistemas.
# Dec 16 2024: Germán: se incorpora un logger para recopilar informacion sobre errores.

import logging
from pathlib import Path
import pandas as pd
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
import os

# Logger setup
def setup_logger(log_file="execution_log.log", log_level=logging.INFO):
    """
    Configura un logger para recopilar errores, advertencias e información.

    Args:
        log_file (str): Nombre del archivo donde se guardarán los logs.
        log_level (int): Nivel mínimo de los mensajes a registrar (INFO, WARNING, ERROR, etc.).

    Returns:
        logger: Objeto logger configurado.
    """
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SpikeSortingLogger")
    logger.setLevel(log_level)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logger(log_file="logs/spike_sorting.log", log_level=logging.INFO)

def log_and_print(msg, level="info"):
    """
    Imprime un mensaje en consola y lo registra en el logger.

    Args:
        msg (str): Mensaje a imprimir y registrar.
        level (str): Nivel del logger. Puede ser "info", "warning", "error", etc.
    """
    print(msg)
    if level == "info":
        logger.info(msg)
    elif level == "warning":
        logger.warning(msg)
    elif level == "error":
        logger.error(msg)
    elif level == "debug":
        logger.debug(msg)
    else:
        logger.info(msg)

# Modified functions to include logging

def read_rhd(rhd_folder):
    rhd_folder_path = Path(rhd_folder)
    rhd_files = list(rhd_folder_path.rglob('*.rhd'))
    recordings = []

    if not rhd_files:
        log_and_print("No se encontraron archivos .rhd en la carpeta.", level="warning")
        return None
    else:
        recordings = [read_intan(file, stream_name='RHD2000 amplifier channel') for file in rhd_files]

    if len(recordings) > 1:
        recording = si.concatenate_recordings(recordings)
        log_and_print(f"Concatenados {len(rhd_files)} archivos .rhd: {[file.name for file in rhd_files]}", level="info")
    else:
        recording = recordings[0]
        log_and_print(f"Procesado 1 archivo .rhd: {rhd_files[0].name}", level="info")

    return recording

def get_recording(file_data_folder, artifacts, probegroup_file):
    try:
        probegroup = pi.read_probeinterface(probegroup_file)
        log_and_print(f"Archivo de probegroup utilizado: {probegroup_file}", level="info")

        file_data_folder = Path(file_data_folder)
        recording = read_rhd(file_data_folder)

        if recording is None:
            log_and_print(f"No se pudo leer la grabación en {file_data_folder}.", level="error")
            return None

        num_samples = recording.get_num_samples()
        total_duration = recording.get_total_duration()
        fs = int(num_samples / total_duration)
        log_and_print(f"Grabación leída con {num_samples} muestras y duración total de {total_duration} segundos. Frecuencia de muestreo calculada: {fs} Hz.", level="info")

        list_triggers, ms_before, ms_after = process_artifacts(artifacts, file_data_folder, fs)

        recording = prep.bandpass_filter(recording, freq_min=500., freq_max=9000.)
        log_and_print("Filtro pasa banda aplicado: 500-9000 Hz.", level="info")

        recording = recording.set_probegroup(probegroup, group_mode='by_probe')
        log_and_print("Probegroup configurado para la grabación.", level="info")

        if list_triggers is not None and len(list_triggers) > 0:
            recording = prep.remove_artifacts(
                recording=recording,
                list_triggers=list_triggers,
                ms_after=500,
                mode="zeros"
            )
            log_and_print(f"Artefactos removidos. Triggers utilizados: {list_triggers}", level="info")

        log_and_print("Procesamiento de archivo completado.", level="info")
        return recording

    except Exception as e:
        log_and_print(f"Error crítico en el procesamiento de archivos: {e}", level="error")
        return None

    except Exception as e:
        logger.error(f"Error crítico en el procesamiento de archivos: {e}")
        return None

def check_concatenation(record_maze, record_sleep):
    """
    Concatenar los registros de Maze y Sueño después de igualar los IDs de canal.
    
    Args:
        record_maze: Objeto de grabación del registro de Maze.
        record_sleep: Objeto de grabación del registro de Sueño.
    
    Returns:
        final_recording: Grabación concatenada o única disponible.
    """
    # Verifica que ambos registros estén disponibles
    if record_maze is not None and record_sleep is not None:
        # Igualar IDs de canales entre Maze y Sueño
        chan_ids = record_maze.get_channel_ids()
        
        # Renombrar canales en record_sleep
        record_sleep = record_sleep.rename_channels(chan_ids)
        
        # Concatenar grabaciones de Maze y Sueño
        final_recording = si.concatenate_recordings([record_maze, record_sleep])
        print("Registros de Maze y Sueño concatenados exitosamente.")
    else:
        # Si solo hay un registro, usarlo como final
        final_recording = record_maze if record_maze is not None else record_sleep
        if final_recording is not None:
            print("Solo un registro disponible para concatenar.")
        else:
            print("No hay registros disponibles para concatenar.")
    
    return final_recording

def process_artifacts(partial_artifact_name, base_folder, fs):
    """
    Procesa artefactos de un archivo HDF5 específico para identificar eventos y generar triggers.

    La función busca un archivo en `base_folder` cuyo nombre comience con 'LAN' y termine en '500.mat'.
    Luego, busca dentro del archivo HDF5 un dataset cuyo nombre contenga la subcadena `partial_artifact_name`.
    Si se encuentra, extrae información de los artefactos y calcula los triggers correspondientes.

    Parámetros:
    ----------
    partial_artifact_name : str
        Subcadena que debe contener el nombre del dataset en el archivo HDF5 para identificar los artefactos.
    base_folder : str
        Ruta de la carpeta base donde se encuentra el archivo LAN.
    fs : int
        Frecuencia de muestreo deseada para la señal de salida en Hz.

    Retorno:
    -------
    list_triggers : list of int
        Lista de posiciones de los triggers en muestras, indicando el inicio de los segmentos sin artefacto.
    ms_before : int
        Tiempo en milisegundos antes de cada trigger.
    ms_after : int
        Tiempo en milisegundos después de cada trigger.

    Notas:
    -----
    - Si no se encuentra un archivo que cumpla con los criterios, o no se encuentra el dataset con la subcadena
      especificada, la función retorna listas vacías y valores predeterminados de `ms_before` y `ms_after`.
    - La función `crear_vectores_acumulados` se utiliza para generar triggers acumulados basados en
      `list_ini` y `list_fin`, que representan los índices de inicio y fin de cada artefacto.
    """
    try:
        # Listar todos los archivos en el folder base
        all_files = os.listdir(base_folder)
        lan_file = [lan_file for lan_file in all_files if lan_file.startswith('LAN') and lan_file.endswith('_500.mat')]

        if not lan_file:
            log_and_print("No se encontró ningún archivo LAN en el directorio especificado.", level="warning")
            log_and_print("\033[31mSe omite la remoción de artefactos\033[0m", level="warning")
            return [], [], []  # Retornar listas vacías y continuar

        path_lan = os.path.join(base_folder, lan_file[0])
        log_and_print(f"Ruta del archivo LAN: {path_lan}", level="info")

        # Leer el archivo HDF5
        with h5py.File(path_lan, 'r') as LAN:
            LAN = LAN['LAN']

            # Buscar el dataset cuyo nombre contiene la subcadena especificada
            artifact_name = None
            for name in LAN.keys():
                if partial_artifact_name in name:
                    artifact_name = name
                    break

            if artifact_name is None:
                log_and_print(f"No se encontró un dataset que contenga '{partial_artifact_name}' en el archivo HDF5.", level="warning")
                log_and_print("\033[31mSe omite la remoción de artefactos\033[0m", level="warning")
                return [], [], []

            # Continuar con el proceso una vez encontrado el nombre completo
            log_and_print(f"Dataset encontrado: {artifact_name}", level="info")
            sf_ref = LAN['srate']
            srate = sf_ref[()][0]
            selected_ref = LAN[artifact_name]

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
            list_ini = np.array(ind_ini / srate) * fs
            list_ini = list_ini.astype(int)

            list_fin = np.array(ind_fin / srate) * fs
            list_fin = list_fin.astype(int)

            # Crear los triggers acumulados
            list_triggers = crear_vectores_acumulados(0.1 * fs, list_ini, list_fin)

            # Tiempos antes y después del artefacto
            ms_before = 0  # 0 ms antes del trigger
            ms_after = 500  # 500 ms después del trigger

        return list_triggers, ms_before, ms_after
    
    except Exception as e:
        log_and_print(f"Error procesando artefactos: {e}", level="error")
        return [], [], []

# Function to recreate experiment
def recreate_experiment(log_file):
    """
    Lee un archivo de log para extraer las rutas de archivos y variables clave.

    Args:
        log_file (str): Ruta del archivo de log.

    Returns:
        dict: Diccionario con información para recrear el experimento.
    """
    import re
    experiment_data = {}

    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()

            # Extraer rutas de archivos
            for line in lines:
                if "Concatenados" in line:
                    match = re.search(r"archivos \.rhd: \[(.*)\]", line)
                    if match:
                        experiment_data["rhd_files"] = match.group(1).split(", ")

                if "Archivo de probegroup utilizado" in line:
                    match = re.search(r"utilizado: (.+)", line)
                    if match:
                        experiment_data["probegroup_file"] = match.group(1)

                if "Ruta del archivo LAN" in line:
                    match = re.search(r"LAN: (.+)", line)
                    if match:
                        experiment_data["lan_file"] = match.group(1)

                if "Frecuencia de muestreo calculada" in line:
                    match = re.search(r"calculada: (\d+) Hz", line)
                    if match:
                        experiment_data["fs"] = int(match.group(1))

                if "Triggers utilizados" in line:
                    match = re.search(r"Triggers utilizados: (\[.*\])", line)
                    if match:
                        experiment_data["triggers"] = eval(match.group(1))

        return experiment_data

    except Exception as e:
        log_and_print(f"Error leyendo el archivo de log: {e}", level="error")
        return None

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
                                                      sparse=True)

        # Compute necessary metrics
        sorting_analyzer.compute(['random_spikes','noise_levels','correlograms'])
        sorting_analyzer.compute(['waveforms', 'principal_components', 'templates', ])
        sorting_analyzer.compute(['spike_amplitudes', 'template_similarity', 'unit_locations'],)
        
        # Compute quality metrics
        sorting_analyzer.compute('quality_metrics', metric_names=["snr", "firing_rate"], skip_pc_metrics=True)
        
        return sorting_analyzer
    
    except Exception as e:
        log_and_print(f"Error crítico en el analisis de archivos: {e}", level="error")
        print(f"An error occurred: {e}")
        return None

def create_folders(base_name, group=False):
    prefix = 'group_' if group else ''
    sorter_folder = Path(f'output/AN/kilosort/{prefix}sorter_{base_name}')
    analyzer_folder = Path(f'output/AN/kilosort/{prefix}analyzer_{base_name}')
    phy_output_folder = Path(f'output/AN/kilosort/{prefix}phy_{base_name}')
    
    return sorter_folder, analyzer_folder, phy_output_folder
