import os
import smtplib
import time
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import plotly.express as px
import requests

MY_LAT = 47.700648
MY_LONG = 19.289358

my_email = os.environ["EMAIL"]
password = os.environ["PASS"]
counter = 0

# Your position is within +5 or -5 degrees of the ISS position.

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

df = pd.DataFrame(columns=['DateTime', 'Latitude', 'Longitude'])


def send_simple_email():
    with smtplib.SMTP_SSL("smtp.gmail.com") as connection:
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs="szabo.gergo.bme@gmail.com",
            msg=f"Subject:ISS position such wow\n\n{img}")


def send_email_with_img():
    sender_email = my_email
    sender_password = password
    recipient_email = "szabo.gergo.bme@gmail.com"
    subject = "ISS position such wow"
    body = "Behold the position of the ISS attached"

    image_part = MIMEImage(img)
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    html_part = MIMEText(body)
    message.attach(html_part)
    message.attach(image_part)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())


# If the ISS is close to my current position
# and it is currently dark
# Then send me an email to tell me to look up.
# BONUS: run the code every 60 seconds.

while True:
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    iss_position = [{'DateTime': datetime.now(), 'Latitude': iss_latitude, 'Longitude': iss_longitude}]

    df = df.append(pd.DataFrame(iss_position))
    print(df)

    if MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and MY_LONG - 5 <= iss_longitude <= MY_LONG + 5:
        if time_now.hour >= sunset + 1 or time_now.hour <= sunrise - 1:
            with smtplib.SMTP_SSL("smtp.gmail.com") as connection:
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs="szabo.gergo.bme@gmail.com",
                    msg=f"Subject:Look up -> ISS over your head!\n\n:)")
    else:
        color_scale = [(0, 'orange'), (1, 'red')]
        fig = px.scatter_mapbox(df,
                                lat="Latitude",
                                lon="Longitude",
                                hover_name="DateTime",
                                hover_data=["DateTime"],
                                color="Latitude",
                                color_continuous_scale=color_scale,
                                zoom=1,
                                height=800,
                                width=800)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        # fig.show()
        # fig.show(renderer="png")
        img = fig.to_image()

        counter = counter + 1

        if counter % 60 == 0:
            send_email_with_img()
    time.sleep(60)
