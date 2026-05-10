import math
import struct
import random
import pygame


SAMPLE_RATE = 44100


def generate_sine_wave(frequency, duration, volume=0.3):
    num_samples = int(SAMPLE_RATE * duration)
    buf = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        envelope = 1.0 - (i / num_samples)
        sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * t))
        buf.append(sample)
    return buf


def generate_noise(duration, volume=0.3):
    num_samples = int(SAMPLE_RATE * duration)
    return [int(32767 * volume * (random.random() * 2 - 1)) for _ in range(num_samples)]


def generate_gunshot(freq=80):
    noise = generate_noise(0.08, 0.4)
    low = generate_sine_wave(freq, 0.05, 0.5)
    combined = []
    for i in range(max(len(noise), len(low))):
        n = noise[i] if i < len(noise) else 0
        l = low[i] if i < len(low) else 0
        combined.append(max(-32767, min(32767, n + l)))
    return array_to_sound(combined)


def generate_explosion():
    noise = generate_noise(0.3, 0.6)
    low = generate_sine_wave(40, 0.25, 0.5)
    combined = []
    total = max(len(noise), len(low))
    for i in range(total):
        n = noise[i] if i < len(noise) else 0
        l = low[i] if i < len(low) else 0
        decay = 1.0 - (i / total)
        combined.append(int(max(-32767, min(32767, (n + l) * decay))))
    return array_to_sound(combined)


def array_to_sound(samples):
    buf = struct.pack('<' + 'h' * len(samples), *samples)
    return pygame.mixer.Sound(buffer=buf)


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
        except Exception:
            pass
        self.sounds = {}
        self.sfx_volume = 0.9
        self.master_volume = 0.8
        self.enabled = True
        self.load_sounds()

    def load_sounds(self):
        try:
            self.sounds["pistol"] = generate_gunshot(80)
            self.sounds["smg"] = generate_gunshot(60)
            self.sounds["shotgun"] = generate_gunshot(50)
            self.sounds["rifle"] = generate_gunshot(100)
            self.sounds["sniper"] = generate_gunshot(30)
            self.sounds["rocket"] = generate_explosion()
            self.sounds["explosion"] = generate_explosion()
            click = generate_sine_wave(800, 0.05, 0.2)
            self.sounds["click"] = array_to_sound(click)
            hit = generate_sine_wave(400, 0.03, 0.3)
            self.sounds["hit"] = array_to_sound(hit)
        except Exception:
            self.enabled = False

    def play(self, name, volume_scale=1.0):
        if not self.enabled or name not in self.sounds:
            return
        try:
            s = self.sounds[name]
            s.set_volume(self.sfx_volume * self.master_volume * volume_scale)
            s.play()
        except Exception:
            pass

    def set_volumes(self, master, sfx):
        self.master_volume = master
        self.sfx_volume = sfx
