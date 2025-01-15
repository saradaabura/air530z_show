from machine import Pin, UART, I2C, RTC
machine.freq(270000000)
from pygps import gga, convert, gsv, zda, vtg, gsa
import time
from gpshow import showup
import _thread
gps_module = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
led = machine.Pin(25, machine.Pin.OUT)
save_bt = Pin(21, Pin.IN, Pin.PULL_UP)
nmea0183 = 0; pronmea = 0; gnss = ""
raw_gga = 0; raw_zda = 0; raw_gsa = 0
raw_vtg = 0; confirmedgga = 0; showdata = [0]
confirmedzda = 0; confirmedvtg = 0; confirmedgsa = 0
sv = 0; la = 0.0; lo = 0.0; sv = 0; mode = 0; switch = 1; switch_0 = 0; speed = 0
ti = 0; path = "/gps.txt"; tick = 0; tims = 0; history = []
runtime = 0; rtc = RTC(); raw_rtc = 0
def update(gps):
    global nmea0183; global pronmea; global raw_gga; global raw_zda; global raw_vtg; global raw_gsa
    global confirmedgga; global confirmedzda; global confirmedvtg; global confirmedgsa; global gnss
    global sv; global la; global lo; global sv
    raw = 0
    raw = str(gps.read(1000))
    nmea0183 = raw[raw.find("$GNGGA"):raw.find("$GPZDA")]
    if nmea0183 != "":
        gnss = nmea0183
        pronmea = gnss.split("$")
        raw_gga = pronmea[1].split(",")
        raw_zda = pronmea[len(pronmea) - 2].split(",")
        raw_vtg = pronmea[len(pronmea) - 3].split(",")
        raw_gsa = pronmea[3].split(",")
        confirmedgsa = gsa(raw_gsa)
        if confirmedgsa != None:
            if confirmedgsa["FixType"] >= 2:
                if len(pronmea) > 12:
                    confirmedgga = gga(raw_gga)
                    confirmedzda = zda(raw_zda)
                    confirmedvtg = vtg(raw_vtg)
                    la = convert(confirmedgga[4])
                    lo = convert(confirmedgga[5])
                    sv = gsv(gnss)
                    if confirmedzda[0] != 0 or confirmedzda[1] != 0:
                        rtc.datetime((confirmedzda[0], confirmedzda[1], confirmedzda[2], 0, int(confirmedzda[3]), int(confirmedzda[4]), int(confirmedzda[5]), int(confirmedzda[6])))
            return True
        
        return None
def log():
    led.value(1)
    with open(path, 'a') as f:
        f.write(str(tmp) + '\n')
    led.value(0)
while True:
    take_start = time.ticks_ms()
    nmea_status = update(gps_module)
    if nmea_status != None:
        if confirmedgsa["FixType"] >= 2:
            if time.ticks_ms() - tims >= 0.5 * 1000:
                history.append((float(lo), float(la)))
                tims = time.ticks_ms()
            raw_rtc = rtc.datetime()
            showdata = la, lo, raw_rtc, sv[1], confirmedgga[1], confirmedgsa["PDOP"], confirmedgga[6], confirmedvtg[0], confirmedvtg[1], tick, sv[0], int(mode), history
            if runtime != confirmedzda:
                showup(showdata, confirmedgsa["FixType"])
                runtime = confirmedzda
            tick = [30, 10, 5, 15, 60][speed]
            date = str(raw_rtc[0]) + "/" + str(raw_rtc[1]) + "/" + str(raw_rtc[2])
            tm = str(raw_rtc[4]) + ":" + str(raw_rtc[5]) + ":" + str(raw_rtc[6])
            tmp = f"{date}/{tm},{la},{lo}"
            if time.time() - ti >= tick:
                log()
                ti = time.time()
        showup(showdata, confirmedgsa["FixType"])
    else:
        #print(rp2.bootsel_button())
        if rp2.bootsel_button() == 1 and switch == 0:
            mode = mode + 1
            switch = 1
            if mode == 4:
                mode = 0
        if switch == 1 and rp2.bootsel_button() == 0:
            switch = 0
        if save_bt.value() == 1 and switch_0 == 0:
            speed = speed + 1
            switch_0 = 1
            if speed == 5:
                speed = 0
        if switch_0 == 1 and save_bt.value() == 0:
            switch_0 = 0
        if len(history) >= 150:
            history.pop(0)
            print(history)
    take_finish = time.ticks_ms()
    #print(take_finish - take_start)