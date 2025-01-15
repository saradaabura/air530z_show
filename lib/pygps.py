def gga(gga):
    if "GNGGA" == gga[0]:
        utc_string = gga[1]
        hours = int(utc_string[0:2])
        minutes = int(utc_string[2:4])
        seconds = float(utc_string[4:])
        satellites_in_use = int(gga[7])
        fix_stat = int(gga[6])
        hdop = float(gga[8])
        l_string = gga[2]
        lat_degs = int(l_string[0:2])
        lat_mins = float(l_string[2:])
        lat_hemi = gga[3]
        l_string = gga[4]
        lon_degs = int(l_string[0:3])
        lon_mins = float(l_string[3:])
        lon_hemi = gga[5]
        altitude = float(gga[9])
        geoid_height = float(gga[11])
        latitude = [lat_degs, lat_mins, lat_hemi]
        longitude = [lon_degs, lon_mins, lon_hemi]
        timestamp = [hours, minutes, seconds]
        return timestamp, satellites_in_use, hdop, fix_stat, latitude, longitude, altitude, geoid_height
def convert(parts):
    if parts[0] == 0:
        return None
    data = parts[0] + (parts[1] / 60.0)
    if parts[2] in ['S', 'W']:
        data = -data
    return '{0:.6f}'.format(data)
def gsv(nmea_data):
    satellite_info_list = []
    satellites = 0
    nmea_lines = nmea_data.split('\\r\\n')
    gsv_lines = [line for line in nmea_lines if line.startswith('$GPGSV') or line.startswith('$BDGSV') or line.startswith('$GLGSV')]
    for sentence in gsv_lines:
        parts = sentence.split(',')
        try:
            num_satellites = int(parts[3])
            for i in range(4, len(parts) - 4, 4):
                satellite_id = int(parts[i])
                elevation = int(parts[i+1])
                azimuth = int(parts[i+2])
                snr = int(parts[i+3]) if parts[i+3] else 0
                satellite_info_list.append({
                    'SV': satellite_id,
                    'EL': elevation,
                    'AZ': azimuth,
                    'SNR': snr
                })
                satellites += 1
        except (ValueError):
            pass
        except (IndexError):
            print(f"データが読み込めない ワロタ")
    return satellite_info_list, satellites
def zda(raw_zda):
    if "GNZDA" == raw_zda[0]:
        time = raw_zda[1]
        h = time[0:2]
        m = time[2:4]
        s = time[4:6]
        ms = time[7:10]
        return int(raw_zda[4]), int(raw_zda[3]), int(raw_zda[2]), h, m, s, ms
    else:
        return 0, 0, 0, "0", "0", "0", "0"
def vtg(raw_vtg):
    if "GNVTG" == raw_vtg[0]:
        course = raw_vtg[1]
        kmh = raw_vtg[7]
        return course, kmh
    return 0,0
def gsa(raw_gsa):
    if raw_gsa[0] == "GNGSA":
        try:
            mode = raw_gsa[1]
            fix_type = int(raw_gsa[2])
            satellites_used = [int(sat) for sat in raw_gsa[3:15] if sat.isdigit()]
            pdop = float(raw_gsa[15])
            hdop = float(raw_gsa[16])
            vdop = float(raw_gsa[17].split('*')[0])

            return {
                'Mode': mode,
                'FixType': fix_type,
                'SatellitesUsed': satellites_used,
                'PDOP': pdop,
                'HDOP': hdop,
                'VDOP': vdop
            }
        except (ValueError, IndexError):
            return None
    else:
        return None