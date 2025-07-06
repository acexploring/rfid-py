from pirc522 import RFID
import signal
import time

rdr = RFID()
util = rdr.util()
util.debug = True

try:
    while True:
        rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        if not error:
            print("Tag detected")
            (error, uid) = rdr.anticoll()
            if not error:
                print("UID:", uid)
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    rdr.cleanup()