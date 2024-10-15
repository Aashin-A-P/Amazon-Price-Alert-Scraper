from bs4 import BeautifulSoup
import requests
import smtplib
import time
import datetime
import random
import streamlit as st
import csv
import os
import threading
import pandas as pd


def send_mail(email_id, product_name, current_price):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("apaashin@gmail.com", "qupm xsyd nsgy aciz")

    subject = "Price Alert: Your Product"
    body = (f"The price of the product '{product_name}' has dropped below your threshold.\n"
            f"Current price: ₹{current_price}")

    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("apaashin@gmail.com", email_id, msg.encode('utf-8'))
    print("Email sent successfully")
    server.quit()



def checkprice(URL, email_id, threshold):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Linux; Android 8.1.0; SM-J530F Build/M1AJQ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.90 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    ]

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': random.choice(user_agents),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    start_time = datetime.datetime.now()  # Track when the tracker started
    max_duration = datetime.timedelta(weeks=2)  # 2 weeks

    while True:

        try:
            elapsed_time = datetime.datetime.now() - start_time
            if elapsed_time > max_duration:
                print("Tracking period of 2 weeks is over. Stopping tracker.")
                break
            page = requests.get(URL, headers=headers)
            Soup1 = BeautifulSoup(page.content, "html.parser")
            page.encoding = 'utf-8'
            title = Soup1.find(id='productTitle').get_text().strip()
            price = Soup1.find('span', class_='a-price-whole').get_text().strip()

            if title is None or price is None:
                raise AttributeError("Could not find the product title or price.")

            price2 = int(''.join(filter(str.isdigit, price)))

            # Log data to CSV
            today = datetime.date.today()
            if not os.path.isfile('AmazonWebScraperData.csv'):
                with open('AmazonWebScraperData.csv', 'w', newline='', encoding="UTF8") as f:
                    writer = csv.writer(f)
                    writer.writerow(['email_id', 'title', 'price', 'date'])

            with open('AmazonWebScraperData.csv', 'a+', newline='', encoding="UTF8") as f:
                writer = csv.writer(f)
                writer.writerow([email_id, title, price2, today])

            if price2 <= threshold:
                send_mail(email_id,title,price2)
            time.sleep(84600)

        except AttributeError as e:
            print(f"{e}. Retrying immediately...")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def dashboard_view(email_id):
    try:
        if os.path.isfile('AmazonWebScraperData.csv'):
            df = pd.read_csv('AmazonWebScraperData.csv')

            # Print column names to debug
            st.write("CSV Columns:", df.columns)

            # Filter by the provided email ID
            user_data = df[df['email_id'] == email_id]

            if not user_data.empty:
                st.write(f"Tracking history for {email_id}:")
                st.dataframe(user_data, use_container_width=True)
            else:
                st.warning("No tracking data found for this email.")
        else:
            st.warning("No tracking data available.")
    except KeyError as e:
        print("KeyError")

            
def main():
    st.title("Amazon Price Tracker")

    email_id = st.text_input("Enter Your Email ID to View Tracking History")
    if st.button("View History"):
        if email_id:
            dashboard_view(email_id)
        else:
            st.error("Please enter your email ID.")

    url = st.text_input("Enter Product URL")
    threshold = st.number_input("Enter Price Threshold", min_value=0)
    email_id = st.text_input("Enter Your Email ID")

    if st.button("Start Tracking"):
        if url and threshold and email_id:
            # Create a thread for the price tracking
            tracking_thread = threading.Thread(target=checkprice, args=(url, email_id, threshold))
            tracking_thread.daemon = True  # Allows the thread to exit when the main program exits
            tracking_thread.start()
            st.success("Started tracking the price. You'll receive an email when it drops below your threshold for the next 2 weeks.")
        else:
            st.error("Please fill all fields.")


if __name__ == "__main__":
    main()
