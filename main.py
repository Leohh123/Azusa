import pygame
from pygame import mixer

import time
import ctypes
import sys

import common as cm
import prompt
from fft import FFT
from audio import Audio

from matplotlib import pyplot as plt
from debug import debug
import numpy as np


def disable_scaling_for_high_resolution():
    # Query DPI Awareness (Windows 10 and 8)
    awareness = ctypes.c_int()
    errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(
        0, ctypes.byref(awareness))
    print(awareness.value)

    # Set DPI Awareness  (Windows 10 and 8)
    errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    # the argument is the awareness level, which can be 0, 1 or 2:
    # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

    # Set DPI Awareness  (Windows 7 and Vista)
    success = ctypes.windll.user32.SetProcessDPIAware()
    # behaviour on later OSes is undefined, although when I run it on my Windows 10 machine, it seems to work with effects identical to SetProcessDpiAwareness(1)


def maximize_window():
    if sys.platform == 'win32':
        HWND = pygame.display.get_wm_info()['window']
        SW_MAXIMIZE = 3
        ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)


pygame.init()
pygame.mixer.set_num_channels(50)

screen = pygame.display.set_mode([0, 0], pygame.RESIZABLE)
width, height = screen.get_size()

TITLE = 'Azusa \u0e05\u0028\u003d\uff65\u03c9\uff65\u003d\u0029\u0e05 nya~'
pygame.display.set_caption(TITLE)

disable_scaling_for_high_resolution()
maximize_window()


def sz(x):
    '''Get size in pixels'''
    result = max(1, round(x * width / (len(cm.WHITE_NOTES) * cm.WK_WIDTH)))
    return result


def get_font_by_height(path, height):
    l, r = 8, 72
    while r - l > 1:
        m = (l + r) // 2
        font = pygame.font.Font(path, m)
        if font.get_height() <= height:
            l = m
        else:
            r = m
    return pygame.font.Font(path, l)


fonts: dict[str, pygame.font.Font] = {}


def load_fonts():
    fonts['regular'] = get_font_by_height('assets/comic.ttf', sz(72))
    fonts['medium'] = get_font_by_height('assets/comic.ttf', sz(42))
    fonts['small'] = get_font_by_height('assets/comic.ttf', sz(24))
    fonts['mini'] = get_font_by_height('assets/comic.ttf', sz(14))


load_fonts()

timer = pygame.time.Clock()
FPS = 60

white_sounds: list[mixer.Sound] = []
black_sounds: list[mixer.Sound] = []
white_last_times = []
black_last_times = []
cnt_active_whites = [0 for _ in range(len(cm.WHITE_NOTES))]
cnt_active_blacks = [0 for _ in range(len(cm.BLACK_NOTES))]
is_detected_whites = [False for _ in range(len(cm.WHITE_NOTES))]
is_detected_blacks = [False for _ in range(len(cm.BLACK_NOTES))]
left_oct = 3
right_oct = 4
white_keys: list[pygame.Rect] = []
black_keys: list[pygame.Rect] = []


for i in range(len(cm.WHITE_NOTES)):
    white_sounds.append(mixer.Sound(
        f'assets\\notes\\{cm.WHITE_NOTES[i]}.wav'))
    white_last_times.append(0.)

for i in range(len(cm.BLACK_NOTES)):
    black_sounds.append(mixer.Sound(
        f'assets\\notes\\{cm.BLACK_NOTES[i]}.wav'))
    black_last_times.append(0.)


def gradient_vertical_rect(surf: pygame.Surface, top_color, bottom_color, rect_value, width=-1, border_color='black'):
    rect_color = pygame.Surface((2, 2))
    pygame.draw.line(rect_color, top_color, (0, 0), (1, 0))
    pygame.draw.line(rect_color, bottom_color,  (0, 1), (1, 1))
    rect_color = pygame.transform.smoothscale(
        rect_color, rect_value[2:4])
    surf.blit(rect_color, rect_value)
    pygame.draw.rect(surf, border_color, rect_value, width)
    return pygame.Rect(rect_value)


