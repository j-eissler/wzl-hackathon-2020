#!/usr/bin/python3
import subprocess
import re
import requests
import json
import paho.mqtt.client as mqtt
import time
import os

thingsboard_protocol = str(os.environ['thingsboard_protocol'])
thingsboard_address = str(os.environ['thingsboard_address'])
thingsboard_port = str(os.environ['thingsboard_port'])
thingsboard_headers = {"Content-Type":"application/json"}
thingsboard_entities = ["timestamp", "axis1_joint_position", "axis2_joint_position", "axis3_joint_position", "axis4_joint_position", "axis5_joint_position", "axis6_joint_position", "axis1_joint_velocity", "axis2_joint_velocity", "axis3_joint_velocity", "axis4_joint_velocity", "axis5_joint_velocity", "axis6_joint_velocity", "axis1_motor_current", "axis2_motor_current", "axis3_motor_current", "axis4_motor_current", "axis5_motor_current", "axis6_motor_current"]
thingsboard_update_interval = int(os.environ['thingsboard_update_interval'])
mqtt_broker_address = str(os.environ['mqtt_broker_address'])
mqtt_broker_port = int(os.environ['mqtt_broker_port'])
mqtt_broker_topic = str(os.environ['mqtt_broker_topic'])






# Instantiate a new mqtt client
mqtt_client = mqtt.Client()
mqtt_client.connect(mqtt_broker_address, port=mqtt_broker_port)
mqtt_client.subscribe(mqtt_broker_topic)
current_mqtt_message = "empty"

# Takes the mqtt message list and sends it to the ThingsBoard dashboard.
def send_to_dashboard(mqtt_output_list):
    
    things_board_url = thingsboard_protocol + "://" + thingsboard_address + ":" + thingsboard_port + "/api/v1/" + os.environ['thingsboard_token'] + "/telemetry"   # using device env. variable to provide the token

    # Store robot information in dictionary
    output_dict = {}
    i = 0
    while i < len(mqtt_output_list) and i < len(thingsboard_entities):
        output_dict[thingsboard_entities[i]] = mqtt_output_list[i]
        i += 1

    # Send values to dashboard as json file
    requests.post(things_board_url, data=json.dumps(output_dict) , headers = thingsboard_headers)

# Removes unwanted characters from the mqtt message and packs it into a list.
def format_raw_input(raw_mqtt_input):
    # Remove unwanted characters
    raw_mqtt_input = re.sub("[^0123456789\-\.\:]","",str(raw_mqtt_input))

    # Separate raw input and store it in a list
    mqtt_output_list = [""]

    index = 0
    for character in raw_mqtt_input:
        if character == ":":
            index = index + 1
            mqtt_output_list.append("")
        else:
            mqtt_output_list[index] = mqtt_output_list[index] + character

    # Remove the first entry as it doesn't contain any information
    del mqtt_output_list[0]

    return mqtt_output_list

# Callback function for when a new mqtt message is received
def on_message_callback(client, userdata, message):
    #print("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
    
    # Read mqtt stream from robot and store it
    global current_mqtt_message
    current_mqtt_message = str(message.payload)



# Main program
mqtt_client.on_message = on_message_callback
mqtt_client.loop_start()        # let client check for new updates automatically

running = True
while running:
    # Send current mqtt message to ThingsBoard
    print("Subscribed to mqtt broker " + str(mqtt_broker_address) + ":" + str(mqtt_broker_port) + ", T:" + str(mqtt_broker_topic))
    print("Sending mqtt data to ThingsBoard on " + str(thingsboard_address))
    formatted_mqtt_data = format_raw_input(current_mqtt_message)
    send_to_dashboard(formatted_mqtt_data)

    time.sleep(thingsboard_update_interval)

mqtt_client.loop_stop()
mqtt_client.disconnect()