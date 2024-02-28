#include <Encoder.h>

class Motor
{
    public:
    enum Mode
    {
        stopped = -1,
        position = 0,
        current = 1
    };

    Motor(
        int encPin1, int encPin2, int drvPinPWM_, int drvPinEn_, int drvPinDir_)
        : m_encoder(Encoder(encPin1, encPin2))
    {
        id = nb_mot;
        nb_mot++;
        double Kp = 0.007, Ki = 0.000001, Kd = 0;
        Kpid[0] = Kp;
        Kpid[1] = Ki;
        Kpid[2] = Kd;

        m_scale_PWM = max_PWM - min_PWM;

        analogWriteResolution(12);
        m_drvPinPWM = drvPinPWM_;
        m_drvPinEn = drvPinEn_;
        m_drvPinDir = drvPinDir_;
        pinMode(m_drvPinPWM, OUTPUT);
        analogWrite(m_drvPinPWM, 410);
        pinMode(m_drvPinDir, OUTPUT);
        digitalWrite(m_drvPinDir, LOW);
        pinMode(m_drvPinEn, OUTPUT);
        digitalWrite(m_drvPinEn, HIGH);
    }

    void update(int8_t *valEndSwitch, int n)
    {
        double o = 0;

        if(mode == Motor::position)
        {
            m_derr = -m_perr;
            m_speed = m_position;

            m_position = m_encoder.read();

            m_perr = (m_setPoint - m_position);
            m_derr += m_perr;
            m_ierr += m_perr;
            
            if(abs(m_perr) < 10)
                m_ierr = 0;

            m_ierr = max(-20000, min(20000, m_ierr));
            
            m_speed -= m_position;
            m_speed = abs(m_speed);

            o = Kpid[0] * m_perr + Kpid[1] * m_ierr + Kpid[2] * m_derr;
            
            //friction compensation: if the motor is stopped but the setpoint is not reached, the motor will not move
            // if(abs(m_speed) < 10 && abs(o) > 0.5)
            // {
            //     double f = 0.10;
                
            //     o += (o > 0) ? -f : f;
            // }
            o = (o < -1) ? -1 : ((o > 1) ? 1 : o); //ensure -1<o<1

            if(abs(m_speed) > max_speed)
            
            {
                Serial.println("saturate: " + String(m_speed));
                o = 0;
            }
        }
        else if(mode == Motor::current)
        {
            //Serial.println(m_current);
            o = m_current; //m_current is set by the method set_current
        }

        if(o > 0)
            digitalWrite(m_drvPinDir, LOW);
        else
        {
            o = -o;
            digitalWrite(m_drvPinDir, HIGH);
        }
        m_PWM = min_PWM + m_scale_PWM * abs(o);
        analogWrite(m_drvPinPWM, m_PWM);
    }

    void set_pos(int32_t sp) { m_setPoint = sp; };

    void set_current(int32_t curr) //between -1000 and 1000
    {
        double c = curr / 1000.0;
        m_current = (c < -1) ? -1 : ((c > 1) ? 1 : c);
    };

    int64_t get_pos() { return m_encoder.read(); }

    void set_zero() { m_encoder.write(0); }

    static int nb_mot;
    int id;

    int16_t min_PWM = 410;
    int16_t max_PWM = 3686;
    double Kpid[3];

    double max_speed = 50;

    Motor::Mode mode = Motor::current;

    private:
    Encoder m_encoder;
    int16_t m_PWM = 0;
    int16_t m_scale_PWM = 1;
    float m_position = 0;
    double m_speed = 0;
    double m_perr = 0;
    double m_derr = 0;
    double m_ierr = 0;
    int64_t m_setPoint = 0;
    double m_current = 0; //value between -1 and 1;
    int m_drvPinPWM;
    int m_drvPinEn;
    int m_drvPinDir;
};
