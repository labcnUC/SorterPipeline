# 📘 Representación ASCII de funciones accesorias
```

┌──────────────────────────────────────────────────────────────┐
│                    Función: preproc_recording2               │
└──────────────────────────────────────────────────────────────┘
Entrada: archivo o carpeta .rhd (+ opcional LAN)
    |
    +-- ¿Es archivo individual?
    |     |
    |     +-- Sí → usar .parent como carpeta
    |     +-- No → usar path como carpeta
    |
    +-- Listar archivos .rhd y mostrar info
    |
    +-- Leer probegroup
    |
    +-- Llamar a read_rhd2()
    |
    +-- Calcular frecuencia de muestreo
    |
    +-- Asignar probegroup a la grabación
    |
    +-- Llamar a process_artifacts2()
    |
    +-- Aplicar filtros:
    |     • Filtro pasa banda
    |     • Centrado
    |
    +-- ¿Triggers disponibles?
          |
          +-- Sí → Calcular niveles de ruido y aplicar silence_periods()
    |
    +-- return recording


┌──────────────────────────────────────────────────────────────┐
│                    Función: process_artifacts2               │
└──────────────────────────────────────────────────────────────┘
Entrada: nombre parcial de artefacto, carpeta base, fs, lan_file
    |
    +-- ¿Se pasa lan_file?
    |     |
    |     +-- No → buscar LAN en base_folder
    |     +-- Sí → usar archivo directamente
    |
    +-- Leer archivo HDF5
    +-- Buscar dataset con subcadena parcial
    +-- Leer señal de selección (~selected)
    +-- Calcular índices de INICIO y FIN
    +-- Filtrar segmentos pequeños
    +-- Convertir a triggers en fs destino
    +-- return list_triggers


┌──────────────────────────────────────────────────────────────┐
│                 Función: crear_vectores_acumulados           │
└──────────────────────────────────────────────────────────────┘
Entrada: ventana mínima, listas de inicio y fin
    |
    +-- Convertir a numpy arrays
    +-- Filtrar segmentos < window_size
    +-- Empaquetar como tuplas (inicio, fin)
    +-- return lista de períodos [(start, end)]
```
