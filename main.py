import os
import smtplib
import time

import requests
from datetime import datetime

MY_LAT = 47.700648
MY_LONG = 19.289358

my_email = os.environ["EMAIL"]
password = os.environ["PASS"]

response = requests.get(url="http://api.open-notify.org/iss-now.json")
response.raise_for_status()
data = response.json()

iss_latitude = float(data["iss_position"]["latitude"])
iss_longitude = float(data["iss_position"]["longitude"])

#Your position is within +5 or -5 degrees of the ISS position.

parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}

response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
response.raise_for_status()
data = response.json()
sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

time_now = datetime.now()

#If the ISS is close to my current position
# and it is currently dark
# Then send me an email to tell me to look up.
# BONUS: run the code every 60 seconds.

while True:
    if MY_LAT-5 <= iss_latitude <= MY_LAT+5 and MY_LONG - 5 <= iss_longitude <= MY_LONG + 5:
        if time_now.hour >= sunset + 1 or time_now.hour <= sunrise - 1:
            with smtplib.SMTP_SSL("smtp.gmail.com") as connection:
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs="szabo.gergo.bme@gmail.com",
                    msg=f"Subject:Look up -> ISS over your head!\n\n:)")
    time.sleep(60)

