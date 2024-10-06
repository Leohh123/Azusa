# references:
# https://www.mathworks.com/matlabcentral/fileexchange/7028-iso-226-equal-loudness-level-contour-signal
# https://cdn.standards.iteh.ai/samples/83117/6afa5bd94e0e4f32812c28c3b0a7b8ac/ISO-226-2023.pdf
# https://scikit-maad.github.io/_modules/maad/spl/conversion_SPL.html


import numpy as np
from typing import Callable

import sys


FLOAT_MIN = sys.float_info.min

f = np.array([
    20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160,
    200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
    2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500
])
af = np.array([
    0.532, 0.506, 0.480, 0.455, 0.432, 0.409, 0.387, 0.367, 0.349, 0.330,
    0.315, 0.301, 0.288, 0.276, 0.267, 0.259, 0.253, 0.250, 0.246, 0.244,
    0.243, 0.243, 0.243, 0.242, 0.242, 0.245, 0.254, 0.271, 0.301
])
Lu = np.array([
    -31.6, -27.2, -23.0, -19.1, -15.9, -13.0, -10.3, -8.1, -6.2, -4.5,
    -3.1, -2.0, -1.1, -0.4, 0.0, 0.3, 0.5, 0.0, -2.7, -4.1,
    -1.0, 1.7, 2.5, 1.2, -2.1, -7.1, -11.2, -10.7, -3.1
])
Tf = np.array([
    78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9,
    14.4, 11.4, 8.6, 6.2, 4.4, 3.0, 2.2, 2.4, 3.5, 1.7,
    -1.3, -4.2, -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3
])


# wave = np.array()
# Vadc = 2
# volt = wave * Vadc
# sensitivity = -35
# dBref = 94
# gain = 42
# coeff = 1/10**(sensitivity/20)
# p = volt * coeff / 10**(gain/20)
# p[p == 0] = FLOAT_MIN
# L = 20*log10(p/pRef)


def PSDs_to_SPLs(psd: float | np.ndarray, gain: int = 42, Vadc: float = 2., sensitivity: float = -35, dBref: int = 94, pRef=20e-6):
    '''Power Spectral Density (^2/Hz) to Sound Pressure Level (dB)'''
    amplitude = np.sqrt(psd)
    volt = amplitude * Vadc
    coeff = 1 / 10 ** (sensitivity / 20)
    p = volt * coeff / 10 ** (gain / 20)
    p = np.abs(p)
    p[p == 0] = FLOAT_MIN
    L = 20 * np.log10(p / pRef)
    return L


def LL_to_SPLs(phon: float) -> np.ndarray:
    '''Loudness Level (phon) to Sound Pressure Level (dB) at all frequency'''
    Af = 4.47e-3 * (10 ** (0.025 * phon) - 1.15) + \
        (0.4 * 10 ** (((Tf + Lu) / 10) - 9)) ** af
    Lp = ((10 / af) * np.log10(Af)) - Lu + 94
    return Lp


def SPL_to_LLs(Lp: float) -> np.ndarray:
    '''Sound Pressure Level (dB) to Loudness Level (phon) at all frequency'''
    Af = 10 ** ((Lp + Lu - 94) * af / 10)
    phon = np.log10(
        (Af - (0.4 * 10 ** (((Tf + Lu) / 10) - 9)) ** af) / 4.47e-3 + 1.15) / 0.025
    return phon


def LLs_to_SPLs_at_iFreqs(phon: float | np.ndarray, i_freq: int | np.ndarray) -> float | np.ndarray:
    '''Loudness Level (phon) to Sound Pressure Level (dB) at given frequency f[i_freq]'''
    af_val, Lu_val, Tf_val = af[i_freq], Lu[i_freq], Tf[i_freq]
    Af = 4.47e-3 * (10 ** (0.025 * phon) - 1.15) + \
        (0.4 * 10 ** (((Tf_val + Lu_val) / 10) - 9)) ** af_val
    Lp = ((10 / af_val) * np.log10(Af)) - Lu_val + 94
    return Lp


def SPLs_to_LLs_at_iFreqs(Lp: float | np.ndarray, i_freq: int | np.ndarray) -> float | np.ndarray:
    '''Sound Pressure Level (dB) to Loudness Level (phon) at given frequency f[i_freq]'''
    af_val, Lu_val, Tf_val = af[i_freq], Lu[i_freq], Tf[i_freq]
    Af = 10 ** ((Lp + Lu_val - 94) * af_val / 10)
    phon = np.log10(
        (Af - (0.4 * 10 ** (((Tf_val + Lu_val) / 10) - 9)) ** af[i_freq]) / 4.47e-3 + 1.15) / 0.025
    return phon


def lerp(fn: Callable[[int | np.ndarray], float | np.ndarray], freq: float | np.ndarray) -> np.ndarray:
    i_search = np.searchsorted(f, freq)
    i_left = np.clip(i_search - 1, 0, f.shape[0] - 1)
    i_right = np.clip(i_search, 0, f.shape[0] - 1)
    val_left, val_right = fn(i_left), fn(i_right)
    f_left, f_right = f[i_left], f[i_right]
    f_left[i_search == 0] = 0
    f_right[i_search == f.shape[0]] = 20000
    val = val_left + (val_right - val_left) * \
        (freq - f_left) / (f_right - f_left)
    return val


def LLs_to_SPLs_at_freqs(phon: float | np.ndarray, freq: float | np.ndarray) -> np.ndarray:
    return lerp(lambda i_freq: LLs_to_SPLs_at_iFreqs(phon, i_freq), freq)


def SPLs_to_LLs_at_freqs(Lp: float | np.ndarray, freq: float | np.ndarray) -> np.ndarray:
    return lerp(lambda i_freq: SPLs_to_LLs_at_iFreqs(Lp, i_freq), freq)


if __name__ == '__main__':
    import matplotlib
    from matplotlib import pyplot as plt

    print(f'SPL = {LLs_to_SPLs_at_iFreqs(50, 9)}')  # at 160 hz
    print(f'LL = {SPLs_to_LLs_at_iFreqs(64.6785, 9)}')

    print(f'SPL = {LLs_to_SPLs_at_iFreqs(
        np.array([45, 55, 65]), np.array([9, 10, 11]))}')
    print(f'LL = {SPLs_to_LLs_at_iFreqs(
        np.array([60.72, 65.81, 71.75]), np.array([9, 10, 11]))}')

    print(f'SPLs = {LLs_to_SPLs_at_freqs(
        np.array([40, 50, 60, 70]), np.array([900, 9000, 10, 30000]))}')
    print(f'LLs = {SPLs_to_LLs_at_freqs(
        np.array([40.04, 62.77, 109.51, 77.04]), np.array([900, 9000, 10, 30000]))}')

    for phon in range(0, 100, 10):
        assert np.all(np.abs(SPL_to_LLs(LL_to_SPLs(phon)) - phon) < 1e7)
        plt.plot(f, LL_to_SPLs(phon), label=f'{phon=}')

    plt.xscale('log')
    plt.xticks([20, 40, 80, 160, 315, 630, 1250, 2500, 5000, 10000])
    plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.xlabel('Frequency / Hz')
    plt.ylabel('Sound Pressure Level / dB')
    plt.legend()
    plt.show()