def get_black_key_pos(i):
    return i // 5 * 7 + i % 5 + (i % 5 + 1) // 2


def draw_piano():
    white_keys.clear()
    black_keys.clear()
    for i, label in enumerate(cm.WHITE_NOTES):
        rect = gradient_vertical_rect(
            screen,
            cm.ORANGE_COLOR if is_detected_whites[i] else cm.WK_COLOR,
            cm.ORANGE_COLOR if cnt_active_whites[i] > 0 else cm.WK_COLOR, [
                sz(i * cm.WK_WIDTH),
                height - sz(cm.WK_HEIGHT),
                sz((i + 1) * cm.WK_WIDTH) - sz(i * cm.WK_WIDTH),
                sz(cm.WK_HEIGHT)
            ], sz(1)
        )
        white_keys.append(rect)
        key_label = fonts['small'].render(label, True, 'black')
        screen.blit(
            key_label, [
                sz((i + 0.5) * cm.WK_WIDTH) - key_label.get_width() // 2,
                height - fonts['small'].get_height()
            ]
        )
    for i, label in enumerate(cm.BLACK_NOTES):
        pos = get_black_key_pos(i)
        rect = gradient_vertical_rect(
            screen,
            cm.BLUE_COLOR if is_detected_blacks[i] else cm.BK_COLOR,
            cm.BLUE_COLOR if cnt_active_blacks[i] > 0 else cm.BK_COLOR, [
                sz((pos + 1) * cm.WK_WIDTH - cm.BK_WIDTH / 2),
                height - sz(cm.WK_HEIGHT), sz(cm.BK_WIDTH), sz(cm.BK_HEIGHT)
            ]
        )
        key_label = fonts['mini'].render(label, True, 'white')
        screen.blit(
            key_label, [
                sz((pos + 1) * cm.WK_WIDTH) - key_label.get_width() // 2,
                height - sz(cm.WK_HEIGHT - cm.BK_HEIGHT) -
                fonts['mini'].get_height()
            ]
        )
        black_keys.append(rect)


def draw_hands():
    for hand, wk_cnt, num_oct, h_rate in [
        [cm.LEFT_HAND, cm.LEFT_WK_CNT, left_oct, 0.15],
        [cm.RIGHT_HAND, cm.RIGHT_WK_CNT, right_oct, 0.22]
    ]:
        bar_h_half = int(fonts['mini'].get_height() * 0.6)
        pygame.draw.rect(
            screen, 'dark gray', [
                sz((num_oct * 7 + 2) * cm.WK_WIDTH),
                height - sz(cm.WK_HEIGHT * h_rate) -
                bar_h_half,
                sz(wk_cnt * cm.WK_WIDTH),
                bar_h_half * 2
            ], 0, bar_h_half
        )
        for i, ch in enumerate(hand):
            note = cm.ALL_NOTES[i + num_oct * 12 + 3]
            if note[1] == 'b':
                index = cm.BLACK_NOTES.index(note)
                pos = get_black_key_pos(index)
                text = fonts['mini'].render(ch, True, 'white')
                screen.blit(text, [
                    sz((pos + 1) * cm.WK_WIDTH) - text.get_width() // 2,
                    height - sz(cm.WK_HEIGHT * h_rate) -
                    fonts['mini'].get_height() // 2
                ])
            else:
                index = cm.WHITE_NOTES.index(note)
                text = fonts['mini'].render(ch, True, 'black')
                screen.blit(text, [
                    sz((index + 0.5) * cm.WK_WIDTH) - text.get_width() // 2,
                    height - sz(cm.WK_HEIGHT * h_rate) -
                    fonts['mini'].get_height() // 2
                ])


run = True
is_mouse_down = False
mouse_black_index = None
mouse_white_index = None


def try_stop_black(index: int):
    cnt_active_blacks[index] -= 1


def try_stop_white(index: int):
    cnt_active_whites[index] -= 1


