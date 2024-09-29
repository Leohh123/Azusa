import numpy as np
import matplotlib.pyplot as plt
import time

# # Generating a sample musical note signal
# fs = 1100  # Sampling frequency (Hz)
# duration = 2  # seconds
# frequency = 440  # A4 note frequency (Hz)
# t = np.linspace(0, duration, int(fs * duration), endpoint=False)
# signal = np.sin(2 * np.pi * frequency * t) + \
#     np.random.normal(0, 1, len(t))  # Signal with noise

# # Applying FFT
# start = time.time()
# fft_result = np.fft.fft(signal)
# freq = np.fft.fftfreq(t.shape[-1], d=1/fs)
# elapsed = time.time() - start
# print(f'{elapsed*1000:.2f}ms')

# # Plotting the spectrum
# plt.plot(freq, np.abs(fft_result))
# plt.title('FFT of a Musical Note')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Amplitude')
# plt.show()


class FFT:
    def __init__(self):
        self.frames = []
        self.selected_channel = 0

    def process(self, data: bytes, frame_count, width, channels, rate):
        if data is not None:
            # print(len(data), frame_count, channels, width)
            # assert len(data) == frame_count * channels * width
            d_all = np.fromstring(data, dtype=np.dtype(f'<i{width}'))
            d_select = d_all[self.selected_channel::channels]
            avg = np.mean(d_select)
            print(f'{np.mean(avg):9.4f}')
