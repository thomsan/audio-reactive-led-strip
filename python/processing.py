import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import websocket_server

EFFECT_COLORED_ENERGY = "effect_colored_energy"
EFFECT_ENERGY = "effect_energy"
EFFECT_SCROLL = "effect_scroll"
EFFECT_SPECTRUM = "effect_spectrum"

def process(raw_fft_data, led_strip_client):
    if(led_strip_client.config.visualization_effect == EFFECT_COLORED_ENERGY):
        process_colored_energy(raw_fft_data, led_strip_client.config)
    #elif(led_strip_client.config.visualization_effect == EFFECT_ENERGY):
    #    process_energy(raw_fft_data, led_strip_client.config)
    #elif(led_strip_client.config.visualization_effect == EFFECT_SCROLL):
    #    process_scroll(raw_fft_data, led_strip_client.config)
    #elif(led_strip_client.config.visualization_effect == EFFECT_SPECTRUM):
    #    process_spectrum(raw_fft_data, led_strip_client.config)

    
def process_colored_energy(raw_fft_data, led_strip_client):
    led_strip_client.y = np.copy(raw_fft_data)
    led_strip_client.gain.update(led_strip_client.y)
    led_strip_client.y /= led_strip_client.gain.value
    # Scale by the width of the LED strip
    led_strip_client.y *= float((led_strip_client.config.num_leds // 2) - 1)
    # Map color channels according to set color and the energy over the whole freq bands
    scale = 0.9
    r = int(np.mean(led_strip_client.y**scale * int(led_strip_client.config.color["r"])/256))
    g = int(np.mean(led_strip_client.y**scale * int(led_strip_client.config.color["g"])/256))
    b = int(np.mean(led_strip_client.y**scale * int(led_strip_client.config.color["b"])/256))
    
    # Assign color to different frequency regions
    led_strip_client.p[0, :r] = 255.0
    led_strip_client.p[0, r:] = 0.0
    led_strip_client.p[1, :g] = 255.0
    led_strip_client.p[1, g:] = 0.0
    led_strip_client.p[2, :b] = 255.0
    led_strip_client.p[2, b:] = 0.0
    led_strip_client.p_filt.update(led_strip_client.p)
    led_strip_client.p = np.round(led_strip_client.p_filt.value)
    # Apply substantial blur to smooth the edges
    led_strip_client.p[0, :] = gaussian_filter1d(led_strip_client.p[0, :], sigma=float(led_strip_client.config.sigma))    
    led_strip_client.p[1, :] = gaussian_filter1d(led_strip_client.p[1, :], sigma=float(led_strip_client.config.sigma))
    led_strip_client.p[2, :] = gaussian_filter1d(led_strip_client.p[2, :], sigma=float(led_strip_client.config.sigma))
    # Set the new pixel value
    return np.concatenate((led_strip_client.p[:, ::-1], led_strip_client.p), axis=1)