def resume_cnt_for_mouse():
    global mouse_black_index, mouse_white_index
    if mouse_black_index is not None:
        try_stop_black(mouse_black_index)
        mouse_black_index = None
    if mouse_white_index is not None:
        try_stop_white(mouse_white_index)
        mouse_white_index = None


def try_play_black(index: int, is_mouse=False):
    global mouse_black_index
    if cnt_active_blacks[index] == 0:
        black_sounds[index].play()
        black_last_times[index] = time.time()
    if is_mouse:
        resume_cnt_for_mouse()
        mouse_black_index = index
    cnt_active_blacks[index] += 1


def try_play_white(index: int, is_mouse=False):
    global mouse_white_index
    if cnt_active_whites[index] == 0:
        white_sounds[index].play()
        white_last_times[index] = time.time()
    if is_mouse:
        resume_cnt_for_mouse()
        mouse_white_index = index
    cnt_active_whites[index] += 1


def check_keys_stop():
    now = time.time()
    for i, sound in enumerate(white_sounds):
        if cnt_active_whites[i] == 0 and \
                now - white_last_times[i] > 0.25:
            sound.fadeout(100)
    for i, sound in enumerate(black_sounds):
        if cnt_active_blacks[i] == 0 and \
                now - black_last_times[i] > 0.25:
            sound.fadeout(100)


note_on_psd = None


def click_key(event: pygame.event.Event):
    if note_on_psd is None:
        is_black_key = False
        for i in range(len(black_keys)):
            if black_keys[i].collidepoint(event.pos):
                is_black_key = True
                try_play_black(i, True)
                break
        if not is_black_key:
            for i in range(len(white_keys)):
                if white_keys[i].collidepoint(event.pos):
                    try_play_white(i, True)
                    break
    else:
        if note_on_psd[1] == 'b':
            index = cm.BLACK_NOTES.index(note_on_psd)
            try_play_black(index, True)
        else:
            index = cm.WHITE_NOTES.index(note_on_psd)
            try_play_white(index, True)


audio = Audio()
fft = FFT()

audio.record(fft.process)


