


#define SERIAL_DEBUG 1
#define LOGLN(...)   \
    if(SERIAL_DEBUG) \
    Serial.println(__VA_ARGS__)
#define LOG(...)     \
    if(SERIAL_DEBUG) \
    Serial.print(__VA_ARGS__)
#include "hman.h"
#include <NativeEthernet.h>
#include <Wire.h>

Hman hman;

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 127, 250);
EthernetServer server(5000);

int pkgSize = 1 + 1 + 8 * 3; //cmd + index + data
byte buff[255];

IntervalTimer pid_timer;
IntervalTimer traj_timer;

long last_time = 0;

void setup()
{
    if(SERIAL_DEBUG)
        Serial.begin(9600);
        delay(1000);
    LOGLN("HMAN");

    Ethernet.begin(mac, ip); // start the Ethernet connection and the server:
    // Check for Ethernet hardware present
    if(Ethernet.hardwareStatus() == EthernetNoHardware)
        LOGLN("Ethernet shield was not found.");
    if(Ethernet.linkStatus() == LinkOFF)
        LOGLN("Ethernet cable is not connected.");
    

    LOG("Ethernet server on ");
    LOG(Ethernet.localIP());
    LOGLN(String(":5000"));
    server.begin();

    last_time = micros();
    pid_timer.begin(update_pid, hman.update_dt_us);
    //traj_timer.begin(update_traj, hman.m_traj_dt_micro);


    // int dx=40,dy=0, vm=20, am=60;
    // hman.add_delta_traj(dx, dy, vm,am);
    // hman.add_delta_traj(-dx, -dy,vm,am);
    // hman.start_traj();
}

void update_pid() { 
    if(micros()-last_time>hman.update_dt_us)
    {
        Serial.println("dt: "+String(micros()-last_time));
    }
    last_time=micros();
    hman.update();
    //Serial.println("dt: "+String(micros()-last_time));
    
     }
void update_traj() { hman.trajectory(); }

void loop()
{
    EthernetClient client = server.available();
    if(client)
    {
        LOGLN("new client");
        while(client.connected())
        {
            int len = client.available();
            if(len >= pkgSize)
            {
                client.read(buff, pkgSize);
                uint8_t index = buff[1];
                switch(buff[0])
                {
                case 'M': //mode
                {
                    hman.set_mode((Motor::Mode) * (int32_t *)(buff + 2));
                    LOGLN("Mode set: " + String(*(int32_t *)(buff + 2)));
                    break;
                }
                case 'K': //mode
                {
                    hman.set_Kpid((int32_t *)(buff + 2));
                    LOG("PID: [");
                    for(int i = 0; i < 3; i++)
                        LOG(" " + String(*(int32_t *)(buff + 2 + 4 * i)));
                    LOGLN("]");
                    break;
                }
                case 'S': //max speed
                {
                    hman.set_max_speed((int32_t *)(buff + 2));
                    LOG("Max speed: [");
                    for(int i = 0; i < 3; i++)
                        LOG(" " + String(*(int32_t *)(buff + 2 + 4 * i)));
                    LOGLN("]");
                    break;
                }
                case 'V': //set value (current, position, speed depending of the mode seleted)
                {
                    int m=hman.mode();
                    // LOG("Mode: " + String(m) + "  values: [");
                    // for(int i = 0; i < NB_MOT; i++)
                    //     LOG(" " + String(*(int32_t *)(buff + 2 + 4 * i)));
                    // LOGLN("]");
                    switch(hman.mode())
                    {
                    case Motor::position:
                    {
                        hman.set_articular_pos((int32_t *)(buff + 2), index);
                        break;
                    }
                    case Motor::current:
                    {
                        hman.set_motor_current((int32_t *)(buff + 2), index);
                        break;
                    }
                    }
                    client.write((uint8_t *)(hman.get_pos()), 4 * NB_MOT);
                    break;
                }
                case 'P': // return encoder position
                {
                    client.write((uint8_t *)(hman.get_pos()), 4 * NB_MOT);
                    break;
                }
                case 'I': // return digital input
                {
                    uint8_t v = digitalRead(index);
                    client.write((uint8_t *)(&v), 1);
                    break;
                }
                case 'A': // return analog input
                {
                    uint16_t v = analogRead(index);
                    client.write((uint8_t *)(&v), 2);
                    break;
                }
                case 'H': // start homing process
                {
                    uint8_t r = hman.home();
                    client.write(&r, 1);
                    break;
                }
                case 'T': // trajecory mode
                {
                    if(index == 1)
                        hman.start_traj();
                    else if(index == 2)
                    {
                        int32_t dx = *(int32_t *)(buff + 2 + 4 * 0);
                        int32_t dy = *(int32_t *)(buff + 2 + 4 * 1);
                        int32_t vm = *(int32_t *)(buff + 2 + 4 * 2);
                        int32_t am = *(int32_t *)(buff + 2 + 4 * 3);
                        hman.add_delta_traj(dx, dy, vm, am);
                    }
                    else
                        hman.stop_traj();
                    break;
                }
                }
            }
        }

        client.stop(); // close the connection
        hman.set_current(0);

        LOGLN("client disconnected");
        delay(10);
    }
}
