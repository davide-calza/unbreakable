import paho.mqtt.client as mqtt
import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
nome_ventola=["Ventola-Rotta","Ventola-Buona"]
sezione_ventola=["k","k"]
print(nome_ventola,sezione_ventola)
try:
    for i in range(0,len(nome_ventola)):
        c.execute("INSERT OR IGNORE INTO Componente (Nome,Sezione) VALUES (?,?)",(nome_ventola[i],sezione_ventola[i]))
        conn.commit()
except:
     print("test")
     pass
def on_message(client, userdata, message):
    coordinates=message.payload.decode("utf-8").split(",")
    coordinates[3]=coordinates[3].replace("\x00","")
    c.execute("INSERT INTO Coordinate (X,Y,Z,Nome_Componente) VALUES (?,?,?,?)",(coordinates[1],coordinates[2],coordinates[3],coordinates[0]))
    conn.commit()

client =mqtt.Client("test")
user="prom2"
password="prom2"

client.username_pw_set(user, password=password)
client.on_message= on_message
client.connect("192.168.181.2", port=8883)
for i in range(0,len(nome_ventola)):
    client.subscribe("prom2/"+nome_ventola[i])
#client.publish("prom2/test","ON")

client.loop_forever()
