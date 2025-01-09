import os
import numpy as np
from pathlib import Path
import probeinterface as pi
import spikeinterface.extractors as se
import spikeinterface.core as si
import pandas as pd
from preprocessing_functions import read_rhd, get_recording, check_concatenation, process_artifacts, espigas, sorting_analyzer, create_folders

job_kwargs = dict(
    n_jobs=-1,
    chunk_duration='1s',
    progress_bar=True,
)

si.set_global_job_kwargs(**job_kwargs)

def waveform_miograma(root_folder, folder_names, bad_channels):
    """
    Extrae las formas de onda de datos de electrofisiología con miograma.

    Args:
        root_folder (str): Ruta principal donde se encuentran las carpetas con los resultados.
        folder_names (list): Lista de nombres de las carpetas que se quieren procesar (por días).
        bad_channels (list): Lista de nombres de canales a remover.
    """
    # Definir estructuras de carpetas
    folder_sorting = Path(root_folder, 'Sorting')
    folder_maze_base = Path(root_folder, 'Maze')
    artifact_maze_base = Path(root_folder, 'Maze')
    folder_sleep_base = Path(root_folder, 'Sleep')
    artifact_sleep_base = Path(root_folder, 'Sleep')

    for folder_name in folder_names:
        print(f"Procesando carpeta: {folder_name}")
        # Construir la ruta completa a la carpeta
        phy_folder = Path(folder_sorting, folder_name)

        folder_maze = Path(folder_maze_base, folder_name)
        artifact_maze = Path(artifact_maze_base, folder_name)
        folder_sleep = Path(folder_sleep_base, folder_name)
        artifact_sleep = Path(artifact_sleep_base, folder_name)

        waveforms_folder = Path(phy_folder,'waveforms')
        print (phy_folder)
        # lectura de archivos
        probegroup_file = 'probes/anillo_probe.json'
        probegroup = pi.read_probeinterface(probegroup_file)

        # 1. Cargar los resultados del sorting desde los archivos de Phy
        try:
            phy_sorting = se.read_phy(phy_folder,
                                      exclude_cluster_groups = 'noise')
        except Exception as e:
            print(f"Error al leer phy en {phy_folder}: {e}. Saltando carpeta")
            continue # Saltar a la siguiente carpeta si hay un error

        # 2. Cargar las grabaciones crudas asociadas y remover canales
        try:
            #
            record_maze = get_recording(folder_maze, "selected_", probegroup_file)
            record_sleep = get_recording(folder_sleep, "selected_", probegroup_file)
            recording = check_concatenation(record_maze, record_sleep)

            recording=recording.remove_channels(bad_channels) # removemos los canales aquí
        except Exception as e:
            print(f"Error al procesar grabaciones en {phy_folder}: {e}. Saltando carpeta")
            continue # Saltar a la siguiente carpeta si hay un error

        # 3. Extraer waveforms con el método antiguo
        try:
            we = si.extract_waveforms(recording,
                                phy_sorting,
                                folder=waveforms_folder,
                                ms_before=1.5,
                                ms_after=2.,
                                max_spikes_per_unit=20000000
                                )
        except Exception as e:
            print(f"Error al extraer waveforms en {phy_folder}: {e}. Saltando carpeta.")
            continue # Saltar a la siguiente carpeta si hay un error


        print(we.get_all_templates().shape)
        print("*********************************************************************")


def waveform_sinmiograma(root_folder, folder_names):
    """
    Extrae las formas de onda de datos de electrofisiología sin miograma.

    Args:
        root_folder (str): Ruta principal donde se encuentran las carpetas con los resultados.
        folder_names (list): Lista de nombres de las carpetas que se quieren procesar (por días).
    """
    for folder_name in folder_names:
        print(f"Procesando carpeta: {folder_name}")
        # Construir la ruta completa a la carpeta
        phy_folder = Path(root_folder, 'sorting', folder_name)
        waveforms_folder = Path(phy_folder,'waveforms')

        # lectura de archivos
        probegroup_file = 'probes/anillo_probe.json'
        probegroup = pi.read_probeinterface(probegroup_file)

        # Leer el archivo params.py
        params_path = os.path.join(phy_folder, 'params.py')
        params = {}
        with open(params_path, 'r') as f:
            try:
                exec(f.read(), {}, params)
            except Exception as e:
                print(f"Error al leer {params_path}: {e}. Saltando carpeta.")
                continue  # Saltar a la siguiente carpeta si hay un error

        # Extraer las variables necesarias de params.py
        dat_path = os.path.join(phy_folder, 'recording.dat')  # Ruta completa al archivo de datos crudos
        n_channels_dat = params.get('n_channels_dat')
        dtype = params.get('dtype')
        offset = params.get('offset',0)
        sample_rate = params.get('sample_rate')
        hp_filtered = params.get('hp_filtered',False)

        if not all([dat_path, n_channels_dat, dtype, sample_rate]):
                print(f"Error: Faltan datos en {params_path}. Saltando carpeta")
                continue


        # 1. Cargar los resultados del sorting desde los archivos de Phy
        try:
            phy_sorting = se.read_phy(phy_folder,
                            exclude_cluster_groups = 'noise')
        except Exception as e:
            print(f"Error al leer phy en {phy_folder}: {e}. Saltando carpeta")
            continue # Saltar a la siguiente carpeta si hay un error
        
        # 2. Cargar las grabaciones crudas asociadas
        try:
            recording = se.read_binary(
                file_paths=dat_path,
                sampling_frequency=sample_rate,
                dtype=dtype,
                num_channels=n_channels_dat
            )
        except Exception as e:
            print(f"Error al leer datos binarios en {dat_path}: {e}. Saltando carpeta.")
            continue # Saltar a la siguiente carpeta si hay un error
        
        # 2.1. asignar info de la sonda y el offset
        try:
            recording = recording.set_probegroup(probegroup)
        except Exception as e:
            print(f"Error al setear probe en {phy_folder}: {e}. Saltando carpeta.")
            continue # Saltar a la siguiente carpeta si hay un error

        # 3. Extraer waveforms con el método antiguo
        try:
            we = si.extract_waveforms(recording,
                                phy_sorting,
                                folder=waveforms_folder,
                                ms_before=1.5,
                                ms_after=2.,
                                max_spikes_per_unit=20000000)
        except Exception as e:
            print(f"Error al extraer waveforms en {phy_folder}: {e}. Saltando carpeta.")
            continue # Saltar a la siguiente carpeta si hay un error
        
        # 4. Imprimir Información
        print(we)
        print(we.recording)
        print(we.sorting)
        print(we.get_all_templates().shape)
        print("*********************************************************************")