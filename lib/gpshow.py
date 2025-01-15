import time
from ili9341 import Display, color565
from machine import Pin, SPI
import framebuf
import math
from misakifont import MisakiFont
from xpt2046 import Touch
import gc
spi = SPI(0, baudrate=32250000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB, sck=Pin(6), mosi=Pin(7))
display = Display(spi, dc=Pin(15), cs=Pin(13), rst=Pin(14), width=240, height=320, rotation=0)
def touch(x, y):
    global thx; global thy
    thx = x; thy = y
spiXPT = SPI(1, baudrate=200000,sck=Pin(10), mosi=Pin(11), miso=Pin(8))
xpt = Touch(spiXPT, cs=Pin(12), int_pin=Pin(0), int_handler=touch)
buffer_width = 154; thx = 0
buffer_height = 154; thy = 0; thdata = 0
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)
ndata = 0; ab = 0; way = 0
def draw_point(elevation, azimuth, cr, radius=70):
    center_x = int(buffer_width / 2)
    center_y = int(buffer_height / 2)
    elevation_rad = math.radians(elevation)
    azimuth_rad = math.radians(azimuth - 0)
    x = center_x + int(radius * math.sin(elevation_rad) * math.cos(azimuth_rad))
    y = center_y - int(radius * math.sin(elevation_rad) * math.sin(azimuth_rad))
    fbuf.pixel(x, y, cr)
    return x, y
def show_bitmap(display, fd, x, y, color, size):
    for row in range(0, 7):
        for col in range(0, 7):
            if (0x80 >> col) & fd[row]:
                fbuf.fill_rect(int(x + col * size), int(y + row * size), size, size, color)
mf = MisakiFont()
def msktext(str, x, y, fcolor, fsize=1):
    global display
    for c in str:
        d = mf.font(ord(c))
        show_bitmap(display, d, x, y, fcolor, fsize)
        x += 8 * fsize
        if x >= buffer_width:
            x = 0
            y += 8 * fsize
        if y >= buffer_height:
            y = 0
def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    if not full:
        return P
    else:
        return ('Total:{0} Free:{1} ({2})'.format(T, F, P))
def show():
    display.block(int((240 - buffer_width) / 2), int((320 - buffer_height) / 2), int((240 - buffer_width) / 2) + buffer_width-1, int((320 - buffer_height) / 2) + buffer_height-1, buffer)
def showup(inp, fix):
    global ab; global way; global ndata; global thdata
    fbuf.fill(color565(0, 0, 0))
    if fix <= 1:
        msktext('No Fix...', 0, 0, color565(255, 255, 255))
        show()
        return
    la, lo, dateutc, satellites, used_satellites, pdop, alt, course, kmh, tick, sdata, mode, history = inp
    if mode == 0:
        ram = free()
        date = f"{dateutc[0]}/{dateutc[1]}/{dateutc[2]}"
        time = f"{dateutc[4]}:{dateutc[5]}:{dateutc[6]}.{dateutc[7]}"
        msktext(f"Mode 0 tick: {tick}", 0, 0, color565(255, 255, 255))
        msktext(f"la: {la}", 0, 9, color565(255, 255, 255))
        msktext(f"lo: {lo}", 0, 18, color565(255, 255, 255))
        msktext(f"satellite: {used_satellites}/{satellites}", 0, 27, color565(255, 255, 255))
        msktext(f"{date} UTC", 0, 36, color565(255, 255, 255))
        msktext(f"{time}", 0, 45, color565(255, 255, 255))
        msktext(f"{kmh} km/h", 0, 54, color565(255, 255, 255))
        msktext(f"{course}*", 0, 63, color565(255, 255, 255))
        msktext(f"{alt} m", 0, 72, color565(255, 255, 255))
        msktext(str(pdop), 0, 81, color565(255, 255, 255))
        msktext(f"freeram{ram}", 0, 90, color565(255, 255, 255))
        show()
    if mode == 1:
        while True:
            ram = free()
            msktext(f"Mode 1 tick: {tick}", 0, 0, color565(255, 255, 255))
            msktext(f"freeram{ram}", 0, 9, color565(255, 255, 255))
            way = sdata[ndata]
            data = draw_point(way["EL"], way["AZ"] - 270, color565(255, 0, 0))
            msktext(str(way["SV"]), data[0], data [1], color565(255, 255, 255))
            ndata = ndata + 1
            while ab <= 359:
                draw_point(90, ab, color565(255,255,255))
                ab = ab + 1
            if len(sdata) <= ndata:
                break
        ab = 0
        ndata = 0
        show()
    if mode == 2:
        msktext(f"Mode 2 tick: {tick}", 0, 0, color565(255, 255, 255))
        ram = free()
        msktext(f"freeram{ram}", 0, 8, color565(255, 255, 255))
        i = len(history)
        lenlist = len(history)
        now_la = history[lenlist - 1][0]
        now_lo = history[lenlist - 1][1]
        odx = int(buffer_width / 2)
        ody = int(buffer_height / 2)
        while True:
            if i == 1:
                break
            i = i - 1
            x = now_la - history[i - 1][0]
            y = now_lo - history[i - 1][1]
            dx = int(buffer_width / 2) + int(x * 100000)
            dy = int(buffer_height / 2) + int(y * 100000)
            if x < 0 or 190 > x:
                pass
            if y < 0 or 190 > y:
                pass
            fbuf.line(odx, ody, dx, dy, color565(255, 255, 255))
            odx = dx
            ody = dy
        fbuf.fill_rect(int(buffer_width / 2) - 3, int(buffer_height / 2) - 3 , 6, 6,color565(255, 0, 0))
        show()
    if mode == 3:
        fbuf.fill(color565(0, 0, 0))
        thdata = xpt.raw_touch()
        if thdata != None:
            x = thdata[0]
            y = thdata[1]
            msktext(f"{x}, {y}", 0, 0, color565(255, 255, 255))
            ram = free()
            msktext(f"freeram{ram}", 0, 20, color565(255, 255, 255))
        else:
            msktext("No Tap", 0, 0, color565(255, 255, 255))
        show()