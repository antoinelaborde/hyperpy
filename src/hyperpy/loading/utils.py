import ntpath
import os
from typing import Optional

import numpy as np
from scipy.io import loadmat

from hyperpy.loading.envi_header import read_hdr_file, find_hdr_file


def read_mat_file(file_name: str) -> np.array:
    """
    Read a matlab file and return a numpy array.
    :param file_name:
    :return:
    """
    mat_dict: dict = loadmat(file_name)
    mat_key: str = [
        key
        for key in mat_dict.keys()
        if key not in ["__header__", "__version__", "__globals__"]
    ][0]
    return mat_dict[mat_key]


def read_raw(file_name: str, hdr_filename: Optional[str] = None):
    """
    read a .raw file

    file_name: str, path to the .raw file.
    hdr_filename: str, path to the corresponding .hdr file. If None, substitute the .raw extension with .hdr.

    raw: numpy array containing raw data.
    """
    if hdr_filename is None:
        hdr_filename = os.path.splitext(file_name)[0] + ".hdr"
    # Read .hdr file
    hdr_file = read_hdr_file(hdr_filename)
    bands = int(hdr_file["bands"])
    lines = int(hdr_file["lines"])
    samples = int(hdr_file["samples"])
    header_offset = int(hdr_file["header offset"])
    # Read the .raw file
    with open(file_name, "rb") as f:
        f.seek(header_offset)
        raw = np.fromfile(f, dtype=np.uint16)
    # Reorder data
    raw = raw.reshape(bands * lines, samples)
    raw = raw.reshape(bands, lines, samples, order="F")
    raw = np.transpose(raw, (2, 1, 0))
    return raw


def read_specim(
    file_name: str,
    white_ref_file_name: Optional[str] = None,
    dark_ref_file_name: Optional[str] = None,
):
    """
    reads hyperspectral specim file

    file_name: str, path to the .raw file.
    white_ref_file_name: str, path to the corresponding white reference .raw file. If None, the file name with "WHITEREF_" before is searched.
    dark_ref_file_name: str, path to the corresponding dark reference .raw file. If None, the file name with "DARKREF_" before is searched.

    raw: numpy array containing reflectance data.
    wavelengths: numpy array containing wavelength values.
    """
    if white_ref_file_name is None:
        white_ref_file_name = add_prefix_filename(file_name, "WHITEREF_")
    if dark_ref_file_name is None:
        dark_ref_file_name = add_prefix_filename(file_name, "DARKREF_")

    # Get raw measurement
    raw = read_raw(file_name)
    white_ref = read_raw(white_ref_file_name)
    dark_ref = read_raw(dark_ref_file_name)
    # Get the number of "samples" of the images
    nbr_samples = raw.shape[1]
    # Calculate reference average expanded
    white_average_expanded = expand_average(white_ref, nbr_samples)
    dark_average_expanded = expand_average(dark_ref, nbr_samples)
    # Calculate reflectance
    reflectance = get_reflectance(raw, white_average_expanded, dark_average_expanded)
    # Get the wavelength values
    wavelengths = get_wavelength(file_name)
    return reflectance, wavelengths


def get_reflectance(
    raw: np.array,
    white_ref: np.array,
    dark_ref: np.array = None,
    zero_denominator_replace: float = 1e-9,
):
    """
    calculates reflectance data from raw and reference measurements

    raw: numpy array, raw measurements.
    white_ref: numpy array, white_ref measurements.
    dark_ref: numpy array, dark_ref measurements. If None, dark_ref is zero. Default: None.
    zero_denominator_replace: float, replace zero at the denominator. Default: 1e-9.

    raw: numpy array containing reflectance data.
    """
    if dark_ref is None:
        dark_ref = np.zeros(raw.shape)
    numerator = raw - dark_ref
    denominator = white_ref - dark_ref
    # Check for zero denominator
    denominator[denominator == 0.0] = zero_denominator_replace
    reflectance = np.divide(numerator, denominator)
    return reflectance


def add_prefix_filename(path_file: str, prefix: str):
    """
    adds a prefix to the file name and keep the same path

    path_file: str, path to file.
    prefix: str, prefix to add.

    path_prefix_file: str, path to file.
    """
    path, file_name = ntpath.split(path_file)
    file_name = prefix + file_name
    path_prefix_file = os.path.join(path, file_name)
    return path_prefix_file


def expand_average(raw: np.array, expand_size: int, average_dim: int = 1):
    """
    calculate the average on average_dim and expand the result

    raw: numpy array, contains raw data.
    expand_size: int, size of expand
    average_dim: int, dimension to calculate the average on.

    raw_expand: numpy array.
    """
    raw_average = np.mean(raw, average_dim)
    raw_expand = np.tile(np.expand_dims(raw_average, 2), (1, 1, expand_size))
    raw_expand = np.transpose(raw_expand, (0, 2, 1))
    return raw_expand


def read_hyspex(file_name: str, end_white_index: int, start_white_index: int = 0):
    """
    reads hyperspectral specim file

    file_name: str, path to the .raw file.
    end_white_index: int, end index for white measurement.
    start_white_index: int, first index for white reference measurement. Default: 0.

    reflectance: numpy array containing reflectance data.
    wavelengths: numpy array containing wavelength values.
    """
    # Get raw measurement
    raw = read_raw(file_name)
    white_ref = raw[:, start_white_index:end_white_index, :]
    # Get the number of "samples" of the images
    nbr_samples = raw.shape[1]
    # Calculate reference average expanded
    white_average_expanded = expand_average(white_ref, nbr_samples)
    # Calculate reflectance
    reflectance = get_reflectance(raw, white_average_expanded)
    # Get the wavelength values
    wavelengths = get_wavelength(file_name)
    return reflectance, wavelengths


def get_wavelength(file_name: str):
    """
    get the wavelength in the .hdr file

    file_name: str, path to the raw file.

    wavelengths: numpy array containing wavelength values.
    """
    hdr_file_name = find_hdr_file(file_name)
    hdr_file = read_hdr_file(hdr_file_name)
    wavelength = np.asarray(eval(hdr_file["wavelength"]))
    return wavelength
