import numpy as np
import matplotlib.pyplot as plt
import time
import threading
import pygame

import iso226


class RQueue:
    def __init__(self, size):
        self.length = size + 1
        self.data = [None for _ in range(self.length)]
        self.head = 0
        self.tail = 0

    def __len__(self):
        return (self.tail - self.head + self.length) % self.length

    def put(self, obj):
        self.data[self.tail] = obj
        self.tail = (self.tail + 1) % self.length
        if self.head == self.tail:
            self.data[self.head] = None
            self.head = (self.head + 1) % self.length

    def get(self):
        if self.head == self.tail:
            return None
        result = self.data[self.head]
        self.data[self.head] = None
        self.head = (self.head + 1) % self.length
        return result

    def clear(self):
        self.data = [None for _ in range(self.length)]
        self.head = 0
        self.tail = 0

    def resize(self, new_size):
        while len(self) > new_size:
            self.get()
        if self.head <= self.tail:
            new_data = self.data[self.head: self.tail]
        else:
            new_data = self.data[self.head:] + self.data[:self.tail]
        self.data = new_data + [None for _ in range(new_size + 1 - len(self))]
        self.tail = len(self)
        self.head = 0
        self.length = new_size + 1

    def __iter__(self):
        pos = self.head
        while pos != self.tail:
            yield self.data[pos]
            pos = (pos + 1) % self.length

    def convert_index(self, index):
        if index is None:
            return None
        if index >= 0:
            if index > self.length - 1:
                raise IndexError(f'Invalid index {index}')
            return (self.head + index) % self.length
        else:
            if -index > self.length:
                raise IndexError(f'Invalid index {index}')
            return (self.tail + index + self.length) % self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            if self.head == self.tail:
                raise IndexError(f'Invalid index {key}')
            index = self.convert_index(key)
            return self.data[index]
        elif isinstance(key, slice):
            s = slice(
                self.convert_index(key.start),
                self.convert_index(key.stop),
                key.step
            )
            print(s)
            return [self[i] for i in range(self.length - 1)[s]]
        raise TypeError(f'Invalid index type of {key}')


