import numpy as np
from typing import Union, Optional
from numpy.random import MT19937, RandomState, SeedSequence

def sub_sampling(data: np.array, size: Union[float, int], random_state: Optional[float] = None) -> np.array:
    """
    Subsample input data
    :param data: 2D array
    :param size: size of sub sampling;
        if float in [0; 1]: fraction of data shape is used.
        if int: exact number of element are used.
    :param random_state: random state of random choice
    :return:
    """
    if isinstance(size, float) and 0 < size <= 1:
        shape = int(np.ceil(data.shape[0] * size))
    elif isinstance(size, int) and size > 0:
        shape = size
    else:
        raise ValueError
    if random_state:
        raise NotImplementedError
    return data[np.random.choice(data.shape[0], shape, replace=False), :]
