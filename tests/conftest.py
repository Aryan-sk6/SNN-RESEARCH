import numpy as np
import pytest

from snn_oddball import params as P


@pytest.fixture(scope="session")
def p():
    return P.NetworkParams()


@pytest.fixture
def rng():
    return np.random.default_rng(12345)
