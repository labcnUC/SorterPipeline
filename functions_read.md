# Spike Sorting System Documentation

## Introduction
This documentation provides a comprehensive guide to the spike sorting system, detailing its components, functionality, and workflow. The system includes a robust logging framework for error tracking, centralized message handling, and core processing functions.

## Components

### 1. Logger Setup
#### Overview
The logger handles and records messages related to the spike sorting pipeline execution. It supports multiple levels: `INFO`, `WARNING`, `ERROR`, and `DEBUG`, ensuring all events are appropriately tracked.

#### Key Function
```python
setup_logger(log_file="execution_log.log", log_level=logging.INFO)
```
- **Inputs**: 
  - `log_file`: Name of the log file.
  - `log_level`: Logging level (e.g., `INFO`, `WARNING`, `ERROR`).
- **Outputs**: Configures logging for both console and file outputs.

---

### 2. Centralized Message Handling: `log_and_print`
#### Overview
The `log_and_print` function standardizes message handling by combining logging and console output. This ensures consistency across the pipeline.

#### Key Function
```python
log_and_print(msg, level="info")
```
- **Inputs**: 
  - `msg`: The message to display and log.
  - `level`: Logging level (e.g., `info`, `warning`, `error`).
- **Outputs**: Logs the message to the logger and displays it on the console.

---

### 3. Main Functions

#### A. `read_rhd`
- **Purpose**: Load `.rhd` files from the specified directory and concatenate them if multiple files exist.
- **Workflow**:
  1. Check for `.rhd` files in the directory.
  2. Load and concatenate the files.
  3. Log the number of processed files and their names.
- **Error Handling**: Logs a warning if no `.rhd` files are found.

#### B. `get_recording`
- **Purpose**: Process recordings, including filtering and artifact removal.
- **Workflow**:
  1. Load the `probegroup` configuration.
  2. Read recordings using `read_rhd`.
  3. Calculate the sampling rate.
  4. Process artifacts using `process_artifacts`.
  5. Apply bandpass filters and remove artifacts.
- **Error Handling**: Logs critical errors encountered during processing.

#### C. `process_artifacts`
- **Purpose**: Analyze and remove artifacts from the recording.
- **Workflow**:
  1. Locate and load the relevant artifact dataset.
  2. Process start and end indices of artifacts.
  3. Compute triggers based on artifact-free segments.
- **Error Handling**: Logs warnings for missing datasets or configuration issues.

---

### 4. Experiment Recreation
#### Overview
The `recreate_experiment` function extracts parameters from the log file, enabling the reconstruction of an experiment.

#### Key Function
```python
recreate_experiment(log_file)
```
- **Inputs**: 
  - `log_file`: Path to the log file.
- **Outputs**: Returns a dictionary with parameters such as file paths, sampling rates, and triggers.

---

## Workflow Diagram
The diagram below illustrates the spike sorting pipeline, including key components, error handling, and logging mechanisms.

![Workflow Diagram](A_structured_flowchart_diagram_illustrating_a_spik.png)

---

## Best Practices
1. **Consistent Message Handling**:
   - Use `log_and_print` for all messages to ensure consistency.
2. **Structured Logging**:
   - Write clear, informative messages with context to aid debugging.
3. **Proactive Error Handling**:
   - Anticipate and handle common issues, such as missing files or incorrect configurations.

---

## Troubleshooting
### Common Issues
1. **Missing Files**:
   - Verify the paths provided to the functions.
   - Check if `.rhd` files are available in the target directory.
2. **Incorrect Sampling Rate**:
   - Ensure all recordings have consistent sampling frequencies.

### Debugging Steps
- Review the log file (`execution_log.log`) for detailed messages.
- Use the `recreate_experiment` function to validate extracted parameters from the logs.

---

## Future Enhancements
- **Support for Additional File Formats**: Extend compatibility to handle more input formats.
- **Visualization Tools**: Implement graphical representations of triggers and processed recordings.
- **Performance Metrics**: Include metrics like processing time in the logs.

---

## References
- **SpikeInterface Documentation**: [SpikeInterface Docs](https://spikeinterface.readthedocs.io)
- **Python Logging Library**: [Python Logging Docs](https://docs.python.org/3/library/logging.html)



