import network
import time
from machine import Pin, I2C
import bme280
from umqtt.simple import MQTTClient
import ussl
import config
from lcd_pcf8574 import I2cLcd
try:
    from machine_learning.comfort_model import RandomForestClassifier
    clf = RandomForestClassifier()
    ML_AVAILABLE = True
    print("[INFO] ML model loaded successfully (class)!")
except ImportError:
    ML_AVAILABLE = False
    print("[WARNING] ML model not found, using rule-based logic")

# =========================
# ✅ LED SETUP
# =========================
green_led = Pin(config.LED_GREEN_PIN, Pin.OUT)   # GREEN LED
red_led = Pin(config.LED_RED_PIN, Pin.OUT)     # RED LED

green_led.off()
red_led.off()

# -------------------------
# 1. WIFI CONFIG
# -------------------------
WIFI_SSID = config.WIFI_SSID
WIFI_PASSWORD = config.WIFI_PASSWORD

# -------------------------
# 2. MQTT CONFIG
# -------------------------
MQTT_SERVER = config.MQTT_SERVER
MQTT_PORT = config.MQTT_PORT
MQTT_USERNAME = config.MQTT_USER
MQTT_PASSWORD = config.MQTT_PWD
MQTT_CLIENT = config.MQTT_CLIENT_ID

MQTT_TOPIC = config.MQTT_TOPIC.encode()

# =========================
# I2C SETUP (LCD + BME280)
# =========================
i2c = I2C(0, sda=Pin(config.SDA), scl=Pin(config.SCL), freq=config.FREQ)

# =========================
# LCD INIT
# =========================
lcd = I2cLcd(i2c, addr=config.LCD_ADDR,
             cols=config.COLS, rows=config.ROWS)


def connect_wifi():
    """Connect to WiFi Network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(1)

    print("[INFO] Connected to WiFi!")
    print("[INFO] IP:", wlan.ifconfig()[0])
    return wlan


def init_bme280():
    """Initialize BME280 Sensor"""
    devices = i2c.scan()
    print("[INFO] I2C Devices:", devices)
    bme = bme280.BME280(i2c=i2c)
    print("[INFO] BME280 ready")
    return bme


def connect_mqtt():
    """Connect to MQTT Broker"""
    print("[INFO] Connecting to MQTT...")
    client = MQTTClient(
        client_id=MQTT_CLIENT,
        server=MQTT_SERVER,
        port=MQTT_PORT,
        user=MQTT_USERNAME,
        password=MQTT_PASSWORD,
        ssl=True,
        ssl_params={"server_hostname": MQTT_SERVER}
    )
    client.connect()
    print("[INFO] MQTT Connected")
    return client


def comfort_status(temp, hum):
    """Determine Comfort Status and Control LEDs"""
    is_temp_okay = config.TEMP_MIN_COMFORTABLE <= temp \
        <= config.TEMP_MAX_COMFORTABLE
    is_hum_okay = config.HUMIDITY_MIN_COMFORTABLE <= hum \
        <= config.HUMIDITY_MAX_COMFORTABLE

    if is_temp_okay and is_hum_okay:
        green_led.on()   # ✅ Comfortable → Green ON
        red_led.off()
        return "Comfort"
    else:
        green_led.off()
        red_led.on()     # ✅ Uncomfortable → Red ON
        return "Uncomf"


def predict_fallback(temp, hum, press):
    """Fallback rule-based prediction"""
    is_temp_okay = config.TEMP_MIN_COMFORTABLE <= temp \
        <= config.TEMP_MAX_COMFORTABLE
    is_hum_okay = config.HUMIDITY_MIN_COMFORTABLE <= hum \
        <= config.HUMIDITY_MAX_COMFORTABLE

    if is_temp_okay and is_hum_okay:
        green_led.on()   # ✅ Comfortable → Green ON
        red_led.off()
        return "Comfort", 0.80
    else:
        green_led.off()
        red_led.on()     # ✅ Uncomfortable → Red ON
        return "Uncomf", 0.80


def predict_ml(temp, hum, press):
    """Use ML model for prediction"""
    try:
        # The generated RandomForest expects pressure in Pascals (~101700),
        # while the code passes hPa (around 1000); convert when it looks like hPa.
        p = press * 100 if press < 2000 else press
        prediction = clf.predict([temp, hum, p])

        # prediction is 0 or 1
        if prediction == 1:
            green_led.on()   # ✅ Comfortable → Green ON
            red_led.off()
            return "Comfort", 0.95
        else:
            green_led.off()
            red_led.on()     # ✅ Uncomfortable → Red ON
            return "Uncomf", 0.95
    except Exception as e:
        print(f"[ERROR] ML prediction failed: {e}")
        return predict_fallback(temp, hum, press)


def predict_comfort(temp, hum, press):
    """Main prediction function - uses ML if available"""
    if ML_AVAILABLE:
        return predict_ml(temp, hum, press)
    else:
        return predict_fallback(temp, hum, press)


# =========================
# SYSTEM START
# =========================
lcd.clear()
lcd.move(0, 0)
lcd.string("System Booting")

wifi = connect_wifi()
bme = init_bme280()
mqtt_client = connect_mqtt()
model_type = "ML" if ML_AVAILABLE else "Rules"

# =========================
# MAIN LOOP
# =========================
try:
    while True:
        temperature, pressure, humidity = bme.read_compensated_data()
        pressure_hpa = pressure / 100

        # Predict using ML or fallback
        status, confidence = predict_comfort(
            temperature, humidity, pressure_hpa)

        # ---- SERIAL OUTPUT ----
        print("Temp:", temperature)
        print("Humidity:", humidity)
        print("Pressure:", pressure_hpa)
        print("Status:", status)

        # ---- LCD DISPLAY ----
        lcd.clear()
        lcd.move(0, 0)
        lcd.string("T:{:.1f} H:{:.1f}".format(temperature, humidity))
        lcd.move(1, 0)
        lcd.string("P:{:.0f} {}".format(pressure_hpa, status))

        # ---- MQTT JSON ----
        json_msg = (
            '{"temperature": %.2f, "humidity": %.2f, "pressure": %.2f, "status": "%s"}'
            % (temperature, humidity, pressure_hpa, status))

        mqtt_client.publish(MQTT_TOPIC, json_msg)
        print("[INFO] MQTT:", json_msg, "\n")
        print(
            f"Prediction ({model_type}): {status} ({confidence*100:.0f}% confidence)\n")

        time.sleep(2)

finally:
    # ✅ This always runs when the script stops
    green_led.off()
    red_led.off()
    print("LEDs turned off, program terminated")
