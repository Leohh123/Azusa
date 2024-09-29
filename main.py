import pygame
from pygame import mixer

import ctypes
import sys

import common
import prompt
from fft import FFT
from audio import Audio

from matplotlib import pyplot as plt


debug = True


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
WIDTH, HEIGHT = screen.get_size()

title = 'Azusa \u0e05\u0028\u003d\uff65\u03c9\uff65\u003d\u0029\u0e05 nya~'
pygame.display.set_caption(title)

disable_scaling_for_high_resolution()
maximize_window()


def sz(x):
    '''Get size in pixels'''
    result = round(x * WIDTH / (52 * 35))
    return result


font = pygame.font.Font('assets/Terserah.ttf', sz(72))
medium_font = pygame.font.Font('assets/Terserah.ttf', sz(42))
small_font = pygame.font.Font('assets/Terserah.ttf', sz(24))
real_small_font = pygame.font.Font('assets/Terserah.ttf', sz(15))
timer = pygame.time.Clock()
fps = 60

white_sounds: list[mixer.Sound] = []
black_sounds: list[mixer.Sound] = []
cnt_active_whites = [0 for _ in range(len(common.white_notes))]
cnt_active_blacks = [0 for _ in range(len(common.black_notes))]
left_oct = 4
right_oct = 5

left_hand = common.left_hand
right_hand = common.right_hand
white_notes = common.white_notes
black_notes = common.black_notes
black_labels = common.black_labels

for i in range(len(white_notes)):
    white_sounds.append(mixer.Sound(f'assets\\notes\\{white_notes[i]}.wav'))

for i in range(len(black_notes)):
    black_sounds.append(mixer.Sound(f'assets\\notes\\{black_notes[i]}.wav'))


def draw_piano():
    pygame.draw.rect(
        screen, 'black',
        [0, HEIGHT - sz(300), WIDTH, sz(300)],
        0, sz(2))
    white_rects = []
    for i in range(52):
        rect = pygame.draw.rect(
            screen,
            '#facc94' if cnt_active_whites[i] > 0 else '#f8f8f8',
            [sz(i * 35), HEIGHT - sz(300), sz(35), sz(300)],
            0, sz(2))
        white_rects.append(rect)
        pygame.draw.rect(
            screen, 'black',
            [sz(i * 35), HEIGHT - sz(300), sz(35), sz(300)],
            sz(2), sz(2))
        key_label = small_font.render(white_notes[i], True, 'black')
        screen.blit(key_label, [sz(i * 35 + 3), HEIGHT - sz(20)])
    skip_count = 0
    last_skip = 2
    skip_track = 2
    black_rects = []
    for i in range(36):
        rect = pygame.draw.rect(
            screen,
            '#76c3ed' if cnt_active_blacks[i] > 0 else '#111111',
            [sz(23 + (i * 35) + (skip_count * 35)),
             HEIGHT - sz(300), sz(24), sz(200)],
            0, sz(2))
        key_label = real_small_font.render(black_labels[i], True, 'white')
        screen.blit(
            key_label,
            [sz(25 + (i * 35) + (skip_count * 35)), HEIGHT - sz(120)])
        black_rects.append(rect)
        skip_track += 1
        if last_skip == 2 and skip_track == 3:
            last_skip = 3
            skip_track = 0
            skip_count += 1
        elif last_skip == 3 and skip_track == 2:
            last_skip = 2
            skip_track = 0
            skip_count += 1

    return white_rects, black_rects


