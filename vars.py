# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# VARIABLES 
# from vars import heartratedata, sleepdata, timepointdata, stepdata, lookdata
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

heartratedata = "data/heartrate.json"
# this is 24 hours of heart-rate sampled on average every 2.76 seconds
# time has the format "19:14:00" "%H:%M:%S"
# appears to be UTC/GMT! Do we wnt to transform to local time? YES

# [{
#   "time" : "08:00:07",
#   "value" : {
#     "bpm" : 78,
#     "confidence" : 2
#   }
# }

sleepdata = "data/sleep.json"

lookdata = "data/amazon.csv"


timepointdata = "data/locations.csv"
# Start Time,End Time,Name,Latitude,Longitude
# lat/lng has been transformed and spoofed for Northern CA
# ten days were compressed into one for variety. 

stepdata = "data/steps_monday.json"
# datetime has the format "Tue 19:14:00" "%a %H:%M:%S"
# appears to be UTC/GMT

# [{
#   "dateTime" : "Sat 08:03:00",
#   "value" : "0"
# },


