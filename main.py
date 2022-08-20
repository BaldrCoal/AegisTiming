import configparser
import cv2
import numpy as np
import os
import pyautogui
import pyperclip
import keyboard
import sys

class TimerRecognizer:
    def __init__(self, path):
        self.threshold = 0.9
        self.templates = np.load(os.path.join(path, 'templates.npy'))

    def process(self, img, template_size, index):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template = cv2.resize(self.templates[index], (template_size[0], template_size[1]))
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.threshold)
        positions = list()
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            positions.append(pt[0])
        return positions

    def get_time(self, img):
        img = img[24: 37, 920: 1000]
        positions = list()
        for i in range(len(self.templates)):
            position = self.process(img, (7, 9), i)
            positions.extend([(pos, i) for pos in position])

        return tuple(i[1] for i in sorted(positions))


def give_timings():
    tr = TimerRecognizer('./ref/')
    scrn = pyautogui.screenshot()
    scrn = np.array(scrn)
    scrn = cv2.cvtColor(scrn, cv2.COLOR_RGB2BGR)
    time_rosh_down = tr.get_time(scrn)

    if time_rosh_down:
        minutes = int(''.join(map(str, time_rosh_down[0:-2:1])))
        seconds = int(''.join(map(str, time_rosh_down[-2:]))) + (minutes * 60)
        pyperclip.copy(
            f'{(seconds + 300) // 60}.{(seconds + 300) % 60:02}, '
            f'{(seconds + 480) // 60}.{(seconds + 480) % 60:02}, '
            f'{(seconds + 660) // 60}.{(seconds + 660) % 60:02}')
    else:
        pyperclip.copy('пусто')


config = configparser.ConfigParser()
config.read('config.ini')
activateKey = config['DEFAULT']['ActivateKey']
shutDownKey = config['DEFAULT']['ShutDownKey']
startDota = bool(config['DEFAULT']['StartDotaOnStartUp'])
if startDota:
    os.system('cmd /c start steam://rungameid/570')
keyboard.add_hotkey(activateKey, give_timings)

while True:
    keyboard.wait(shutDownKey)
    sys.exit()
