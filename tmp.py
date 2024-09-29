# import tkinter as tk
# from PIL import Image, ImageTk, ImageDraw


# class Paint:
#     def __init__(self, width=800, height=600):
#         self.width = width
#         self.height = height
#         self.root = tk.Tk()

#         self.canvas = tk.Canvas(
#             self.root, width=self.width, height=self.height)
#         self.canvas.grid(row=0)

#         self.modify_button = tk.Button(
#             self.root, text='Modify', command=self.modify)
#         self.modify_button.grid(row=1, sticky='ew')

#         self.image = Image.new('RGB', (self.width, self.height), 'white')
#         self.draw = ImageDraw.Draw(self.image)
#         self.image_id = None
#         self.update()

#         self.old_x = None
#         self.old_y = None
#         self.canvas.bind('<B1-Motion>', self.pen_down)
#         self.canvas.bind('<ButtonRelease-1>', self.pen_up)

#         self.root.mainloop()

#     def update(self):
#         self.imageTk = ImageTk.PhotoImage(self.image)
#         if self.image_id is not None:
#             self.canvas.delete(self.image_id)
#         self.image_id = self.canvas.create_image(
#             self.width,
#             self.height,
#             image=self.imageTk,
#             state='normal',
#             anchor='se',
#         )
#         all = self.canvas.find_all()
#         print(len(all))

#     def pen_down(self, event):
#         if self.old_x and self.old_y:
#             self.draw.line(
#                 [self.old_x, self.old_y, event.x, event.y],
#                 width=4,
#                 fill='black',
#             )
#             self.draw = ImageDraw.Draw(self.image)
#             self.update()
#         self.old_x = event.x
#         self.old_y = event.y

#     def pen_up(self, event):
#         self.old_x, self.old_y = None, None

#     def modify(self):
#         new_image = Image.eval(self.image, lambda x: 100 + x)
#         self.image = new_image
#         self.update()


# if __name__ == '__main__':
#     Paint()

# import tkinter
# import tkinter.filedialog
# import pygame

# WIDTH = 640
# HEIGHT = 480
# FPS = 30

# def prompt_file():
#     """Create a Tk file dialog and cleanup when finished"""
#     top = tkinter.Tk()
#     top.withdraw()  # hide window
#     file_name = tkinter.filedialog.askopenfilename(parent=top)
#     top.destroy()
#     return file_name

# pygame.init()
# window = pygame.display.set_mode((WIDTH, HEIGHT))
# clock = pygame.time.Clock()

# f = "<No File Selected>"
# frames = 0
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYUP:
#             if event.key == pygame.K_SPACE:
#                 f = prompt_file()

#     # draw surface - fill background
#     window.fill(pygame.color.Color("grey"))
#     ## update title to show filename
#     pygame.display.set_caption(f"Frames: {frames:10}, File: {f}")
#     # show surface
#     pygame.display.update()
#     # limit frames
#     clock.tick(FPS)
#     frames += 1
# pygame.quit()

# import io
# from pydub import AudioSegment
# from pydub.generators import Sine
# from pydub.playback import play
# from pynput.keyboard import Key, Listener
# import threading
# from math import log2

# # Function to generate a sine wave tone
# def generate_tone(frequency, duration=500):
#     """
#     Generate a sine wave tone with the given frequency and duration.
#     Args:
#         frequency (float): The frequency of the tone in Hz.
#         duration (int, optional): The duration of the tone in milliseconds. Defaults to 500.
#     Returns:
#         pydub.AudioSegment: The generated tone.
#     """
#     tone = Sine(frequency).to_audio_segment(duration=duration)
#     return tone

# # Function to play the generated tone
# def play_tone(tone):
#     """
#     Play the given audio tone.
#     Args:
#         tone (pydub.AudioSegment): The audio tone to be played.
#     """
#     try:
#         play(tone)  # play the audio using pydub.playback.play
#     except Exception as error:
#         print(f"Error in playing tone: {error}")

