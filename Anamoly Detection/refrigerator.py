import math, json, time, conf, statistics
from boltiot import Bolt, Sms

min_limit = 10
max_limit = 100

mybolt = Bolt(conf.API_KEY, conf.device_id)
sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)

def compute_bounds( history_data, frame_size, factor):
      if len(history_data) < frame_size:
            return None
      if len(history_data) > frame_size:
            del history_data[0:len(history_data) - frame_size]
            
      Mean_value = statistics.mean(history_data)
      Variance = 0
      for data in history_data:
            Variance += math.pow((data - Mean_value), 2)
            
      Zn = factor * math.sqrt(Variance/frame_size)
      High_bound = history_data[frame_size-1] + Zn
      Low_bound = history_data[frame_size-1] - Zn
      return [High_bound, Low_bound]
      
history_data = []

while True:
      print("Reading sensor value: ")
      response = mybolt.analogRead('A0')
      data = json.loads(response)
      print("Sensor Value is: " + str(data["value"]))
      temperature = (100 * int(data['value']))/ 1024        #to convert the temperature in degree Celcious
      print("Temperature is ", temperature)
      
      try:
            sensor_value = int(data['value'])
      except e:
            print("There was an error in parsing the response: ", e)
            continue
      
      bound = compute_bounds(history_data, conf.Frame_size, conf.Mul_factor)
      if not bound:
            required_data_count = conf.Frame_size - len(history_data)
            print("Not enough data to compute the Z-Score, Need ", required_data_count," more points")
            history_data.append(int(data['value']))
            time.sleep(20)
            continue
      
      #this portion of the code can be changed as per your use
      
      try:
            if sensor_value > min_limit and sensor_value < max_limit:
                print("Warning!!!")
                print("Making request to Twilio to send SMS")
                response = sms.send_sms("The Current temperature is: "+str(sensor_value)+\
                          ". Someone has openned the door of the refridgerator.")
                print("Response received from Twilio is : "+str(response))
                print("Status of SMS at Twilio is: "+str(response.status))
               
      except Exception as e:
            print("Error Occured")
            print(e)
            
      time.sleep(20)
