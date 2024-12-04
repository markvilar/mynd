# Mynd

### CLI - Ingestion

#### Create a chunk with cameras and metadata

```bash
poetry run mynd ingest-cameras \
  <path/to/source_project.psz> \
  <path/to/destination_project.psz> \
  --bundle \
    <chunk_label> \
    <path/to/cameras.csv> \
    <path/to/image_directory> \
    <path/to/metadata.csv> \
    <path/to/config.toml>
```

#### Adding metadata to an existing chunk

```bash
poetry run mynd ingest-metadata \
  <path/to/source_project.psz> \
  <path/to/destination_project.psz> \
  --bundle \
    <chunk_label> \
    <path/to/metadata.csv> \
    <path/to/config.toml>
```

### CLI - Export cameras

#### Export cameras to ASDF

```bash
poetry run mynd export-cameras <path/to/source_project.psz> <path/to/output.asdf> <chunk_label>
```

#### Export cameras to CSV

```bash
poetry run mynd export-cameras <path/to/source_project.psz> <path/to/output.csv> <chunk_label>
```

#### Export stereo geometry

```bash
poetry run mynd export-stereo \
  <path/to/project.psz> \
  <path/to/output_directory> \
  <path/to/stereo_model.onnx> \
  <chunk_label> \
  --save-samples
```

### CLI - Registration

#### Register chunks

```bash
poetry run mynd register \
  <path/to/source_project.psz> \
  <path/to/destination_project.psz> \
  <path/to/config.toml> \
  <path/to/cache_directory> \
  --reference <reference_chunk_label> \
  --vis # flag for visualization
```