def draw_line_on_psd(rect: pygame.Rect, index_note: int):
    f = cm.ALL_FREQS[index_note]
    i_freq = np.argmin(np.abs(fft.freq - f))
    y_freq = rect.bottom - (i_freq * rect.height // fft.freq.shape[0])
    # print(i_freq, fft.freq[i_freq], rect.bottom,
    #       y_freq, fft.freq.shape, pygame.mouse.get_pos())
    pygame.draw.line(
        screen, 'blue',
        [rect.left, y_freq], [rect.right, y_freq])
    text = fonts['mini'].render(cm.ALL_NOTES[index_note], True, 'blue')
    screen.blit(
        text, [
            rect.right - text.get_width(),
            y_freq - text.get_height()
        ]
    )


def draw_psd():
    global note_on_psd
    if fft.image is not None:
        with fft.lock_image:
            im_rotated = pygame.transform.rotate(fft.image, 90)
        im_scaled = pygame.transform.smoothscale(
            im_rotated, [screen.get_width(), 600])
        rect = screen.blit(im_scaled, [0, 0])
        # draw_line_at_frequency(440., rect)
        x, y = pygame.mouse.get_pos()
        if rect.collidepoint(x, y):
            i_mouse = np.clip(
                (rect.bottom - y) * fft.freq.shape[0] // rect.height,
                0, fft.freq.shape[0] - 1)
            f_mouse = fft.freq[i_mouse]
            ni_close = np.argmin(np.abs(cm.ALL_FREQS - f_mouse))
            draw_line_on_psd(rect, ni_close)
            note_on_psd = cm.ALL_NOTES[ni_close]
        else:
            note_on_psd = None


def update_detect_status():
    if fft.spl is None:
        return
    global is_detected_whites, is_detected_blacks
    is_detected_whites = [False for _ in range(len(cm.WHITE_NOTES))]
    is_detected_blacks = [False for _ in range(len(cm.BLACK_NOTES))]
    for note, freq in cm.NOTE2FREQ.items():
        i_freq = np.argmin(np.abs(fft.freq - freq))
        val = fft.spl[i_freq]
        if val > fft.db_range[0]:
            if note[1] == 'b':
                index = cm.BLACK_NOTES.index(note)
                is_detected_blacks[index] = True
            else:
                index = cm.WHITE_NOTES.index(note)
                is_detected_whites[index] = True


while run:
    timer.tick(FPS)
    screen.fill('gray')
    # for i in range(0, width//100+1):
    #     for j in range(0, height//100+1):
    #         pygame.draw.rect(screen, ['black', 'white']
    #                          [(i+j) % 2], [i*100, j*100, 100, 100])
    if not debug:
        draw_piano()
        draw_hands()
    draw_psd()
    update_detect_status()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            is_mouse_down = True
            click_key(event)
        if event.type == pygame.MOUSEBUTTONUP:
            is_mouse_down = False
            resume_cnt_for_mouse()
        if event.type == pygame.MOUSEMOTION:
            if is_mouse_down:
                click_key(event)
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name in cm.LEFT_HAND:
                index_all = cm.LEFT_HAND.index(key_name) + left_oct * 12 + 3
                note = cm.ALL_NOTES[index_all]
                if note[1] == 'b':
                    index = cm.BLACK_NOTES.index(note)
                    try_play_black(index)
                else:
                    index = cm.WHITE_NOTES.index(note)
                    try_play_white(index)
            elif key_name in cm.RIGHT_HAND:
                index_all = cm.RIGHT_HAND.index(key_name) + right_oct * 12 + 3
                note = cm.ALL_NOTES[index_all]
                if note[1] == 'b':
                    index = cm.BLACK_NOTES.index(note)
                    try_play_black(index)
                else:
                    index = cm.WHITE_NOTES.index(note)
                    try_play_white(index)
            elif event.key == pygame.K_PAGEUP and right_oct < 8:
                right_oct += 1
            elif event.key == pygame.K_PAGEDOWN and right_oct > 0:
                right_oct -= 1
            elif event.key == pygame.K_HOME and left_oct < 8:
                left_oct += 1
            elif event.key == pygame.K_END and left_oct > 0:
                left_oct -= 1

        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            if key_name in cm.LEFT_HAND:
                index_all = cm.LEFT_HAND.index(key_name) + left_oct * 12 + 3
                note = cm.ALL_NOTES[index_all]
                if note[1] == 'b':
                    index = cm.BLACK_NOTES.index(note)
                    try_stop_black(index)
                else:
                    index = cm.WHITE_NOTES.index(note)
                    try_stop_white(index)
            elif key_name in cm.RIGHT_HAND:
                index_all = cm.RIGHT_HAND.index(key_name) + right_oct * 12 + 3
                note = cm.ALL_NOTES[index_all]
                if note[1] == 'b':
                    index = cm.BLACK_NOTES.index(note)
                    try_stop_black(index)
                else:
                    index = cm.WHITE_NOTES.index(note)
                    try_stop_white(index)
            if event.key == pygame.K_F1:
                filename = prompt.open_file()
                try:
                    fft.clear_window()
                    audio.read(filename, fft.process)
                except Exception as e:
                    prompt.info(str(e))
            elif event.key == pygame.K_F2:
                fft.clear_window()
                audio.record(fft.process)
            elif event.key == pygame.K_F3:
                # prompt.dashboard()
                try:
                    thresh_psd = float(input('thresh_psd: '))
                except:
                    pass
            elif event.key == pygame.K_F4:
                # prompt.dashboard()
                try:
                    fft.db_range[0] = float(input('max_psd: '))
                except:
                    pass
            elif event.key == pygame.K_F11:
                fft.set_channel(0)
            elif event.key == pygame.K_F12:
                fft.set_channel(1)

        if event.type == pygame.VIDEORESIZE:
            width, height = screen.get_size()
            print(f'resize: {width=}, {height=}')
            load_fonts()

    check_keys_stop()

    pygame.display.flip()


pygame.quit()
audio.close()
