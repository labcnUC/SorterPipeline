# 🧠 get_recording2: Árbol de decisiones para preprocesamiento de señales neuronales

Este repositorio contiene una implementación robusta para la gestión automatizada de grabaciones neuronales (`.rhd`) y sus archivos de sincronización (`LAN_*.mat`). La función principal `get_recording2` utiliza un árbol de decisiones para decidir cómo preprocesar, emparejar, y concatenar datos según la estructura de la carpeta de entrada.

---

## 🔧 Función principal

### `get_recording2(rhd_folder, artifacts, probegroup_file)`

Esta función busca archivos `.rhd` y `LAN_*.mat` dentro de un directorio, toma decisiones según su cantidad, los empareja por nombre y retorna un `RecordingExtractor` preprocesado.

---

## 🌳 Árbol de decisiones

```
Inicio
  ├── ¿Hay archivos .rhd?
  │     └── No → 🚨 return None
  ├── ¿Hay archivos LAN?
  │     └── No → 🚨 return None
  └── ¿Cantidad de LAN?
        ├── 1 → 🔁 Concatenar .rhd y ejecutar preproc_recording2
        └── >1
             ├── 🔗 Emparejar .rhd ↔ LAN
             ├── 📊 Ejecutar preproc_recording2
             ├── 📦 Acumular grabaciones válidas
             └── ✅ Concatenar si es necesario
```

---

## 🧩 Funciones auxiliares

### `preproc_recording2(...)`
📂 Preprocesa una carpeta o archivo `.rhd` y opcionalmente un archivo LAN.  
Incluye: filtro pasa banda, centrado, remoción de artefactos `LAN`, detección de ruido y configuración de probegroup.

### `process_artifacts2(...)`
📊 Detecta artefactos dentro del archivo LAN y genera triggers para eliminar segmentos ruidosos.

### `crear_vectores_acumulados(...)`
⏱️ Filtra y crea períodos válidos de señal a partir de inicios y fines en frames.

### `read_rhd2(...)`
📥 Lee y concatena uno o más archivos `.rhd` como `RecordingExtractor`.

### `experiment_type(...)`
🔍 Clasifica archivos en `Sleep`, `Maze`, o `Desconocido` según el nombre del archivo.

---

## 📁 Estructura esperada

```
📂 animal_folder/
├── Sleep_Day01_123000.rhd
├── Sleep_Day01_124000.rhd
├── LAN_Sleep_Day01_123000.mat
├── LAN_Sleep_Day01_124000.mat
├── probegroup.json
```

---

## ✅ Requisitos

- Python 3.8+
- SpikeInterface
- h5py, numpy
- Archivos `.rhd` de Intan y archivos `.mat` de sincronización

---

## 📄 Documentación adicional

Ver el archivo [README_get_recording2.md](README_get_recording2.md) o su versión en PDF para una descripción completa del flujo.

