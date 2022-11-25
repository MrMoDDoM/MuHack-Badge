import sys
from time import sleep_ms
from machine import I2C, Pin, PWM, UART
from buzzer_music.buzzer_music import music
import binascii
import neopixel
import _thread
import gc
#import micropython
import random
import select
from BHY.bhy import BHY
from CLED.cled import CLED

BOSS_Version = "1.0_beta"

applications = []

ESP_TX_PIN = 0
ESP_RX_PIN = 1

LED_LETTER_PIN = 18
LED_LETTER_LEN = 2

LED_STRIPE_PIN = 19
LED_STRIPE_LEN = 12

BUZZER_PIN = 29

BUTTON_A_PIN = 25
BUTTON_B_PIN = 24

SCL_PIN = 23
SDA_PIN = 22
BHY_I2C_ADDR = 0x28 # 40 in decimal

CLED_THREAD = 0

button_A = machine.Pin(BUTTON_A_PIN, Pin.IN)
button_B = machine.Pin(BUTTON_B_PIN, Pin.IN)

bhy = BHY(sda=SDA_PIN, scl=SCL_PIN, address=BHY_I2C_ADDR, stand_alone=False, debug=False)
cled = CLED(LED_STRIPE_PIN, LED_STRIPE_LEN, LED_LETTER_PIN, LED_LETTER_LEN, debug=False)

song = '0 E3 1 0;2 E4 1 0;4 E3 1 0;6 E4 1 0;8 E3 1 0;10 E4 1 0;12 E3 1 0;14 E4 1 0;16 A3 1 0;18 A4 1 0;20 A3 1 0;22 A4 1 0;24 A3 1 0;26 A4 1 0;28 A3 1 0;30 A4 1 0;32 G#3 1 0;34 G#4 1 0;36 G#3 1 0;38 G#4 1 0;40 E3 1 0;42 E4 1 0;44 E3 1 0;46 E4 1 0;48 A3 1 0;50 A4 1 0;52 A3 1 0;54 A4 1 0;56 A3 1 0;58 B3 1 0;60 C4 1 0;62 D4 1 0;64 D3 1 0;66 D4 1 0;68 D3 1 0;70 D4 1 0;72 D3 1 0;74 D4 1 0;76 D3 1 0;78 D4 1 0;80 C3 1 0;82 C4 1 0;84 C3 1 0;86 C4 1 0;88 C3 1 0;90 C4 1 0;92 C3 1 0;94 C4 1 0;96 G2 1 0;98 G3 1 0;100 G2 1 0;102 G3 1 0;104 E3 1 0;106 E4 1 0;108 E3 1 0;110 E4 1 0;114 A4 1 0;112 A3 1 0;116 A3 1 0;118 A4 1 0;120 A3 1 0;122 A4 1 0;124 A3 1 0;0 E6 1 1;4 B5 1 1;6 C6 1 1;8 D6 1 1;10 E6 1 1;11 D6 1 1;12 C6 1 1;14 B5 1 1;0 E5 1 6;4 B4 1 6;6 C5 1 6;8 D5 1 6;10 E5 1 6;11 D5 1 6;12 C5 1 6;14 B4 1 6;16 A5 1 1;20 A5 1 1;22 C6 1 1;24 E6 1 1;28 D6 1 1;30 C6 1 1;32 B5 1 1;36 B5 1 1;36 B5 1 1;37 B5 1 1;38 C6 1 1;40 D6 1 1;44 E6 1 1;48 C6 1 1;52 A5 1 1;56 A5 1 1;20 A4 1 6;16 A4 1 6;22 C5 1 6;24 E5 1 6;28 D5 1 6;30 C5 1 6;32 B4 1 6;36 B4 1 6;37 B4 1 6;38 C5 1 6;40 D5 1 6;44 E5 1 6;48 C5 1 6;52 A4 1 6;56 A4 1 6;64 D5 1 6;64 D6 1 1;68 D6 1 1;70 F6 1 1;72 A6 1 1;76 G6 1 1;78 F6 1 1;80 E6 1 1;84 E6 1 1;86 C6 1 1;88 E6 1 1;92 D6 1 1;94 C6 1 1;96 B5 1 1;100 B5 1 1;101 B5 1 1;102 C6 1 1;104 D6 1 1;108 E6 1 1;112 C6 1 1;116 A5 1 1;120 A5 1 1;72 A5 1 6;80 E5 1 6;68 D5 1 7;70 F5 1 7;76 G5 1 7;84 E5 1 7;78 F5 1 7;86 C5 1 7;88 E5 1 6;96 B4 1 6;104 D5 1 6;112 C5 1 6;120 A4 1 6;92 D5 1 7;94 C5 1 7;100 B4 1 7;101 B4 1 7;102 C5 1 7;108 E5 1 7;116 A4 1 7'
sensor_config = []
bhy_upload_try = 3
one_shot_re_enable = [BHY.VS_TYPE_WAKEUP,
                      BHY.VS_TYPE_WAKEUP + BHY.BHY_SID_WAKEUP_OFFSET,
                      BHY.VS_TYPE_GLANCE,
                      BHY.VS_TYPE_GLANCE + BHY.BHY_SID_WAKEUP_OFFSET,
                      BHY.VS_TYPE_PICKUP,
                      BHY.VS_TYPE_PICKUP + BHY.BHY_SID_WAKEUP_OFFSET]

