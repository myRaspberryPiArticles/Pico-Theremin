import time
from machine import Pin, I2C, PWM
from vl53l0x import VL53L0X

# 1. Wake up the sensor (XSHUT must be HIGH)
xshut = Pin(14, Pin.OUT)  # or 15 or 14
xshut.value(1)
time.sleep_ms(200)

xshut1 = Pin(15, Pin.OUT)  # or 15 or 14
xshut1.value(1)
time.sleep_ms(200)

time.sleep(2)

buzzer = PWM(Pin(5))

print("Setting up I2C")
sda = Pin(10) #or 10 or 8
scl = Pin(11) #or 11 or 9

sda1 = Pin(8) #or 10 or 8
scl1 = Pin(9) #or 11 or 9
# Explicit frequency prevents init handshake failures
# Lower frequency to 100kHz to prevent clock-stretching EIO errors
i2c1 = I2C(id=1, sda=sda, scl=scl, freq=100000) #or id 1 for 10/11 or id 0 for8/9
i2c0 = I2C(id=0, sda=sda1, scl=scl1, freq=100000)
print("I2C Scan:", i2c1.scan())  # Should return [41]
print("I2C Scan:", i2c0.scan())

print("Creating VL53L0X object...")
tof = VL53L0X(i2c1)
tof1 = VL53L0X(i2c0)

budget = tof.measurement_timing_budget_us
print("Budget was:", budget)
tof.set_measurement_timing_budget(100000)

budget1 = tof1.measurement_timing_budget_us
print("Budget was:", budget1)
tof1.set_measurement_timing_budget(100000)

# VCSEL pulse periods
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

tof1.set_Vcsel_pulse_period(tof1.vcsel_period_type[0], 18)
tof1.set_Vcsel_pulse_period(tof1.vcsel_period_type[1], 14)


def play_tone(frequency, duration):
    """Plays a specific frequency for a set duration in seconds"""
    buzzer.freq(frequency)
    # 32768 is a 50% duty cycle, which gives max volume for a passive buzzer
    buzzer.duty_u16((avgToF1 * 10)) 
    time.sleep(duration)

n = 20
reading_group = []

n1 = 20
reading_group1 = []

# Initialize the average variables before the loop so they always exist
avg = 0.0
avg1 = 0.0

print("Starting measurements")

# Initialize your variables so they always exist at startup
avg = 0.0
avg1 = 0.0
avgToF = 0
avgToF1 = 0

print("Starting measurements...")

while True:
    try:
        new_value = tof.ping() - 50
        new_value1 = tof1.ping() - 75
        
        # Filter out error codes for Sensor 1 (Pitch)
        if new_value not in (8140, 8141):
            reading_group.append(new_value)
            if len(reading_group) > n:
                reading_group.pop(0)
            avg = sum(reading_group) / len(reading_group)
            avgToF = int(avg)
            
        # Filter out error codes for Sensor 2 (Volume)
        if new_value1 not in (8140, 8141):
            reading_group1.append(new_value1)
            if len(reading_group1) > n1:
                reading_group1.pop(0)
            avg1 = sum(reading_group1) / len(reading_group1)
            avgToF1 = int(avg1)
            
        # =========================================================
        # PITCH AND VOLUME CONTROL (Right next to each other!)
        # =========================================================
        
        # 1. Set Tone Pitch (Sensor 1)
        pitch = avgToF * 10
        if pitch < 20: pitch = 20  # Keep it above human hearing minimum
        buzzer.freq(pitch)
        
        # 2. Set Volume (Sensor 2)
        volume = avgToF1 * 40      # Simple multiplier just like the tone!
        if volume > 32768:         # Cap it at 32768 (50% duty cycle) for max volume
            volume = 32768         # This prevents the audio from cutting out or crashing
            
        buzzer.duty_u16(volume)
        # =========================================================
        
        print(f"Avg 1 (Pitch): {avg:.1f} mm  |  Avg 2 (Vol): {avg1:.1f} mm")
        
    except OSError as e:
        print(f"I2C Read Error: {e}")
        buzzer.duty_u16(0) # Mute on error
        
    time.sleep(0.01)

