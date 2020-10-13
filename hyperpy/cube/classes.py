from dataclasses import dataclass
from typing import Optional

import numpy as np

from hyperpy import exceptions
from hyperpy.loading import read_specim, read_hyspex, read_mat_file


@dataclass
class SpectralCube:
    data: np.array
    domain: np.array

    def __post_init__(self):
        """
        Make some check for the consistency of the data.
        """
        # Check data dimension
        if len(self.data.shape) != 3:
            raise exceptions.DataDimensionError(len(self.data.shape), 3)
        # Check data dimension
        if len(self.domain.shape) != 1:
            raise exceptions.DataDimensionError(len(self.domain.shape), 1)
        # Check domain dimension
        self.width, self.heigh, data_domain = self.data.shape
        if data_domain != self.domain.shape[0]:
            raise exceptions.WrongDomainDimension(self.domain.shape, self.data.shape)
        self.shape = self.data.shape

    def get_matrix(self):
        """
        Get a 2D matrix from the data array.
        """
        x, y, l = self.data.shape
        mat = np.reshape(self.data, (x * y, l))
        return mat

    @staticmethod
    def from_mat_file(data_file_name: str, domain_file_name: Optional[str] = None):
        """
        Construct a SpectralCube instance from a .mat file containing the data array and a .mat file containing the domain array.
        :param data_file_name:
        :param domain_file_name:
        :return:
        """
        domain_file_name = domain_file_name or None
        data: np.array = read_mat_file(data_file_name)
        if domain_file_name is None:
            domain = np.arange(1, data.shape[2] + 1)
        else:
            domain: np.array = read_mat_file(domain_file_name)
        return SpectralCube(data=data, domain=domain)

    @staticmethod
    def from_specim(data_file_name: str, **kwargs):
        """
        Construct a SpectralCube instance from a specim file.
        :param data_file_name:
        :return:
        """
        data, domain = read_specim(data_file_name, **kwargs)
        return SpectralCube(data=data, domain=domain)

    @staticmethod
    def from_hyspex(data_file_name: str, end_white_index: int, **kwargs):
        """
        Construct a SpectralCube instance from a specim file.
        :param end_white_index:
        :param data_file_name:
        :return:
        """
        data, domain = read_hyspex(data_file_name, end_white_index, **kwargs)
        return SpectralCube(data=data, domain=domain)


def as_cube(
    data: np.array, spectral_cube: SpectralCube, domain: Optional[np.array] = None
):
    """
    Create a Spectral Cube using the cube shape of an existing Spectral Cube.
    :param data: 2D numpy array to transform in Spectral Cube.
    :param spectral_cube: reference spectral cube.
    :param domain: Optional. If None use the domain of the reference spectral cube.
    :return: SpectralCube
    """
    domain = domain or spectral_cube.domain
    data_cube = np.reshape(data, spectral_cube.shape)
    return SpectralCube(data=data_cube, domain=domain)
