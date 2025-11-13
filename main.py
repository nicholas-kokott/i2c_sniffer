import smbus
import csv
import time
from datetime import datetime

def process_location(data):
    x_location = data[6] * 256 + data[5]
    y_location = data[8] * 256 + data[7]

    area = "NA"
    if x_location <= 645 and y_location <= 240:
        area = "UpperLeft"
    elif x_location > 645 and y_location <= 240:
        area = "UpperRight"
    elif x_location <= 645 and y_location > 240:
        area = "LowerLeft"
    elif x_location > 645 and y_location > 240:
        area = "LowerRight"
    
    return x_location, y_location, area

def process_touch_type(data):
    touch_type = "Unknown"
    if data[4] == 0x94:
        touch_type = "Down"
    elif data[4] == 0x91:
        touch_type = "Moving"
    elif data[4] == 0x15:
        touch_type = "Up"
    elif data[4] == 0x21:
        touch_type = "NoTouch"

    return touch_type
    

def main():
    file_name = f"csvs/touches_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    header = ["Time", "TouchFound", "TouchType", "LocationX", "LocationY", "GeneralLocation", "TouchCount"]

    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        bus = smbus.SMBus(1)
        device_addr = 0x4B
        register = 0x05
        num_bytes = 16

        x_value_reading = -1
        y_value_reading = -1
        region = "NoTouch"
        touch_type = "N/A"
        touch_count = 0

        while(True):
            data = bus.read_i2c_block_data(device_addr, register, num_bytes)

            if data[2] == 0x64 and data[3] != 0x03:
                touch_type = process_touch_type(data)
                x_value_reading, y_value_reading, region = process_location(data)
                touch_count += 1
                row = [datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), "TouchDetected", touch_type, x_value_reading, y_value_reading, region, touch_count]
                writer.writerow(row)
            else:
                x_value_reading = -1
                y_value_reading = -1
                touch_type = "N/A"

            time.sleep(1)

if __name__ == "__main__":
    main()