#   | X | Y | Z |
# Xs| 1 | 0 | 0 |
# Ys| 0 | -1| 0 |
# Zs| 0 | 0 | -1|

remapping_matrix = [0,1,0,1,0,0,0,0,-1] # P5 ?
#remapping_matrix = [1,0,0,0,-1,0,0,0,-1] # P7 ?

def testHardware():
    led_stripe = neopixel.NeoPixel(machine.Pin(LED_STRIPE_PIN), LED_STRIPE_LEN)
    led_letter = neopixel.NeoPixel(machine.Pin(LED_LETTER_PIN), LED_LETTER_LEN)
    try:
        print("Testing LED Stripe")
        for j in range(255):
            for i in range(LED_STRIPE_LEN):
                rc_index = (i * 256 // LED_STRIPE_LEN) + j
                led_stripe[i] = cled.wheel(rc_index & 255)
            led_stripe.write()
            sleep_ms(10)

        print("Testing LED on Letters")
        for j in range(255):
            for i in range(LED_LETTER_LEN):
                rc_index = (i * 256 // LED_LETTER_LEN) + j
                led_letter[i] = cled.wheel(rc_index & 255)
            led_letter.write()
            sleep_ms(10)

        print("Testing A amb B buttons")
        while True:
            if button_A.value():
                led_letter[0] = (255,0,0)
            else:
                led_letter[0] = (0,0,0)

            if button_B.value():
                led_letter[1] = (255,0,0)
            else:
                led_letter[1] = (0,0,0)

            if not button_A.value() and not button_B.value():
                break

            led_letter.write()

        mySong = music(song, pins=[Pin(BUZZER_PIN)], looping=False)

        while mySong.tick():
            sleep_ms(40)

    except KeyboardInterrupt:
        print("##Hardware test aborted!##")
        return

    finally:
        led_stripe.fill( (0,0,0) )
        led_stripe.write()
        led_letter.fill( (0,0,0) )
        led_letter.write()

        # De-init the neopixel object
        del led_letter
        del led_stripe


def initBhy():
    print("Uploading firmware to BMI160")
    if not bhy.upload_BHI160B_RAM():
        print("Uploading FAILED!")
        return False

    print("Upload completed. Starging MainTask, waiting for the BMI160 to come up...")
    bhy.startMainTask()
    while not bhy.bhy_interrupt():
        pass

    sleep_ms(100)
    return True

def printSensorsList():
    my_list = []
    for i in range(1,33): # TODO: find a more reliable way to find how many sensor are available
        my_list.append(str(i) + ". " + bhy.sensorIdToName(i))

    for a,b in zip(my_list[::2],my_list[1::2]):
        print ('{:<40}{:<}'.format(a,b))

def printSensorsConfig():
    if not len(sensor_config):
        print("No sensor configured yet!\n")
    else:
        for i in range(len(sensor_config)):
            print("-"*20)
            s = sensor_config[i]
            print((str(i)+". "), end='')
            print("Sensor name:", bhy.sensorIdToName(s["sensor_id"]))
            print("\tWakeup:",s["wakeup_status"])
            print("\tSample rate:",s["sample_rate"])
            print("\tLatency ms:",s["max_report_latency_ms"])
            print("\tFlush FIFO:", end='')
            if s["flush_sensor"] == BHY.BHY_FIFO_FLUSH_ALL:
                print(" BHY_FIFO_FLUSH_ALL")
            else:
                print(" NONE")
            print("\tChange sensitivity:",s["change_sensitivity"])
            print("\tDynamic range:",s["dynamic_range"])
            print("-"*20)

    print('\n')

# Typical configuration is:
# Wakeup: FALSE
# Sample freq: 25 Hz
# Flush FIFO sensor: FALSE
# Max Report Latency: 0
# Change Sensitivity: 0
# Dynamic Range: 0

def addNewSensor():
    printSensorsList()
    id = int(input("Sensor ID: "))
    wake = input("Wakeup? [y/N]: ")
    sample = int(input("Sample rate [25]: ") or 25)
    latency = int(input("Max report latency [0]: ") or 0)
    flush_sensor = str(input("Flush Sensor data [-A-ll/-n-one]: ") or "A")
    change_sensitivity = int(input("Change Sensitivity [0]: ") or 0)
    dynamic_range = int(input("Dynamic Range [0]: ") or 0)

    if wake == 'y' or wake == 'Y':
        wake = True
    else:
        wake = False

    if flush_sensor == 'a' or flush_sensor == 'A':
        flush_sensor = BHY.BHY_FIFO_FLUSH_ALL
    else:
        flush_sensor = 0

    sensor_config.append({"sensor_id": id,
                          "wakeup_status": wake,
                          "sample_rate":sample,
                          "max_report_latency_ms": latency,
                          "flush_sensor": flush_sensor,
                          "change_sensitivity": change_sensitivity,
                          "dynamic_range": dynamic_range,
                          "to_remove": False})

    print("Sensor added!\n")

def removeSensor():
    printSensorsConfig()
    id = int(input("Sensor ID:"))
    if id >= len(sensor_config):
        print("Not a valid choice!")
    else:
        s = sensor_config[id]
        bhy.configVirtualSensor(s["sensor_id"], s["wakeup_status"], 0, 0, 0, 0, 0) # To disable a sensor, set sample reat at 0
        sensor_config.remove(s)
        print("Sensor Removed!\n")

def sensorsMenu():
    fin = False
    while not fin:
        print("### Sensors Menu ###")
        print("1. Print current configuration")
        print("2. Add a new sensor")
        print("3. Remove a sensor")
        print("4. Scan Physical Sensors")
        print("5. Calibrate Sensors")
        print("\n99. Return main menu")

        sel = input("\n> ")
        if sel == "1":
            printSensorsConfig()
        elif sel == "2":
            addNewSensor()
        elif sel == "3":
            removeSensor()
        elif sel == "4":
            scanPhysicalSensor()
        elif sel == "5":
            calibrationProccess()
        elif sel == "99":
            fin = True
        else:
          print("Bad selection!\n")

def scanPhysicalSensor():
    for i in range(33,96):
        data = bhy.readParameterPage(bhy.BHY_SYSTEM_PAGE, i, 16)
        if data:
            print("-"*20)
            print(binascii.hexlify(data))
            print("-"*20)

# TODO: Fix this function and add physical sensor query procedure
def discoverSelfTest():
    bhy.requestSelfTest()
    # Wait for interrupt
    while not bhy.bhy_interrupt():
        pass

    buffer = bhy.readFIFO()

    #print(binascii.hexlify(buffer))

    # print("Event type:", info,
    #     "\tEvent ID:", buffer[0],
    #     "\tData:", binascii.hexlify(buffer[:dim])
    #     )

    # events = bhy.parse_fifo(buffer, [BHY.EV_META_EVENTS, BHY.EV_WAKEUP_META_EVENTS])
    # for e in events:
    #     print(bhy.parseMetaEvent(e[2]))

def streamCalibration(vs_type):
    calibrated = False
    calibration_level = -1
    try:
        while not calibrated:
            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, raw=True) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if e[0] == vs_type:
                    actual_level = bhy.parseVectorPlus(e[2])["accuracy"]
                    if actual_level > calibration_level:
                        calibration_level = actual_level
                        cled.drawLevel(actual_level, 3)
                        print("Level of calibration:", calibration_level)

            if calibration_level == 3:
                calibrated = True
                cled.blinkAll((255,255,255), 50, 2)
                print("Calibrated!")

        return True

    except KeyboardInterrupt:
        print("User Interrupt! Ending streaming!")
        return False

def setRemappingMatrix():
    print("Current Accelerometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER))
    bhy.setRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER, remapping_matrix)
    print("New Accelerometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER))
    print("Current Megnetometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED))
    bhy.setRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED, remapping_matrix)
    print("New Megnetometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED))
    print("Current Gyroscope map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED))
    bhy.setRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED, remapping_matrix)
    print("New Gyroscope map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED))

def calibrationProccess():
    bhy.calibrated = False

    print("##This procedure will follow you to calibrate the BHI160B sensors##")
    print("\nFirst we set the remapping Matrix for the MuHack Badge pcb...")
    setRemappingMatrix()
    print("\nThen, starting from the gyroscope, lay the pcb on a flat surface:")

    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GYROSCOPE,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    if not streamCalibration(BHY.VS_TYPE_GYROSCOPE):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Gyroscope
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GYROSCOPE,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    print("Now the Accelerometer: rotate the board with 45° step in one direction")

    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_ACCELEROMETER,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    if not streamCalibration(BHY.VS_TYPE_ACCELEROMETER):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Accelerometer
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_ACCELEROMETER,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    print("And last, the Magnetometer: draw an 8-figure in mid-air with the board")
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GEOMAGNETIC_FIELD,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    if not streamCalibration(BHY.VS_TYPE_GEOMAGNETIC_FIELD):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Magnetometer
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GEOMAGNETIC_FIELD,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    print("\n##Calibration completed!##\n")
    bhy.calibrated = True
    cled.clear()
    cled.np.write()

def compass():
    # Activate orientation sensor
    sensor = {"sensor_id": BHY.VS_TYPE_ORIENTATION,
              "wakeup_status": False,
              "sample_rate": 25,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    startCLED()

    try:
        while True:
            if (not button_B.value()):
                break
            gc.collect()

            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, False) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if e[0] == BHY.VS_TYPE_ORIENTATION or e[0] == (BHY.VS_TYPE_ORIENTATION + BHY.BHY_SID_WAKEUP_OFFSET):
                    north = 360 - e[2]['x'] # Lock in place the rotation 
                    cled.addAnimation("drawArrow", north)
    except:
        raise
    finally:
        stopCLED()
        # Disable orientation sensor
        sensor["sample_rate"] = 0
        bhy.configVirtualSensorWithConfig(sensor)

def streamFifo():
    showAll = input("Show all event? [False] ")
    raw = input("Show raw data? [False] ")
    if raw == 'y' or raw == 'Y':
        raw = True
    else:
        raw = False

    filter = []
    for s in sensor_config:
        ret = bhy.configVirtualSensorWithConfig(s)
        filter.append(s["sensor_id"]) # Add this sensor to the filter

    # For good measure, flush old data
    bhy.flushFifo() # TODO: THIS DONT WORKS AS EXPECTED

    startCLED()

    try:
        while True:
            gc.collect()

            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, raw) # Dont pass the filters if we want to show everythings
            if showAll:
                print(events)

            for e in events: # Loop every events read
                if e[0] in one_shot_re_enable:
                    # Search the current config and re-enable it
                    for c in sensor_config:
                        if c["sensor_id"] == e[0]:
                            ret = bhy.configVirtualSensorWithConfig(c) # Re-enable one-shot sensor # TODO: add proper check
                    # c = next((conf for conf in sensor_config if conf["sensor_id"] == e[0]))
                    # print(bhy.parseActivityRecognitionData(e[2])) # THIS IS NOT CORRECT EVEN IF THE DATA IS LISTED AS AN EVENT

                if e[0] == BHY.VS_TYPE_WAKEUP or e[0] == (BHY.VS_TYPE_WAKEUP + BHY.BHY_SID_WAKEUP_OFFSET):
                    #_thread.start_new_thread(cled.run, ("goesRound", [(0,255,0), 10]))
                    cled.addAnimation("blinkAll", [(255,255,0), 50, 2])
                elif e[0] == BHY.VS_TYPE_PICKUP or e[0] == (BHY.VS_TYPE_PICKUP + BHY.BHY_SID_WAKEUP_OFFSET):
                    cled.addAnimation("goesRound", [(0,255,0), 50])
                elif e[0] == BHY.VS_TYPE_ORIENTATION or e[0] == (BHY.VS_TYPE_ORIENTATION + BHY.BHY_SID_WAKEUP_OFFSET):
                    north = 360 - e[2]['x']
                    cled.addAnimation("drawArrow", north)
                elif e[0] == BHY.VS_TYPE_GEOMAGNETIC_FIELD or e[0] == (BHY.VS_TYPE_GEOMAGNETIC_FIELD + BHY.BHY_SID_WAKEUP_OFFSET):
                    print(e[2])

    except KeyboardInterrupt:
        print("User Interrupt! Ending streaming!")
    finally:
        stopCLED()

def startCLED():
    print("Starting CLED system.. hold on")
    if cled.is_running:
        print("CLED systeam already running! Simply add animation with addAnimation function")
    else:
        _thread.start_new_thread(cled.run, ())
        cled.is_running = True # TODO: Seems like the _thread.start_new_thread return None even if the thread had been started

def stopCLED():
    global CLED_THREAD
    if CLED_THREAD:
        cled.addAnimation("exit", [])
        cled.is_running = False
    else:
        print("CLED system is not running!")

def modeSelection(max_sel):
    sel = 0
    wheel = 0
    pressed = False
    while True:
        if (not button_B.value()):
            break

        if (not button_A.value()) and (not pressed):
            pressed = True
            sel += 1
        elif button_A.value():
            pressed = False

        cled.np.fill((0,0,0))
        cled.np[sel % max_sel] = cled.wheel(wheel)
        cled.np.write()
        sleep_ms(100)
        wheel += 1
        wheel = wheel % 255

    print("Sel", sel)
    print("Sel modulus", sel%max_sel)

    return (sel % max_sel)

def headlessMain():
    sleep_ms(500)
    state = 0
    fin = False
    # First we try to configure the BHY
    for i in range(3):
        if not initBhy():
            print("Retring...")
        else:
            break

    while not fin:
        sel = modeSelection(len(applications)) # Let the user select the application with the LED circle
        print("Starting application number", sel)
        applications[sel]() # Actually call the function

def print_menu():
    print("1. Configure i2c and upload RAM patch to BHY")
    print("2. Print BHY Internal Informations")
    print("3. Hardware Test")
    print("4. Sensors Menu")
    print("\n5. Start streaming data")
    print("\n6. ESP32 UART passthrough")
    print("\n99. Drop out to REPL prompt")

uart_lock = _thread.allocate_lock()

def from_stdin_to_uart(uart, a):
    while True:
        uart.write(sys.stdin.read(1))

def UARTPassThrough():
    try:
        esp_uart = machine.UART(0, 115200, tx=Pin(ESP_TX_PIN), rx=Pin(ESP_RX_PIN))

        sys_uart_thread = _thread.start_new_thread(from_stdin_to_uart, (esp_uart,1))
        while True:
            if esp_uart.any(): # ESP has data to send us
                sys.stdout.write(esp_uart.read())
    except KeyboardInterrupt:
        print("User Interrupt! Ending UART passthrough!")

def main():
    printWelcome()
    fin = False

    gc.enable()

    while not fin:
        print_menu()
        sel = input("\n> ")
        if sel == "1":
            for i in range(bhy_upload_try):
                if not initBhy():
                    print("Retring...")
                else:
                    break

        elif sel == "2":
            bhy.dump_Chip_status()
        elif sel == "3":
            testHardware()
        elif sel == "4":
            sensorsMenu()
        elif sel == "5":
            streamFifo()
        elif sel == "6":
            UARTPassThrough()
        elif sel == "99":
            print("Bye Bye BOSS!")
            fin = True
        else:
            ("Bad selection!\n")

def startUpAnimation():
    startup_chime = "6 C6 1 8;0 C5 1 43;1 F5 1 8;2 A5 1 8;3 C6 1 8;5 A5 1 8"
    cled.fillFromBottom((0,255,0), 100)
    mySong = music(startup_chime, pins=[Pin(BUZZER_PIN)], looping=False)
    while mySong.tick():
        sleep_ms(40)

    sleep_ms(100)
    cled.clear()
    cled.np.write()

def printWelcome():
  welcomes = [
      '''
    ██████╗  ██████╗ ███████╗███████╗
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
    ██████╔╝██║   ██║███████╗███████╗
    ██╔══██╗██║   ██║╚════██║╚════██║
    ██████╔╝╚██████╔╝███████║███████║
    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
    ''',
      '''
    ▀█████████▄   ▄██████▄     ▄████████    ▄████████
      ███    ███ ███    ███   ███    ███   ███    ███
      ███    ███ ███    ███   ███    █▀    ███    █▀
     ▄███▄▄▄██▀  ███    ███   ███          ███
    ▀▀███▀▀▀██▄  ███    ███ ▀███████████ ▀███████████
      ███    ██▄ ███    ███          ███          ███
      ███    ███ ███    ███    ▄█    ███    ▄█    ███
    ▄█████████▀   ▀██████▀   ▄████████▀   ▄████████▀
    ''',
      '''
    ███████████     ███████     █████████   █████████
    ░░███░░░░░███  ███░░░░░███  ███░░░░░███ ███░░░░░███
    ░███    ░███ ███     ░░███░███    ░░░ ░███    ░░░
    ░██████████ ░███      ░███░░█████████ ░░█████████
    ░███░░░░░███░███      ░███ ░░░░░░░░███ ░░░░░░░░███
    ░███    ░███░░███     ███  ███    ░███ ███    ░███
    ███████████  ░░░███████░  ░░█████████ ░░█████████
    ░░░░░░░░░░░     ░░░░░░░     ░░░░░░░░░   ░░░░░░░░░
    ''',
      '''
    ▄▄▄▄·       .▄▄ · .▄▄ ·
    ▐█ ▀█▪▪     ▐█ ▀. ▐█ ▀.
    ▐█▀▀█▄ ▄█▀▄ ▄▀▀▀█▄▄▀▀▀█▄
    ██▄▪▐█▐█▌.▐▌▐█▄▪▐█▐█▄▪▐█
    ·▀▀▀▀  ▀█▄▀▪ ▀▀▀▀  ▀▀▀▀
    ''',
      '''
     ___  ___  ___ ___
    | _ )/ _ \/ __/ __|
    | _ \ (_) \__ \__ \\
    |___/\___/|___/___/
    ''',
      '''
    ███   ████▄    ▄▄▄▄▄    ▄▄▄▄▄
    █  █  █   █   █     ▀▄ █     ▀▄
    █ ▀ ▄ █   █ ▄  ▀▀▀▀▄ ▄  ▀▀▀▀▄
    █  ▄▀ ▀████  ▀▄▄▄▄▀   ▀▄▄▄▄▀
    ███
    ''',
      '''
    ▄▀▀█▄▄   ▄▀▀▀▀▄   ▄▀▀▀▀▄  ▄▀▀▀▀▄
    ▐ ▄▀   █ █      █ █ █   ▐ █ █   ▐
      █▄▄▄▀  █      █    ▀▄      ▀▄
      █   █  ▀▄    ▄▀ ▀▄   █  ▀▄   █
    ▄▀▄▄▄▀    ▀▀▀▀    █▀▀▀    █▀▀▀
    █    ▐             ▐       ▐
    ▐
    '''
  ]

  print(welcomes[random.randrange(len(welcomes) - 1)])
  print("Welcome to B.O.S.S. - Badge Operating Small System! Version: " + BOSS_Version + "\n")

if __name__ == "__main__":
    print("Starting...")
    SIE_STATUS=const(0x50110000+0x50)
    CONNECTED=const(1<<16)
    SUSPENDED=const(1<<4)
    try:
        gc.enable()
        startUpAnimation()
        cled.clear()
        cled.np.write()
        applications.append(calibrationProccess)
        applications.append(compass)
        # Check if we have a serial connection active
        if (machine.mem32[SIE_STATUS] & (CONNECTED | SUSPENDED))==CONNECTED and button_B.value():
            main()
        else: # If we dont, we start the headless mode
            headlessMain()

    except KeyboardInterrupt: # TODO: can't use it on micropython?
        print("\n\nKeyboard Interrupt catched! Use menu -99- to exit\n")
    except Exception as e:
        cled.np.fill((255,0,0))
        cled.np.write()
        print("#"*10 + "ERROR" + "#"*10)
        print("Got this error while running:")
        sys.print_exception(e)
        print("#"*25)

