import cv2

import paho.mqtt.client as paho
from paho import mqtt


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNECT received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))


client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect


client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

client.username_pw_set("testing", "Testing1234")

client.connect("85e5f62c47ba413e8fa64e36d2ab5a34.s1.eu.hivemq.cloud", 8883)

client.on_publish = on_publish

cap = cv2.VideoCapture(0)

while True:
  _, frame = cap.read()
 
  decoder = cv2.QRCodeDetector()
  data, points, _ = decoder.detectAndDecode(frame)
  
  if data:
    client.publish("id_kamion/naklad", payload=str(data), qos=1)
    print(data)
  
  cv2.imshow('frame',frame)
  key = cv2.waitKey(1)
  if key & 0xFF == ord('q'):
      break

cv2.destroyAllWindows()