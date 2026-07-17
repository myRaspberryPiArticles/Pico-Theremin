import time
import math
from machine import Pin, I2C, SoftI2C, PWM
import ssd1306
from vl53l0x import VL53L0X

# =========================================================
# STEP 1: INITIALIZE HARDWARE (Pins & Audio)
# =========================================================
# Power up the sensors via XSHUT pins
Pin(15, Pin.OUT).value(1)
Pin(14, Pin.OUT).value(1)
time.sleep(0.2) 

# Audio Setup
buzzer = PWM(Pin(5))
led = Pin("LED", Pin.OUT)
led.value(1)

# =========================================================
# STEP 2: INITIALIZE I2C BUSES (No overlapping hardware blocks)
# =========================================================
# Bus 1 (Pins 10/11) - Pitch Sensor (Hardware I2C)
i2c1 = I2C(1, sda=Pin(10), scl=Pin(11), freq=400000)

# Bus 0 (Pins 8/9) - Volume Sensor (Hardware I2C)
i2c0 = I2C(0, sda=Pin(8),  scl=Pin(9),  freq=400000)

# Pins 2/3 - OLED Display (Using SoftI2C to avoid hijacking Hardware I2C 1)
i2c_oled = SoftI2C(sda=Pin(2), scl=Pin(3), freq=400000)

print("Bus 1 Scan (Pitch):", i2c1.scan()) 
print("Bus 0 Scan (Volume):", i2c0.scan()) 
print("OLED Bus Scan:", i2c_oled.scan())

# Initialize ToF Sensors
tof_pitch = VL53L0X(i2c1, address=41)  
tof_vol   = VL53L0X(i2c0, address=41)  

# Initialize OLED (128x32 screen size)
oled = ssd1306.SSD1306_I2C(128, 32, i2c_oled)

# =========================================================
# STEP 3: SETUP VARIABLES & FILTERS
# =========================================================
tof_pitch.set_measurement_timing_budget(40000)
tof_vol.set_measurement_timing_budget(40000)

n = 15
pitch_group = []
vol_group = []
avg_pitch = 0
avg_vol = 0

# Place this in STEP 3 of your script
smoothed_vol_duty = 0.0  # Tracks the actual current volume for smooth gliding

# Oscilloscope Animation variables (Adjusted for 32px height)
phase_shift = 0
center_y = 16  # Changed from 32 to 16 so the wave sits perfectly in the middle

print("🎛️ Theremin + Oscilloscope Active!")

# =========================================================
# STEP 4: THE UNIFIED, NON-BLOCKING LOOP
# =========================================================

while True:
    try:
        # --- 1. READ SENSORS ---
        raw_pitch = tof_pitch.ping() - 50
        raw_vol = tof_vol.ping() - 75
        
        # --- 2. FILTER DATA ---
        if raw_pitch not in (8140, 8141) and raw_pitch > 0:
            pitch_group.append(raw_pitch)
            if len(pitch_group) > n: pitch_group.pop(0)
            avg_pitch = int(sum(pitch_group) / len(pitch_group))
            
        if raw_vol not in (8140, 8141) and raw_vol > 0:
            vol_group.append(raw_vol)
            if len(vol_group) > n: vol_group.pop(0)
            avg_vol = int(sum(vol_group) / len(vol_group))
            
        # --- 3. AUDIO MAPPING & EXECUTION ---
        # A. Map pitch (Distance -> Frequency)
        pitch_freq = 100 + int(avg_pitch * 1.5)
        pitch_freq = max(40, min(pitch_freq, 1000)) 
        buzzer.freq(pitch_freq)
        
        # B. Map volume using a quadratic curve (avoids sudden quiet-to-loud jumps)
        # Normalize distance to a 0.0 - 1.0 scale (assuming max comfortable distance ~400mm)
        norm_vol = min(max(avg_vol / 400.0, 0.0), 1.0)
        
        # Squaring it (norm_vol * norm_vol) creates a smooth exponential curve for your ear
        target_volume_duty = int((norm_vol ** 2) * 32768) 
        
        # C. Apply the Glide Filter (Exponential Moving Average)
        # 0.10 means the volume moves 10% closer to your hand's position every single frame.
        # Lower = smoother/slacker glide. Higher (e.g., 0.25) = faster/snappier response.
        smoothing_factor = 0.10 
        smoothed_vol_duty += (target_volume_duty - smoothed_vol_duty) * smoothing_factor
        
        # Send the final smoothed value to the hardware
        buzzer.duty_u16(int(smoothed_vol_duty))
        
        # --- 4. VISUAL MAPPING (DYNAMIC OSCILLOSCOPE) ---
        wave_frequency = 0.05 + (1.0 / (avg_pitch + 1)) * 20 
        wave_frequency = max(0.05, min(wave_frequency, 0.4))

        # Scale down max amplitude to 12 pixels so it doesn't clip off the 32px screen bounds
        # Map Volume to Wave Amplitude using the newly smoothed volume duty cycle
        wave_amplitude = int((smoothed_vol_duty / 32768) * 12)        
        # --- 5. RENDER OLED FRAME ---
        oled.fill(0) 
        
        # Plot and draw the wave
        last_x = 0
        last_y = int(center_y + math.sin((last_x * wave_frequency) + phase_shift) * wave_amplitude)
        
        for x in range(1, 128):
            y = int(center_y + math.sin((x * wave_frequency) + phase_shift) * wave_amplitude)
            oled.line(last_x, last_y, x, y, 1) 
            last_x = x
            last_y = y
            
        oled.show() 
        phase_shift -= 0.25
        
    except OSError as e:
        print(f"I2C Bus Glitch Caught: {e}")
        oled.text("ERROR with I2C", 0, 16)
        buzzer.duty_u16(0)
        
    time.sleep_ms(2)
