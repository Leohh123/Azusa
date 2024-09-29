import numpy as np
import matplotlib.pyplot as plt
import time
import threading
import pygame


class FFT:
    def __init__(self):
        self.frames = []
        self.lock_frames = threading.RLock()
        self.ch_selected = 0
        self.resolution = 5
        self.num_rows = 2000
        # self.buffer = bytearray()
        # self.lock_buffer = threading.RLock()
        self.max_psd = 1e12
        self.color = [77, 171, 207]
        self.image = None
        self.lock_image = threading.RLock()
        self.psd: np.ndarray = None

    def set_channel(self, channel):
        self.ch_selected = channel
        with self.lock_frames:
            self.frames.clear()

    def set_resolution(self, resolution):
        with self.lock_frames:
            self.resolution = resolution
            self.frames.clear()

    def set_max_psd(self, v):
        self.max_psd = v

    def process(self, data: bytes, frame_count, width, channels, rate):
        if data is not None:
            # assert len(data) == frame_count * channels * width
            d_all = np.fromstring(data, dtype=np.dtype(f'<i{width}'))
            d_select = d_all[self.ch_selected::channels]
            self.lock_frames.acquire()
            self.frames.append(d_select)
            if len(self.frames) >= self.resolution:
                self.compute_psd(rate)
                print(self.psd.shape, frame_count)
                self.lock_frames.release()
            else:
                self.lock_frames.release()
            self.update_image()

    def compute_psd(self, rate):
        with self.lock_frames:
            f = np.concatenate(self.frames)
            self.frames.clear()
        n: int = f.shape[0]
        fhat = np.fft.fft(f)
        freq = np.fft.fftfreq(n, d=1/rate)
        mask = (freq > 0) & (freq <= 5000)
        fhat = fhat[mask]
        freq = freq[mask]
        # print(freq, freq.shape)
        # PSD: Power Spectral Density
        self.psd = (fhat * np.conj(fhat) / n).real

        # pairs = np.vstack([psd, freq]).T.tolist()
        # sorted_pairs = sorted(pairs, key=lambda p: p[0], reverse=True)
        # print(' '.join([f'{sorted_pairs[i][1]:5.0f}' for i in range(5)]))

    def update_image(self):
        if self.psd is None:
            return
        with self.lock_image:
            if self.image is None:
                total = self.num_rows * self.psd.shape[0] * 3
                self.image = pygame.image.frombytes(
                    b'\0' * total, [self.psd.shape[0], self.num_rows], 'RGB')
            self.image.blit(self.image, [0, -1])
        psd_norm = np.clip(np.log(self.psd) / np.log(self.max_psd), 0., 0.999)
        psd_display = psd_norm ** 4
        # psd_norm = np.clip((psd) / (self.max_psd), 0., 1.)
        # psd_display = psd_norm
        row = np.repeat(
            np.floor(psd_display * 256).astype('<u1'), 3).tobytes()
        im_row = pygame.image.frombytes(row, [self.psd.shape[0], 1], 'RGB')
        with self.lock_image:
            self.image.blit(im_row, [0, self.num_rows - 1])

    def plot(self, screen: pygame.Surface):
        if self.image is not None:
            with self.lock_image:
                im_rotated = pygame.transform.rotate(self.image, 90)
            im_scaled = pygame.transform.smoothscale(
                im_rotated, [screen.get_width(), 600])
            screen.blit(im_scaled, [0, 0])
