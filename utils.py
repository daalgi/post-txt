from numpy import trapz, asarray, asanyarray, diff, add


def force_stress_integration(y, x=None, dx=1.0, axis=-1):
    """
    FORCE OBTAINED BY INTEGRATION OF THE STRESS DISTRIBUTION USING THE TRAPEZOIDAL RULE:
    Integrate(y(x) dx)
    Reference: numpy.trapz
    :param y:
    :param x:
    :param dx:
    :param axis:
    :return:
    """
    return trapz(y, x, dx, axis)


def moment_stress_integration(y, x=None, dx=1.0, axis=-1):
    """
    BENDING MOMENT OBTAINED BY INTEGRATION OF THE STRESS DISTRIBUTION USING THE TRAPEZOIDAL RULE:
    Integrate(y(x) x dx)
    Reference: numpy.trapz
    :param y:
    :param x:
    :param dx:
    :param axis:
    :return:
    """
    y = asanyarray(y)
    if x is None:
        d = dx
    else:
        x = asanyarray(x)
        if x.ndim == 1:
            d = diff(x)
            # reshape to correct shape
            shape = [1] * y.ndim
            shape[axis] = d.shape[0]
            d = d.reshape(shape)
        else:
            d = diff(x, axis=axis)
    nd = y.ndim
    slice1 = [slice(None)] * nd
    slice2 = [slice(None)] * nd
    slice1[axis] = slice(1, None)
    slice2[axis] = slice(None, -1)
    try:
        ret = ((y[tuple(slice2)] * (x[tuple(slice1)] + x[tuple(slice2)]) +
               (y[tuple(slice1)] - y[tuple(slice2)]) * (2.0 * x[tuple(slice1)] + x[tuple(slice2)]) / 3.0) *
               (x[tuple(slice1)] - x[tuple(slice2)]) / 2.0).sum(axis)
    except ValueError:
        # Operations didn't work, cast to ndarray
        d = asarray(d)
        y = asarray(y)
        ret = add((y[tuple(slice2)] * (x[tuple(slice1)] + x[tuple(slice2)]) +
                   (y[tuple(slice1)] - y[tuple(slice2)]) * (2.0 * x[tuple(slice1)] + x[tuple(slice2)]) / 3.0) *
                  (x[tuple(slice1)] - x[tuple(slice2)]) / 2.0).sum(axis)
    return ret


if __name__ == '__main__':
    """
    y = [2, 2]
    x = [0, 3]
    print(moment_stress_integration(y, x))

    y = asarray(y)
    nd = y.ndim
    slice1 = [slice(None)] * nd
    slice2 = [slice(None)] * nd
    print(slice1, slice2)
    slice1[-1] = slice(1, None)
    slice2[-1] = slice(None, -1)
    print(slice1, slice2)
    print(y)
    print(y[tuple(slice1)])
    print(y[tuple(slice2)])"""

    stress = [-7.62257, +5.76795]
    y = [-1.7/2, 1.7/2]
    print(moment_stress_integration(stress, y))