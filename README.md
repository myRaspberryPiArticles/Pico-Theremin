# Pico-Theremin
My version of a theremin, built with a Raspberry Pi Pico, buzzer and Time of Flight sensors! See the code, detailed description, parts list and things you will need to build it here!

## Pictures

## What it is

A theremin is a simple device that allows hand gestures and movements to be transmitted into sound, with different frequencies and volumes based on the movements. They usually have two metal rods that create an electromagnetic field to detect hand movements. 

My version of this is built with 2 Time of Flight sensors that get hand input, and a buzzer that outputs the sound. I also added a small OLED, which can display the sound wave it is producing, using some math implemented in the code. It changes the wave length and wave width on the screen to visualise the sound.

## How it works

The two sensors each detect two different distances the hand is, and they are used to become a buzzer’s frequency and amplitude. The code gives out a value in millimetres, anywhere from 5 to 600 - while the buzzer requires a sound of 36 - 1024 Hz. To make this achievable, we multiply the distance readings by 10 for the pitch. However, the buzzer duty cycle (volume) ranges anywhere from 0 (silent); 32768 (50%) and 65534 (loudest). To match the integer it requires, we multiply the volume reading by 40. The main processing chip is a Raspberry Pi Pico, and it is a small maker board for these types of projects. To control the volume of the buzzer, it has PWM GPIO pins, which stand for Pulse Width Modulation General Purpose Input/Output pins. They basically make the flow of electricity go on and off at different speeds to make the buzzer louder or quieter.

## Code

The code is split up into 2 codes, one that controls sensors, and one that is the main.py where the OLED is run. You do need to download the 'vl53l0x' library to get the sensors to work properly, and when wiring remember to put the sensors on DIFFERENT I2C BUSES. I found a small I2C scan code to be helpful when testing.

## Case design

I printed a simple bumper for my Theremin to keep the wiring on the bottom safe. I designed it in TinkerCAD, in a way that my protoboard it is built on can sit inside it. The STL files are above for you to download for yourelf!

## Parts List

| Part | Where to buy |
| :--- | :---: |
| Raspberry Pi Pico | [PiHut](https://thepihut.com/products/raspberry-pi-pico?variant=41925332566211) |
| x2 Time of Flight sensors | [Amazon](https://www.amazon.com/ALAMSCN-Breakout-VL53L0XV2-Distance-Measurement/dp/B08V8SKKZ4) |
| Passive buzzer (make sure it changes sound) | [Amazon](https://www.amazon.co.uk/sourcing-map-Passive-Electronic-Electromagnetic/dp/B08MDNL2DW/ref=sr_1_6?crid=1L5DSP92BLCCU&dib=eyJ2IjoiMSJ9.KnYuVLhYsOBbQpzhHd40r0vmiO1H1uCPrPelARdF_mAAAdzqh2rJxxdH_unTmfCktZwJacB87SYo3MATOUwBWVa-sl4sq_rqhS8fRsQJThAFZqUQ4zsnzQZF3BYpKb72AZNnIaduQ0Rd-2GabuvAAiOPvOnsFOZawR8EXr9STGbradUrp_HnkHoNWwzaR2p0VVvWDaD6b8brrTnPFqrHRvm5CMNss2sT4H6-itD_PmYmaDexlTUX7UZKjTT9r7Y-dHC9o1gebZHlGytmp15P4CZDdpJC1XEziWj4oHbEcgk.84gzMObtTIe8Sfq6XJ0Qngf9T8Zu25DvNdh7kwrBDGg&dib_tag=se&keywords=passive+buzzer&qid=1784305029&sprefix=passive+buzz%2Caps%2C151&sr=8-6) |
| 0.91" OLED | [Amazon](https://www.amazon.co.uk/DollaTek-Display-SSD1306-3-3V-5V-Arduino/dp/B07MHGPNVT/ref=sr_1_6?crid=URWJ7DWKSGGW&dib=eyJ2IjoiMSJ9.HCmeK5wbxzHTGP5CBhZz0IqapT47WvNwxKQszh7rR1-XqCjZqOxVAu3cN_JeVNUaCYnxNbscEOIypJjqK2xFZQvKJMky5hpBnEf2QyM-Ks5Ho1X0BWk9NSLyRbS5jrszOGcFQQ2QAvyz4HIuoMgpeZJNuzFY7NYNJ2Coo5RAlnBxaBDFmGdhgZ_AFscD4U2ucASlIZYHnYl-RF0YDmE8LoEPpa1vUG7N-g8mJ-1xrWCyanNdzgVv_LWpErzo-zvZbhjsPpbpaXsVm9TTX2pOZbUiWcO4u7ao4BCgwm7iLhs.ttbz9E7pcfJOc3Rh_9Zx6ahfeEh4PTHFW7um-OzkWgc&dib_tag=se&keywords=0.91+oled+i2c+display&qid=1784304998&sprefix=0.91%22%2Caps%2C232&sr=8-6) |