def draw_hands(rightOct, leftOct, rightHand, leftHand):
    # left hand
    pygame.draw.rect(screen, 'dark gray', [
                     sz((leftOct * 245) - 175), HEIGHT - sz(60), sz(245), sz(30)], 0, sz(4))
    pygame.draw.rect(screen, 'black', [
                     sz((leftOct * 245) - 175), HEIGHT - sz(60), sz(245), sz(30)], sz(4), sz(4))
    text = small_font.render(leftHand[0], True, 'white')
    screen.blit(text, [sz((leftOct * 245) - 165), HEIGHT - sz(55)])
    text = small_font.render(leftHand[2], True, 'white')
    screen.blit(text, [sz((leftOct * 245) - 130), HEIGHT - sz(55)])
    text = small_font.render(leftHand[4], True, 'white')
    screen.blit(text, [sz((leftOct * 245) - 95), HEIGHT - sz(55)])
    text = small_font.render(leftHand[5], True, 'white')
    screen.blit(text, [sz((leftOct * 245) - 60), HEIGHT - sz(55)])
    text = small_font.render(leftHand[7], True, 'white')
    screen.blit(text, [sz((leftOct * 245) - 25), HEIGHT - sz(55)])
    text = small_font.render(leftHand[9], True, 'white')
    screen.blit(text, [sz((leftOct * 245) + 10), HEIGHT - sz(55)])
    text = small_font.render(leftHand[11], True, 'white')
    screen.blit(text, [sz((leftOct * 245) + 45), HEIGHT - sz(55)])
    text = small_font.render(leftHand[1], True, 'black')
    screen.blit(text, [sz((leftOct * 245) - 148), HEIGHT - sz(55)])
    text = small_font.render(leftHand[3], True, 'black')
    screen.blit(text, [sz((leftOct * 245) - 113), HEIGHT - sz(55)])
    text = small_font.render(leftHand[6], True, 'black')
    screen.blit(text, [sz((leftOct * 245) - 43), HEIGHT - sz(55)])
    text = small_font.render(leftHand[8], True, 'black')
    screen.blit(text, [sz((leftOct * 245) - 8), HEIGHT - sz(55)])
    text = small_font.render(leftHand[10], True, 'black')
    screen.blit(text, [sz((leftOct * 245) + 27), HEIGHT - sz(55)])
    # right hand
    pygame.draw.rect(screen, 'dark gray', [
                     sz((rightOct * 245) - 175), HEIGHT - sz(60), sz(245), sz(30)], 0, sz(4))
    pygame.draw.rect(screen, 'black', [
                     sz((rightOct * 245) - 175), HEIGHT - sz(60), sz(245), sz(30)], sz(4), sz(4))
    text = small_font.render(rightHand[0], True, 'white')
    screen.blit(text, [sz((rightOct * 245) - 165), HEIGHT - sz(55)])
    text = small_font.render(rightHand[2], True, 'white')
    screen.blit(text, [sz((rightOct * 245) - 130), HEIGHT - sz(55)])
    text = small_font.render(rightHand[4], True, 'white')
    screen.blit(text, [sz((rightOct * 245) - 95), HEIGHT - sz(55)])
    text = small_font.render(rightHand[5], True, 'white')
    screen.blit(text, [sz((rightOct * 245) - 60), HEIGHT - sz(55)])
    text = small_font.render(rightHand[7], True, 'white')
    screen.blit(text, [sz((rightOct * 245) - 25), HEIGHT - sz(55)])
    text = small_font.render(rightHand[9], True, 'white')
    screen.blit(text, [sz((rightOct * 245) + 10), HEIGHT - sz(55)])
    text = small_font.render(rightHand[11], True, 'white')
    screen.blit(text, [sz((rightOct * 245) + 45), HEIGHT - sz(55)])
    text = small_font.render(rightHand[1], True, 'black')
    screen.blit(text, [sz((rightOct * 245) - 148), HEIGHT - sz(55)])
    text = small_font.render(rightHand[3], True, 'black')
    screen.blit(text, [sz((rightOct * 245) - 113), HEIGHT - sz(55)])
    text = small_font.render(rightHand[6], True, 'black')
    screen.blit(text, [sz((rightOct * 245) - 43), HEIGHT - sz(55)])
    text = small_font.render(rightHand[8], True, 'black')
    screen.blit(text, [sz((rightOct * 245) - 8), HEIGHT - sz(55)])
    text = small_font.render(rightHand[10], True, 'black')
    screen.blit(text, [sz((rightOct * 245) + 27), HEIGHT - sz(55)])


def draw_title_bar():
    instruction_text = medium_font.render(
        'Up/Down Arrows Change Left Hand', True, 'black')
    screen.blit(instruction_text, [WIDTH - sz(500), sz(10)])
    instruction_text2 = medium_font.render(
        'Left/Right Arrows Change Right Hand', True, 'black')
    screen.blit(instruction_text2, [WIDTH - sz(500), sz(50)])
    # img = pygame.transform.scale(
    #     pygame.image.load('assets/logo.png'), [150, 150])
    # screen.blit(img, (-20, -30))
    # title_text = font.render('Python Programmable Piano!', True, 'white')
    # screen.blit(title_text, (298, 18))
    # title_text = font.render('Python Programmable Piano!', True, 'black')
    # screen.blit(title_text, (300, 20))


run = True
is_mouse_down = False
is_sustain = False
mouse_black_index = None
mouse_white_index = None


def resume_cnt_for_mouse():
    global mouse_black_index, mouse_white_index
    if mouse_black_index is not None:
        cnt_active_blacks[mouse_black_index] -= 1
        mouse_black_index = None
    if mouse_white_index is not None:
        cnt_active_whites[mouse_white_index] -= 1
        mouse_white_index = None


