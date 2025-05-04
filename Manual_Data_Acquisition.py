# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 14:02:52 2025

@author: Administrator
"""

import csv
from datetime import datetime, timedelta
import calendar

def get_month_days(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    year = start_date.year
    month = start_date.month
    num_days = calendar.monthrange(year, month)[1]
    return [start_date.replace(day=day) for day in range(1, num_days + 1)]

def collect_data_for_month(start_date_str):
    all_data = []
    month_days = get_month_days(start_date_str)
    
    for day in month_days:
        print(f"\nEnter data for {day.strftime('%d-%m-%Y')}:")
        for hour in range(6, 18):  # Hours 06 to 17 inclusive
            while True:
                try:
                    value = input(f"  Hour {hour:02d}: ")
                    all_data.append({
                        "Date": day.strftime("%d-%m-%Y"),
                        "Hour": f"{hour:02d}",
                        "Value": value
                    })
                    break
                except Exception as e:
                    print("Invalid input. Please try again.")
    
    return all_data

def save_to_csv(data, filename="monthly_data.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "Hour", "Value"])
        writer.writeheader()
        writer.writerows(data)
    print(f"\nData saved to {filename}")

if __name__ == "__main__":
    start_date = input("Enter the start date (DD-MM-YYYY): ")
    data = collect_data_for_month(start_date)
    save_to_csv(data)
