# 📘 Manual de uso – Árbol de decisiones `get_recording2`

## Introducción

La función `get_recording2` ha sido diseñada para gestionar el preprocesamiento automatizado de archivos de grabación neuronal en formato `.rhd`, y su sincronización mediante archivos `LAN_*.mat`. Este árbol de decisiones describe el flujo lógico implementado para adaptar el procesamiento según el contenido disponible en una carpeta determinada.

## Requisitos de entrada

La carpeta de entrada debe contener:

- Uno o más archivos `.rhd` (datos de señal cruda)
- Uno o más archivos `LAN_*.mat` (archivos de sincronización LAN)

## Flujo de decisión

### 1. Verificación de archivos `.rhd`

- Si no se encuentran archivos `.rhd`, el proceso se detiene con un mensaje de error.

### 2. Verificación de archivos `LAN_*.mat`

- Si no se encuentra ningún archivo LAN, el proceso se detiene.

### 3. Detección de la cantidad de archivos LAN

- **Un solo archivo LAN**:
  - Se concatenan todos los `.rhd` encontrados.
  - Se llama a `preproc_recording2` con el archivo LAN.

- **Múltiples archivos LAN**:
  - Se empareja cada LAN con un archivo `.rhd` basado en el nombre.
  - Se llama a `preproc_recording2` por cada par.
  - Solo las grabaciones válidas se conservan.

### 4. Postprocesamiento

- Si no se obtiene ninguna grabación válida, el proceso finaliza.
- Si se obtiene una sola grabación, se retorna directamente.
- Si se obtienen múltiples grabaciones válidas, se concatenan y se retorna el resultado final.

## Funciones asociadas

- `preproc_recording2`: Procesa una grabación única (carpeta o archivo `.rhd`), con o sin archivo LAN asociado.
- `process_artifacts2`: Detecta artefactos dentro del archivo LAN, y genera eventos de limpieza.

## Recomendaciones

- Los archivos `.rhd` y `LAN_*.mat` deben compartir un identificador común en el nombre (por ejemplo, fecha/hora).
- Si se presentan errores en el emparejamiento, verificar manualmente los nombres de los archivos.

## Resultado

El resultado final es un objeto de tipo `RecordingExtractor` (de SpikeInterface) que representa una o varias grabaciones preprocesadas, listas para análisis, sorting, o visualización.

---

Este manual es parte del sistema de procesamiento automatizado para datos de neurofisiología. Para modificaciones adicionales o casos personalizados, se recomienda adaptar el árbol de decisiones y las funciones auxiliares correspondientes.


## Árbol de decisiones (representación ASCII)
```

Inicio: get_recording2()
    |
    +-- ¿Hay archivos .rhd?
    |     |
    |     +-- No  --> 🚨 return None
    |     |
    |     +-- Sí
    |           |
    |           +-- ¿Hay archivos LAN?
    |                 |
    |                 +-- No  --> 🚨 return None
    |                 |
    |                 +-- Sí
    |                      |
    |                      +-- ¿Cantidad de LAN?
    |                           |
    |                           +-- 1 LAN
    |                           |     |
    |                           |     +-- Concatenar todos los .rhd
    |                           |     +-- Ejecutar preproc_recording2
    |                           |
    |                           +-- Múltiples LAN
    |                                 |
    |                                 +-- Para cada LAN:
    |                                       |
    |                                       +-- Buscar .rhd correspondiente
    |                                       |     |
    |                                       |     +-- No --> ⚠️ advertencia
    |                                       |     +-- Sí
    |                                       |           |
    |                                       |           +-- Ejecutar preproc_recording2
    |                                       |           +-- ¿Grabación válida?
    |                                       |                 |
    |                                       |                 +-- No --> ⚠️ advertencia
    |                                       |                 +-- Sí --> agregar a lista
    |                                       |
    |                                       +-- ¿Grabaciones válidas?
    |                                             |
    |                                             +-- No --> 🚨 return None
    |                                             +-- Una --> return directamente
    |                                             +-- Varias --> concatenar y return
```


## 📚 Funciones auxiliares utilizadas en `get_recording2`

### `preproc_recording2(...)`

Preprocesa una carpeta de archivos `.rhd` o un archivo único, con un probegroup definido y un archivo LAN opcional. Esta función aplica:

1. Carga y orden de archivos `.rhd`
2. Lectura del objeto `RecordingExtractor`
3. Configuración del `ProbeGroup`
4. Procesamiento de artefactos desde un archivo LAN
5. Filtro pasa banda (500–5000 Hz)
6. Centración de la señal
7. Cálculo de ruido (MAD)
8. Aplicación de `silence_periods`

**Entrada:**
- `file_data_folder`: ruta a carpeta o archivo `.rhd`
- `artifacts`: nombre parcial del artefacto
- `probegroup_file`: archivo `.json` de SpikeInterface
- `lan_file`: archivo `.mat` LAN (opcional)

**Salida:**
- Objeto `RecordingExtractor` preprocesado

---

### `process_artifacts2(...)`

Busca un archivo LAN en la carpeta indicada, localiza el dataset asociado al nombre del artefacto, y genera triggers a partir de los segmentos válidos.

**Entrada:**
- `partial_artifact_name`: subcadena esperada en el nombre del dataset
- `base_folder`: ruta base
- `fs`: frecuencia de muestreo
- `lan_file`: ruta explícita al archivo LAN (opcional)

**Salida:**
- `list_triggers`: lista de segmentos sin artefactos en muestras

---

### `crear_vectores_acumulados(...)`

Filtra segmentos muy pequeños y crea una lista de tuplas `(inicio, fin)` que representan períodos válidos.

**Entrada:**
- `window_size`: duración mínima en muestras
- `list_ini`: tiempos de inicio
- `list_fin`: tiempos de fin

**Salida:**
- Lista de períodos de silencio (como pares de índices)

---