def try_play_black(index: int, is_mouse=False):
    global mouse_black_index
    if cnt_active_blacks[index] == 0:
        black_sounds[index].play(0, 0 if is_sustain else 1000)
    if is_mouse:
        resume_cnt_for_mouse()
        mouse_black_index = index
    cnt_active_blacks[index] += 1


def try_play_white(index: int, is_mouse=False):
    global mouse_white_index
    if cnt_active_whites[index] == 0:
        white_sounds[index].play(0, 0 if is_sustain else 1000)
    if is_mouse:
        resume_cnt_for_mouse()
        mouse_white_index = index
    cnt_active_whites[index] += 1


audio = Audio()
fft = FFT()

while run:
    left_dict = {
        'Z': f'C{left_oct}',
        'S': f'C#{left_oct}',
        'X': f'D{left_oct}',
        'D': f'D#{left_oct}',
        'C': f'E{left_oct}',
        'V': f'F{left_oct}',
        'G': f'F#{left_oct}',
        'B': f'G{left_oct}',
        'H': f'G#{left_oct}',
        'N': f'A{left_oct}',
        'J': f'A#{left_oct}',
        'M': f'B{left_oct}',
    }
    right_dict = {
        'R': f'C{right_oct}',
        '5': f'C#{right_oct}',
        'T': f'D{right_oct}',
        '6': f'D#{right_oct}',
        'Y': f'E{right_oct}',
        'U': f'F{right_oct}',
        '8': f'F#{right_oct}',
        'I': f'G{right_oct}',
        '9': f'G#{right_oct}',
        'O': f'A{right_oct}',
        '0': f'A#{right_oct}',
        'P': f'B{right_oct}'
    }

    timer.tick(fps)
    screen.fill('gray')
    # for i in range(0, WIDTH//100):
    #     for j in range(0, HEIGHT//100):
    #         pygame.draw.rect(screen, ['black', 'white']
    #                          [(i+j) % 2], [i*100, j*100, 100, 100])
    if not debug:
        white_keys, black_keys = draw_piano()

        def click_key(event: pygame.event.Event):
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

        draw_hands(right_oct, left_oct, right_hand, left_hand)
        draw_title_bar()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print('mouse down')
            is_mouse_down = True
            click_key(event)
        if event.type == pygame.MOUSEBUTTONUP:
            print('mouse up')
            is_mouse_down = False
            resume_cnt_for_mouse()
        if event.type == pygame.MOUSEMOTION:
            if is_mouse_down:
                click_key(event)
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key).upper()
            if key_name in left_dict:
                if left_dict[key_name][1] == '#':
                    index = black_labels.index(left_dict[key_name])
                    try_play_black(index)
                else:
                    index = white_notes.index(left_dict[key_name])
                    try_play_white(index)
            elif key_name in right_dict:
                if right_dict[key_name][1] == '#':
                    index = black_labels.index(right_dict[key_name])
                    try_play_black(index)
                else:
                    index = white_notes.index(right_dict[key_name])
                    try_play_white(index)
            elif event.key == pygame.K_RIGHT and right_oct < 8:
                right_oct += 1
            elif event.key == pygame.K_LEFT and right_oct > 0:
                right_oct -= 1
            elif event.key == pygame.K_UP and left_oct < 8:
                left_oct += 1
            elif event.key == pygame.K_DOWN and left_oct > 0:
                left_oct -= 1

        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key).upper()
            if key_name in left_dict:
                if left_dict[key_name][1] == '#':
                    index = black_labels.index(left_dict[key_name])
                    cnt_active_blacks[index] -= 1
                else:
                    index = white_notes.index(left_dict[key_name])
                    cnt_active_whites[index] -= 1
            elif key_name in right_dict:
                if right_dict[key_name][1] == '#':
                    index = black_labels.index(right_dict[key_name])
                    cnt_active_blacks[index] -= 1
                else:
                    index = white_notes.index(right_dict[key_name])
                    cnt_active_whites[index] -= 1
            elif event.key == pygame.K_F1:
                filename = prompt.open_file()
                try:
                    audio.read(filename, fft.process)
                except Exception as e:
                    prompt.info(str(e))
            elif event.key == pygame.K_F2:
                audio.record(fft.process)

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = screen.get_size()
            print(f'resize: {WIDTH=}, {HEIGHT=}')

    # print(len(fft.frames))
    # if len(fft.frames) > 100000:
    #     plt.plot(fft.frames)
    #     plt.show()
    #     fft.frames = []

    fft.plot(screen)

    pygame.display.flip()

pygame.quit()
audio.close()
