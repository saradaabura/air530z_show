**はじめに**
pico_MicroPython_misakifont
を利用して動作しています。
 Tamakichiさんありがとうございます
/にmisakifontのフォルダを入れることで動作します。
**環境**
・Raspberry Pi Pico 1
・micropython 25/1/1最新ファームウェア
・Air530Z(Glove モジュール)
→NMEA0183プロトコル,115200bps
・ili9341ライブラリ
→フレームバッファー使用
**使用ピン**
Air530Zモジュール
gps|pico
TX  5
(gps_module = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5)))
なおRXのみ使用しておりPicoのTXは接続されていません。したがってPicoとの接続はVCC(3.3V),GND,TX(air530z)の計3本です。
ili9341
SPIです。以下のような接続です。
                      ↓かなりのOCです。400でもいいと思います。(flamebuf使用のため)
spi = SPI(0, baudrate=32250000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB, sck=Pin(6), mosi=Pin(7))
display = Display(spi, dc=Pin(15), cs=Pin(13), rst=Pin(14), width=240, height=320, rotation=0)
