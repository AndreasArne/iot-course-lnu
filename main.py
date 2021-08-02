import time
import ubinascii
import hashlib
from mqttclient import MQTTClient
from machine import Pin
from _pybytes import Pybytes, unique_id
from _pybytes_config import PybytesConfig

print("Setup")

# Use pybytes config to connect to Wifi
conf = PybytesConfig().read_config()
pybytes = Pybytes(conf)
pybytes.start()

# Prepare pin to read from sensor
pin_input = Pin('P16', mode = Pin.IN)

# mqtt settings
topic_pub = 'home/bedroom/'
broker_url = '<IP-to-broker>'

client_name = ubinascii.hexlify(hashlib.md5(unique_id()).digest()) # create a md5 hash of the pycom WLAN mac
c = MQTTClient(client_name,broker_url)
c.connect()

def send_value(motion, mq):
    # create message and send it
    value = '{"bedroom": { "motion": ' + str(motion) + '}}'
    try:
        mq.publish(topic_pub, value)
        print('Sensor data sent with value {}'.format(motion))
    except (NameError, ValueError, TypeError) as e:
        print('Failed to send!')
        print(e)

    # also send pybytes signal
    pybytes.send_signal(99, motion)


old_motion = 0
while True: # main loop
    motion = pin_input.value() # 1 for movement, 0 for nothing
    if old_motion != motion: #  if state has changed, send it
        old_motion = motion
        send_value(motion, c)
    time.sleep(2)
