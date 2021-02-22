# Hyperpy
A Python package to process, analyze and work with hyperspectral data.

## Import data

Use the SpectralCube class to import hyperspectral data.

### Specim

Assume your data are organized as follow:

```
.
+-- Measurement_folder 
|   +-- DATA_001.hdr            => header file for raw measurement
|   +-- DATA_001.raw            => raw measurement file
|   +-- DARKREF_DATA_001.hdr    => header file for dark reference
|   +-- DARKREF_DATA_001.raw    => dark reference measurement
|   +-- WHITEREF_DATA_001.hdr   => header file for white reference
|   +-- WHITEREF_DATA_001.raw   => white reference measurement
```

The raw measurement data are loaded and the reflectance is computed directly using:
```python
from hyperpy.cube import SpectralCube
path = './Measurement_folder/DATA_001.raw'
specim_cube = SpectralCube.from_specim(path)
```