# # Mapping keyboard keys to piano notes (simplified)
# key_to_note = {
#     'a': 261.63,  # C4
#     'w': 277.18,  # C#4/Db4
#     's': 293.66,  # D4
#     'e': 311.13,  # D#4/Eb4
#     'd': 329.63,  # E4
#     'f': 349.23,  # F4
#     't': 369.99,  # F#4/Gb4
#     'g': 392.00,  # G4
#     'y': 415.30,  # G#4/Ab4
#     'h': 440.00,  # A4
#     'u': 466.16,  # A#4/Bb4
#     'j': 493.88,  # B4
#     'k': 523.25,  # C5
#     'o': 554.37,  # C#5/Db5
#     'l': 587.33,  # D5
#     'p': 622.25,  # D#5/Eb5
#     ';': 659.25,  # E5
#     '\'': 698.46,  # F5
#     ']': 739.99,  # F#5/Gb5
#     '\\': 783.99,  # G5
#     'z': 830.61,  # G#5/Ab5
#     'x': 880.00,  # A5
#     'c': 932.33,  # A#5/Bb5
#     'v': 987.77,  # B5
#     'b': 1046.50,  # C6
# }
# key_to_segment = {k: generate_tone(v) for k, v in key_to_note.items()}

# # Function to handle key press
# def on_press(key):
#     """
#     Handle the key press event.
#     Args:
#         key (pynput.keyboard.Key): The key that was pressed.
#     """
#     # try:
#     if hasattr(key, 'char') and key.char in key_to_note:
#         frequency = key_to_note[key.char]
#         # print(frequency)
#         # tone = generate_tone(frequency)
#         threading.Thread(target=play_tone, args=(key_to_segment[key.char],)).start()
#     # except Exception as error:
#     #     print(f"Error in key press handler: {error}")

# # Function to handle key release
# def on_release(key):
#     """
#     Handle the key release event.
#     Args:
#         key (pynput.keyboard.Key): The key that was released.
#     Returns:
#         bool: False to stop the listener.
#     """
#     if key == Key.esc:
#         return False  # Stop listener

# # Main function to start the keyboard listener
# def start_keyboard_piano():
#     """
#     Start the keyboard listener to play piano notes.
#     """
#     with Listener(on_press=on_press, on_release=on_release) as listener:
#         listener.join()

# def frequency_to_note(frequency):
#     """
#     Convert a frequency to its corresponding musical note.
#     Args:
#         frequency (float): The frequency of the note in Hz.
#     Returns:
#         str: The musical note name.
#     """
#     note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
#     octave = 4
#     index = int(round(12 * log2(frequency / 440.0))) + 49
#     return note_names[index % 12] + str(octave + index // 12)

# if __name__ == "__main__":
#     try:
#         print("Key Note")
#         sharp_keys = [key for key, frequency in key_to_note.items() if '#' in frequency_to_note(frequency)]
#         natural_keys = [key for key, frequency in key_to_note.items() if '#' not in frequency_to_note(frequency)]
#         print(' '.join([frequency_to_note(key_to_note[key]) for key in sharp_keys]))
#         print(' '.join([frequency_to_note(key_to_note[key]) for key in natural_keys]))
#         start_keyboard_piano()
#     except Exception as error:
#         print(f"Error in main function: {error}")


# import pyaudio  # Soundcard audio I/O access library
# import wave  # Python 3 module for reading / writing simple .wav files

# # Setup channel info
# FORMAT = pyaudio.paInt16  # data type formate
# CHANNELS = 2  # Adjust to your number of channels
# RATE = 44100  # Sample Rate
# CHUNK = 1024  # Block Size
# RECORD_SECONDS = 10  # Record time
# WAVE_OUTPUT_FILENAME = "file.wav"

# # Startup pyaudio instance
# audio = pyaudio.PyAudio()

# # start Recording
# stream = audio.open(format=FORMAT, channels=CHANNELS,
#                     rate=RATE, input=True, output=True,
#                     frames_per_buffer=CHUNK)
# print("recording...")
# frames = []

