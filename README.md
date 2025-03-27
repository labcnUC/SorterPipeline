# SorterPipeline: Pipeline para análisis de spike sorting con Kilosort4

SorterPipeline es un pipeline para el análisis de *spike sorting* utilizando Kilosort4 a través de SpikeInterface. Este pipeline no incluye *Phy2*, que debe ser instalado por separado (ver sección [Instalación de Phy](#instalación-de-phy)).

## Tabla de Contenidos

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Instalación de Phy](#instalación-de-phy)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Descripción

Este pipeline proporciona herramientas para el análisis de datos de *spike sorting*, facilitando la integración con Kilosort4 y SpikeInterface para una mayor eficiencia en el procesamiento de datos neuronales.

## Requisitos

- **Python**: Se recomienda usar Anaconda para gestionar entornos.
- **CUDA**: Asegúrate de tener un controlador CUDA compatible con tu versión de PyTorch.
- **PyTorch**: Consulta la compatibilidad de versiones entre CUDA y PyTorch.

## Instalación



1. Navega al directorio:
    ```bash
    cd SorterPipeline
    ```

2. Crea un nuevo entorno virtual:
    ```bash
    conda create --name sorterpipeline python=3.10
    ```

3. Activa el entorno:
    ```bash
    conda activate sorterpipeline
    ```

4. Clona el repositorio:
    ```bash
    git clone https://github.com/labcnUC/SorterPipeline.git
    ```

5. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

6. Verifica la instalación:
    ```bash
    python
    ```   
    ```python
    import spikeinterface
    import kilosort
    import torch
    torch.cuda.is_available()
    ```

## Uso

1. Abre Jupyter Lab:
    ```bash
    jupyter lab
    ```

2. Abre el archivo `sorterpipeline_v2.ipynb`.

3. Sigue las instrucciones para cargar datos, configurar el pipeline y ejecutar el análisis.

## Instalación de Phy

Phy es una herramienta opcional para la curación manual de datos. Para instalarla:

1. Crea un nuevo entorno:
    ```bash
    conda create -n phy2 -y python=3.11 ...
    ```

2. Activa el entorno:
    ```bash
    conda activate phy2
    ```

3. Instala Phy:
    ```bash
    pip install phy
    ```

## Contribuciones

1. Haz un fork.
2. Crea una nueva rama:
    ```bash
    git checkout -b feature/nueva-funcionalidad
    ```
3. Realiza cambios.
4. Envía un pull request.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta [LICENSE](LICENSE) para más detalles.
