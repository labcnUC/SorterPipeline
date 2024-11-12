# SorterPipeline

SorterPipeline es un pipeline para el análisis de *spikesorter* utilizando Kilosort4 a través de SpikeInterface. Este pipeline no incluye *Phy2*, que debe ser instalado por separado (ver sección de instalación).

## Tabla de Contenidos

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Descripción

Este pipeline proporciona herramientas para el análisis de datos de *spike sorting*, facilitando la integración con Kilosort4 y SpikeInterface para una mayor eficiencia en el procesamiento de datos neuronales.

## Requisitos

- **Python**: Se recomienda usar Anaconda para gestionar entornos.
- **CUDA**: Asegúrate de tener un controlador CUDA compatible con tu versión de PyTorch.
- **PyTorch**: Consulta la compatibilidad de versiones entre CUDA y PyTorch.

## Instalación

Sigue estos pasos para instalar el SorterPipeline:

1. **Instala Anaconda**: Puedes descargarlo desde [Anaconda](https://www.anaconda.com/download). Recomendacion: Si no quieres utilizar el GUI, utiliza la version compacta "miniconda".
   
2. **Verifica el controlador CUDA**: Ejecuta el siguiente comando en la terminal:
   ```bash
   nvcc --version
    ```
Si no lo tienes instalado, consulta [NVIDIA CUDA GPUs](https://developer.nvidia.com/cuda-gpus#compute)

3. Clone el repositorio:
    ```bash
    git clone https://github.com/labcnUC/SorterPipeline.git
    ```
4. Navegue al directorio del pipeline ⛵:
    ```bash
    cd SorterPipeline
    ```
9. Cree el env de conda e instala las dependencias (advertencia: Estas estan creadas para funcionar con CUDA 11.8)
    ```bash
    conda env create -f environment.yml
    ```
6. Verifique la instalación: Inicia Python y ejecuta:

    ```python
    import spikeinterface
    import kilosort
    import torch
    torch.cuda.is_available()
    ```
🚨 Si ocurre un error, verifica la compatibilidad de PyTorch consultando las [notas de versión de PyTorch](https://github.com/pytorch/pytorch/blob/main/RELEASE.md)  para asegurarte de que tu versión de CUDA sea compatible. Instala PyTorch si es necesario utilizando el siguiente enlace: [Instalación de PyTorch](https://pytorch.org/get-started/locally/).  
El funcionamiento correcto de CUDA y PyTorch es esencial tanto para DeepLabCut como para otras aplicaciones con requisitos similares.

10. Ejecuta Jupyter Lab:
    ```bash
    jupyter lab
    ```
# Uso
Después de seguir los pasos de instalación, abre Jupyter Lab y lea el notebook sh_sorterpipeline para comenzar a trabajar en el análisis de spike sorting.

# Instalación de Phy.
```python
conda create -n phy2 -y python=3.11 cython dask h5py joblib matplotlib numpy pillow pip pyopengl pyqt pyqtwebengine pytest python qtconsole requests responses scikit-learn scipy traitlets
```

# Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor sigue estos pasos:

1. Haz un fork del proyecto.
2. Crea una nueva rama (feature/nueva-funcionalidad).
3. Realiza cambios y prueba funcionalidades (expandir a otros sorters).
4. Envía un pull request.
