# Configuration File for Thermal Comfort Monitoring System
# Group 19 - IoT Project

# ============================================
# WiFi Configuration
# ============================================
WIFI_SSID = ''
WIFI_PASSWORD = ''

# ============================================
# MQTT Broker Configuration (HiveMQ Cloud)
# ============================================
MQTT_SERVER = ''
MQTT_PORT = ''
MQTT_USER = ''
MQTT_PWD = ''
MQTT_TOPIC = 'sensors/env'
MQTT_CLIENT_ID = '"pico_client"'

# ============================================
# Hardware Configuration
# ============================================
# LED Pins for Comfort Indication
LED_GREEN_PIN = 15  # GPIO 15 for Green LED (Comfortable)
LED_RED_PIN = 14    # GPIO 14 for Red LED (Uncomfortable)

# I2C Configuration
SDA = 0
SCL = 1
FREQ = 400000
LCD_ADDR = 0x27
ROWS = 2
COLS = 16
# ============================================
# Thermal Comfort Thresholds
# ============================================
# Temperature range for comfort (°C)
TEMP_MIN_COMFORTABLE = 20.0
TEMP_MAX_COMFORTABLE = 26.0

# Humidity range for comfort (%)
HUMIDITY_MIN_COMFORTABLE = 30.0
HUMIDITY_MAX_COMFORTABLE = 60.0
