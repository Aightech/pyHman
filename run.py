import pyhman as ph
import time
hman = ph.Hman()
hman.connect('192.168.127.151')
#set the motors in articular position

hman.setPID([0.001,0.0000,0])#set the PID at Kp=0.005, Ki=0.0000, Kd=0.005

sp = [4000,4000,180]
T = 5
nb_step=1
dt=T/nb_step

hman.home()

for i in range(1,nb_step,1):
    pos = hman.set_cartesian_pos(int(sp[0]*i/nb_step),int(sp[1]*i/nb_step),int(sp[2]*i/nb_step))
    print(pos)
    time.sleep(dt)

for i in range(nb_step,-1,-1):
    pos = hman.set_cartesian_pos(int(sp[0]*i/nb_step),int(sp[1]*i/nb_step),int(sp[2]*i/nb_step))
    print(pos)
    time.sleep(dt)

#pos = hman.set_motors_current(1000,1000,1000)
# print(pos)

time.sleep(3)

hman.disconnect()