# # Record for RECORD_SECONDS
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     stream.write(data)
#     frames.append(data)
# print("finished recording")


# # Stop Recording
# stream.stop_stream()
# stream.close()
# audio.terminate()

# # Write your new .wav file with built in Python 3 Wave module
# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()

# import tkinter

# # top = tkinter.Tk()

# # top.destroy()

# import pyaudio
# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     print(p.get_device_info_by_index(i))


# import threading

# num = 0


# def add():
#     global num
#     for i in range(10_000_000):
#         tmp = num
#         num = tmp + 1


# def sub():
#     global num
#     for i in range(10_000_000):
#         tmp = num
#         num = tmp - 1


# if __name__ == "__main__":
#     subThread01 = threading.Thread(target=add)
#     subThread02 = threading.Thread(target=sub)

#     subThread01.start()
#     subThread02.start()

#     subThread01.join()
#     subThread02.join()

#     print("num result : %s" % num)

# # 结果三次采集
# # num result : 669214
# # num result : -1849179
# # num result : -525674


# import pygame
# import random

# pygame.init()
# W, H = 200, 200
# screen = pygame.display.set_mode([W, H])

# im = pygame.image.load('./2x2.png')
# b = pygame.image.tobytes(im, 'RGB')
# print(b, list(map(hex, b)))

# ba = bytearray(b)

# # im2 = pygame.image.frombytes(b, [2, 2], 'RGB')
# im2 = pygame.image.frombuffer(ba, [2, 2], 'RGB')

# timer = pygame.time.Clock()
# while True:
#     timer.tick(60)
#     screen.fill('gray')
#     im_scaled = pygame.transform.scale(im2, (W, H))
#     screen.blit(im_scaled, [0, 0])
#     # screen.blit(im2, [0, 0])
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             exit()
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_TAB:
#                 while True:
#                     try:
#                         cmd = input('Eval: ')
#                         if cmd.startswith('quit'):
#                             break
#                         print(eval(cmd))
#                     except Exception as e:
#                         print(e)
#             if event.key == pygame.K_ESCAPE:
#                 ba[:len(ba)] = random.randbytes(len(ba))
#                 print(ba)

#     pygame.display.flip()

import wave
import sys

import pyaudio
import numpy as np
from matplotlib import pyplot as plt

CHUNK = 1024

if len(sys.argv) < 2:
    print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
    sys.exit(-1)

with wave.open(sys.argv[1], 'rb') as wf:
    # Instantiate PyAudio and initialize PortAudio system resources (1)
    p = pyaudio.PyAudio()

    # Open stream (2)
    width = wf.getsampwidth()
    channels = wf.getnchannels()
    rate = wf.getframerate()
    stream = p.open(format=p.get_format_from_width(width),
                    channels=channels,
                    rate=rate,
                    output=True)

    frames = []
    # Play samples from the wave file (3)
    while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
        # try:
        stream.write(data)
        # except KeyboardInterrupt:
        d_all = np.fromstring(data, dtype=np.dtype(f'<i{width}'))
        f = d_all[0::channels]
        n: int = f.shape[0]
        fhat = np.fft.fft(f)
        freq = np.fft.fftfreq(n, d=1/rate)
        mask = (freq > 0) & (freq <= 5000)
        fhat = fhat[mask]
        freq = freq[mask]
        print(freq, freq.shape)
        psd = (fhat * np.conj(fhat) / n).real
        # plt.plot(freq, np.log(psd))
        # plt.show()
        # break
        if len(frames) == 0 or frames[-1].shape[0] == psd.shape[0]:
            frames.append(np.log(psd)/np.log(1e12))
            print('append')
    psd_all = np.vstack(frames)
    plt.imshow(psd_all.T, cmap='grey', aspect='auto', vmin=0, vmax=1)
    plt.colorbar()
    plt.gca().invert_yaxis()
    plt.show()

    # Close stream (4)
    stream.close()

    # Release PortAudio system resources (5)
    p.terminate()
