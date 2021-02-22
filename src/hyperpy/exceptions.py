class HyperspectralError(Exception):
    """
    Basic exception for the all package
    """

    pass


class DomainError(HyperspectralError):
    """
    Error caused by the spectral domain
    """

    pass


class DataDimensionError(HyperspectralError):
    """
    Error caused by a wrong number of dimension
    """

    def __init__(self, data_dim, expected_dim):

        message = f"Expected data with {expected_dim} but received {data_dim} instead."
        super(DataDimensionError, self).__init__(message)
        self.data_dim = data_dim
        self.expected_dim = expected_dim


class WrongDomainDimension(DomainError):
    """
    When the domain dimension is not appropriate
    """

    def __init__(self, domain_shape, data_shape):

        message = f"Wrong domain shape {domain_shape} for data of shape {data_shape}."
        super(WrongDomainDimension, self).__init__(message)
        self.domain_shape = domain_shape
        self.data_shape = data_shape


class ArrayDimensionError(DataDimensionError):
    """
    Error caused by a numpy array with a wrong shape
    """

    def __init__(self, array_dim, expected_dim):

        message = f"Expected data with {expected_dim} dimensions but received {array_dim} instead."
        super(DataDimensionError, self).__init__(message)
        self.array_dim = array_dim
        self.expected_dim = expected_dim
