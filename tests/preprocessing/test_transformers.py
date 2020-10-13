from unittest import mock
from unittest.mock import MagicMock

import numpy as np
import pytest

from hyperpy.preprocessing.transformers import (
    Log,
    Positive,
    StandardNormalDeviate,
    MeanCentering,
    SavitzkyGolay,
    MultiplicativeScatterCorrection,
    Normalization,
)


class TestLog:
    def test_log(self):
        array = np.array([1, 10, 100])
        log_transformer = Log()
        log_array = log_transformer.transform(array)
        np.allclose(log_array, np.array([0.0, 1.0, 2.0]))


class TestPositive:
    def test_positive_already_positive(self):
        array = np.array([5, 10, 15, 20])
        pos_transformer = Positive()
        pos_array = pos_transformer.transform(array)
        np.allclose(pos_array, np.array([5, 10, 15, 20]))

    def test_positive_not_positive(self):
        array = np.array([-5, 10, 15, 20])
        pos_transformer = Positive()
        pos_array = pos_transformer.transform(array)
        np.allclose(pos_array, np.array([0, 15, 20, 25]))


class TestStandardNormalDeviate:
    def test_standard_normal_deviate_row(self):
        array = np.array([1.0, 2.0, 3.0, 4.0])
        snv_transformer = StandardNormalDeviate()
        snv_array = snv_transformer.transform(array)
        np.allclose(snv_array, np.array([-1.34, -0.45, 0.45, 1.34]))

    def test_standard_normal_deviate_mat(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        snv_transformer = StandardNormalDeviate()
        snv_array = snv_transformer.transform(array)
        np.allclose(snv_array, np.array([[-1, 1], [-1, 1]]))


class TestMeanCentering:
    def test_mean_centering_row(self):
        array = np.array([1.0, 2.0])
        mean_centering_transformer = MeanCentering()
        mr_array = mean_centering_transformer.transform(array)
        np.allclose(mr_array, np.array([-0.5, 0.5]))

    def test_mean_centering_mat(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        snv_transformer = StandardNormalDeviate()
        snv_array = snv_transformer.transform(array)
        np.allclose(snv_array, np.array([[-0.5, 0.5], [-0.5, 0.5]]))


class TestSavistkyGolay:
    @mock.patch("hyperpy.preprocessing.utils.np.apply_along_axis")
    @mock.patch("hyperpy.preprocessing.transformers.savitzky_golay")
    def test_savistky_golay(self, mocked_savitzky_golay, mocked_apply_along):
        sg = SavitzkyGolay(window_size=7, polynomial_order=2, derivation_order=1)
        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        mocked_filter = MagicMock()
        mocked_extended = MagicMock()

        mocked_savitzky_golay.return_value = (mocked_filter, mocked_extended)
        sg.transform(array)
        mocked_savitzky_golay.assert_called_with(array, 7, 2, 1)
        mocked_apply_along.assert_called_with(
            np.convolve, 1, mocked_extended, mocked_filter, mode="valid"
        )


class TestMultiplicativeScatterCorrection:
    @mock.patch("hyperpy.preprocessing.utils.np.polyfit")
    def test_multiplicative_scatter_correction_no_ref(self, mock_polyfit):
        array = np.array([1, 2, 3, 4])
        msc = MultiplicativeScatterCorrection()
        with pytest.raises(ValueError):
            msc.fit(array)

        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        msc = MultiplicativeScatterCorrection()
        msc.fit(array)

        np.allclose(msc.reference, np.array([1.5, 3.5]))
        mock_polyfit.return_value = (np.array([1, 1]),)
        msc.transform(array)
        mock_polyfit.assert_called()

    def test_multiplicative_scatter_correction_with_ref(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        msc = MultiplicativeScatterCorrection()
        with pytest.raises(ValueError):
            msc.fit(array, np.array([[1.0, 2.0], [3.0, 4.0]]))
        msc.fit(array, np.array([[1.0, 3.0]]))


class TestNormalization:
    def test_l1_normalization(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        normalizer = Normalization(norm="l1")
        tested_array = normalizer.transform(array)

        norm_l1_array = np.array(
            [
                [0.33333333, 0.66666667],
                [0.42857143, 0.57142857],
                [0.45454545, 0.54545455],
            ]
        )

        np.allclose(norm_l1_array, tested_array)

    def test_l2_normalization(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        normalizer = Normalization(norm="l2")
        tested_array = normalizer.transform(array)

        norm_l2_array = np.array(
            [[0.4472136, 0.89442719], [0.6, 0.8], [0.6401844, 0.76822128]]
        )

        np.allclose(norm_l2_array, tested_array)

    def test_inf_normalization(self):
        array = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        normalizer = Normalization(norm="inf")
        tested_array = normalizer.transform(array)

        norm_inf_array = np.array([[0.5, 1.0], [0.75, 1.0], [0.83333333, 1.0]])

        np.allclose(norm_inf_array, tested_array)

    def test_unknown_normalization(self):
        with pytest.raises(ValueError):
            Normalization(norm="toto")
