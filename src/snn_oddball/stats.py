"""Mean and 95% confidence interval over seeds (t-interval; n is small)."""

from __future__ import annotations

import numpy as np
from scipy import stats as _st


def mean_ci(values, conf: float = 0.95):
    """Return (mean, lo, hi, n_valid, n_nan) over `values`, ignoring NaN.

    The interval is the Student-t interval of the mean. With fewer than two valid values
    the interval is (nan, nan): a single seed gives no uncertainty estimate.
    """
    if not 0.0 < conf < 1.0:
        raise ValueError("conf must be in (0, 1)")
    x = np.asarray(values, dtype=float).ravel()
    n_nan = int(np.isnan(x).sum())
    x = x[~np.isnan(x)]
    n = x.size
    if n == 0:
        return (np.nan, np.nan, np.nan, 0, n_nan)
    m = float(x.mean())
    if n < 2:
        return (m, np.nan, np.nan, n, n_nan)
    sem = float(x.std(ddof=1) / np.sqrt(n))
    h = float(_st.t.ppf(0.5 + conf / 2, df=n - 1) * sem)
    return (m, m - h, m + h, n, n_nan)
