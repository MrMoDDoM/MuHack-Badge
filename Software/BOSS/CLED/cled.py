import machine
import neopixel
import _thread
from time import sleep_ms
import gc

class CLED:

    animation_list = []
    animationLetter_list = []

    def __init__(self, led_pin=22, led_len=23, letter_pin = 18, letter_len = 2, debug = False):
        self.len = led_len
        self.lenLetter = letter_len
        self.np = neopixel.NeoPixel(machine.Pin(led_pin), led_len)
        self.np_letter = neopixel.NeoPixel(machine.Pin(letter_pin), letter_len)

        self.lock = _thread.allocate_lock()

        self.debug = debug
        self.last_led = 0 
        self.is_running = False

    def addAnimation(self, name, data):
        while not self.lock.acquire(0):
                    pass
        self.animation_list.append([name, data])
        self.lock.release()

    def addAnimationLetter(self, name, data):
        while not self.lock.acquire(0):
                    pass
        self.animation_list.append([name, data])
        self.lock.release()

    def run(self):

        while True:

            if len(self.animation_list):

                self.lock.acquire()

                nextAnimation = self.animation_list.pop()

                # Check the stop condition
                if nextAnimation[0] == "stopThread":
                    self.is_running = False
                    _thread.exit()

                # TODO: This is the rigth way, BUT IT IS TOO SLOW!
                # Decide what function to call
                # if nextAnimation[0] in dir(self):
                #     animation = getattr(self, nextAnimation[0])
                #     animation(nextAnimation[1])
                
                if nextAnimation[0] == "blinkAll":
                    self.blinkAll(nextAnimation[1][0], nextAnimation[1][1], nextAnimation[1][2] )
                elif nextAnimation[0] == "goesRound":
                    self.goesRound(nextAnimation[1][0], nextAnimation[1][1])
                elif nextAnimation[0] == "drawArrow":
                    self.drawArrow(nextAnimation[1])
                elif nextAnimation[0] == "drawLevel":
                    self.drawLevel(nextAnimation[1][0], nextAnimation[1][1])
                
                self.lock.release()
                gc.collect()

    def drawLevel(self, value, max):

        self.clear()
        top = (value*self.len)//max
        color = (255, 0, 0)

        if (value > max//3):
            color = (255, 255, 0)
        if (value > (max//3)*2):
            color = (0, 255, 0)

        for i in range(top):
            self.np[i] = color

        self.np.write()

    def goesRound(self, color, delay):
        for i in range(self.len):
            self.np[i] = color
            self.np.write()
            sleep_ms(delay)

        self.clear()

    def blinkAll(self, color, delay, blinks):
        for b in range(blinks):
            for i in range(self.len):
                self.np[i] = color
            
            self.np.write()
            sleep_ms(delay)
            self.clear()

    def drawArrow(self, grade):
        half_number_leds=self.len//2

        index = int((grade/361) * self.len)
        resto = grade - (360/self.len) * index
        delta_rgb = (255 * 2) / self.len
        fix = (resto * self.len * delta_rgb)/360

        # initialize array
        led_color=[]
        for i in range(self.len):
            led_color.append((0,0,0))

        led_color[index]= (255-fix,0,fix)

        if(self.len%2==0):
            led_color[(index+half_number_leds) % self.len]= (fix,0,255-fix)

        for i in range(half_number_leds-1):
            if i==0:
                (r,g,b)= led_color[(index+i)%self.len]
                led_color[(index+(i+1))%self.len] = (r-delta_rgb+2*fix,g,b+delta_rgb-2*fix)
            else:
                (r,g,b)= led_color[(index+i)%self.len]
                led_color[(index+(i+1))%self.len] = (r-delta_rgb,g,b+delta_rgb)

            (r1,g1,b1)= led_color[(index-i)%self.len]
            led_color[(index-(i+1))%self.len] = (r1-delta_rgb,g1,b1+delta_rgb)

        for i in range(self.len):
            (r,g,b)= led_color[i]
            self.np[i]= (int(r),int(g),int(b))

        self.np.write()
    
    # def drawArrow(self, data):
    #     # self.len=12 
    #     delta_grad = 360/self.len
    #     half_leds=self.len/2
    #     led_color=[]
    #     for i in range(self.len):
    #         red=(255*(i/half_leds))
    #         if i > half_leds:
    #             red=255*((self.len-i)/half_leds)

    #         blue=255-red
    #         led_color.append((int(red),0,int(blue)))

    #     # shift colors to the standar position aka red on sector 0 blue on sector 6 
    #     led_color = led_color[-6:] + led_color[:-6]
    #     # compute correct sector to put red
    #     position = int(data[1]//delta_grad)
    #     #update position
    #     led_color = led_color[-position:] + led_color[:-position]

    #     for i in range(self.len):
    #         self.np[i] = led_color[i]

    #     self.np.write()
        # return led_color
    
    # def drawArrow(self, data):
    #     color = 255
    #     #led = int((data[1]*12)//361) # Remap 360 on the 12 led - 361 to avoid off by one on led
    #     #led = 11 - led # The poin must 
    #     # if led != self.last_led:
    #     #     print(led)
    #     #     self.last_led = led
        
    #     for i in range(self.len):
    #         angle = (i+1) * 30
    #         delta = abs(data[1] - angle)
    #         if delta > 180:
    #             delta = -delta % 180
    #         color = (delta * 255) // 90
    #         if color > 255:
    #             color = 255
            
    #         self.np[i] = (int(color),0,0) #self.wheelRB(int(color))

    #     self.np.write()
    #     # for i in range(self.len / 2):
    #     #     self.np[ (led + i) % self.len ] = (0,0,color)
    #     #     self.np[ (led - i) % self.len ] = (0,0,color)
    #     #     color = color - 21 # 255//6

    def clear(self):
        for i in range(self.len):
            self.np[i] = (0,0,0)
    def clearLetter(self):
        for i in range(self.lenLetter):
            self.np_letter[i] = (0,0,0)
            
    def wheelRB(self, pos):
        #   Input a value 0 to 255 to get a color value.
        #   The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, 0, 0)
        if pos < 170:
            pos -= 85
            return (0, 0, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    def wheel(self, pos):
        #   Input a value 0 to 255 to get a color value.
        #   The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

    def fillFromBottom(self, color, delay):
        for i in range(6):
            self.np[ (self.len // 2) + i] = color
            self.np[ (self.len // 2) - i] = color
            self.np.write()
            sleep_ms(delay)

        self.np[0] = color
        self.np.write()
        sleep_ms(delay)