class FFT:
    def __init__(self):
        self.window_size = 5
        self.frames = RQueue(self.window_size)
        self.lock_frames = threading.RLock()
        self.ch_selected = 0
        self.num_rows = 2000
        self.color = [77, 171, 207]
        self.image = None
        self.lock_image = threading.RLock()
        self.freq = None
        self.psd: np.ndarray = None
        self.spl: np.ndarray = None
        # self.loudness: np.ndarray = None
        self.db_range = [90, 80]
        # self.last_cycle_time = time.time()
        # self.cnt_cycle = 0

    def clear_window(self):
        with self.lock_frames:
            self.frames.clear()
        with self.lock_image:
            self.image = None
        self.psd = None
        self.freq = None
        self.spl = None
        self.loudness = None

    def set_channel(self, channel):
        self.ch_selected = channel
        with self.lock_frames:
            self.frames.clear()

    def set_window(self, window):
        with self.lock_frames:
            self.window_size = window
            self.frames.resize(window)

    # def set_max_psd(self, v):
    #     self.max_psd = v

    def process(self, data: bytes, frame_count, width, channels, rate):
        if data is not None:
            # self.cnt_cycle += 1
            # if self.cnt_cycle == self.window_size:
            #     self.cnt_cycle = 0
            #     print(time.time() - self.last_cycle_time)
            #     self.last_cycle_time = time.time()
            # assert len(data) == frame_count * channels * width
            d_all = np.fromstring(data, dtype=np.dtype(f'<i{width}'))
            d_select = d_all[self.ch_selected::channels]
            with self.lock_frames:
                self.frames.put(d_select)
                # print(len(self.frames))
                if len(self.frames) == self.window_size:
                    self.compute_psd(width, rate)
                    self.update_image()

    def compute_psd(self, width, rate):
        with self.lock_frames:
            f = np.concatenate(self.frames)
        half = 2 ** (width * 8 - 1)
        f = (f - half) / half
        n: int = f.shape[0]
        fhat = np.fft.fft(f)
        freq = np.fft.fftfreq(n, d=1/rate)
        mask = (freq > 0) & (freq <= 5000)
        fhat = fhat[mask]
        self.freq = freq[mask]
        # Power Spectral Density (PSD), proportional to Amplitude^2
        self.psd = (fhat * np.conj(fhat) / n).real
        self.spl = iso226.PSDs_to_SPLs(self.psd)
        # self.loudness = iso226.SPLs_to_LLs_at_freqs(self.spl, self.freq)
        # print(np.mean(np.abs(f)), np.mean(np.abs(self.psd)))
        # print(np.min(self.psd), np.max(self.psd))
        # print(np.mean(self.spl), np.min(self.spl), np.max(self.spl), np.mean(
        #     np.abs(self.spl)), np.min(np.abs(self.spl)), np.max(np.abs(self.spl)), sep='\t')
        # print(np.mean(self.loudness), np.min(self.loudness), np.max(self.loudness), np.mean(
        #     np.abs(self.loudness)), np.min(np.abs(self.loudness)), np.max(np.abs(self.loudness)), sep='\t')

    def update_image(self):
        if self.psd is None:
            return
        with self.lock_image:
            if self.image is None:
                total = self.num_rows * self.psd.shape[0] * 3
                self.image = pygame.image.frombytes(
                    b'\0' * total, [self.psd.shape[0], self.num_rows], 'RGB')
                # print(f'reset {self.image.get_size()=}')
            self.image.blit(self.image, [0, -1])

        if_id = 3
        # if if_id == 1:
        #     # psd_norm = np.clip(np.log(self.psd) / np.log(self.max_psd), 0., 0.999)
        #     # psd_norm = np.clip(np.log(self.psd) / np.log(max(np.max(self.psd), self.max_psd)), 0., 0.999)
        #     # psd_display = psd_norm ** 4
        #     psd_norm = np.clip(self.psd, 0., 0.999)
        #     psd_display = psd_norm
        #     row = np.repeat(
        #         np.floor(psd_display * 256).astype('<u1'), 3).tobytes()
        #     print(np.mean(self.psd), np.min(self.psd), np.max(self.psd),
        #           np.mean(np.abs(self.psd)), np.min(np.abs(self.psd)), np.max(np.abs(self.psd)), sep='\t')

        # elif if_id == 2:
        #     # loudness_norm = np.clip((self.loudness - self.db_range[0]) / (
        #     #     self.db_range[1] - self.db_range[0]), 0., 0.999)
        #     d1 = self.loudness - self.db_range[0]
        #     d2 = self.db_range[1] - self.db_range[0]
        #     loudness_norm = np.clip(10 ** d1, 0, 10 ** d2) / 10 ** d2
        #     loudness_display = loudness_norm
        #     # loudness_display = loudness_norm ** 4
        #     row = np.repeat(
        #         np.floor(loudness_display * 255).astype('<u1'), 3).tobytes()

        # else:
        d1 = self.spl - self.db_range[0]
        d2 = self.db_range[1] - self.db_range[0]
        spl_norm = np.clip(2 ** d1, 0, 2 ** d2) / 2 ** d2
        spl_display = np.clip(np.floor(spl_norm * 256), 0, 255)
        # spl_display = spl_norm ** 4
        row = np.repeat(spl_display.astype('<u1'), 3).tobytes()

        im_row = pygame.image.frombytes(row, [self.psd.shape[0], 1], 'RGB')
        with self.lock_image:
            self.image.blit(im_row, [0, self.num_rows - 1])
        # print(np.mean(self.spl))
        # print(len(row), self.psd.shape, self.freq.shape,
        #       self.image.get_size(), im_row.get_size())

    # def plot_psd(self, screen: pygame.Surface):
    #     if self.image is not None:
    #         with self.lock_image:
    #             im_rotated = pygame.transform.rotate(self.image, 90)
    #         im_scaled = pygame.transform.smoothscale(
    #             im_rotated, [screen.get_width(), 600])
    #         screen.blit(im_scaled, [0, 0])


if __name__ == '__main__':
    q = RQueue(4)
    q.put(233)
    for i in range(5):
        print(list(q), len(q))
        q.put(i)
    print(list(q))
    print(q[0], q[1], q[3], q[-1], q[-4])
    print(q[1:3])
    print(q[0::2])
    print(q[-4::2])
    print(q[-1:-5:-2])
    print(q.get())
    print(list(q))
    print(q.data, q.head, q.tail)
    q.resize(10)
    print(q.data, q.head, q.tail)
