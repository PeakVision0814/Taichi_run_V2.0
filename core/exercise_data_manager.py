"""
exercise_data_manager.py
Exercise Data Management Module
==============================
This module provides functionalities to save, load, and manage exercise session data, 
including saving data to CSV files, loading data from CSV files, and generating 
previews of historical exercise records for display in user interfaces.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-10
Last Modified: 2025-03-17
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""
import csv
import os
import time
import datetime

DATA_FOLDER = "data"

def save_exercise_data(filename, session_data, level, lap_distance, age, exercise_duration_seconds, laps_completed, exercise_distance): 

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    filepath = os.path.join(DATA_FOLDER, filename)
    try:
        with open(filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Second", "HeartRate", "Level", "LapDistance", "Age", "Duration(seconds)", "Laps", "Distance(meters)"])
            elapsed_seconds = 0
            for timestamp, heart_rate in session_data:
                elapsed_seconds += 1
                csv_writer.writerow([elapsed_seconds, heart_rate, level, lap_distance, age, exercise_duration_seconds, laps_completed, exercise_distance]) 
        print(f"运动数据成功保存到: {filepath}")
    except Exception as e:
        print(f"保存运动数据到 CSV 文件时出错: {e}")


def load_exercise_data(filename):
    filepath = os.path.join(DATA_FOLDER, filename)
    try:
        with open(filepath, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)
            data = []
            for row in csv_reader:
                if row:
                    data.append(row)
            return data
    except FileNotFoundError:
        print(f"文件未找到: {filepath}")
        return None
    except Exception as e:
        print(f"加载运动数据时出错: {e}")
        return None


def get_history_record_previews():
    if not os.path.exists(DATA_FOLDER):
        return []

    preview_data = []
    filenames = [f for f in os.listdir(DATA_FOLDER) if f.startswith("heart_rate_log_") and f.endswith(".csv")]
    for filename in filenames:
        filepath = os.path.join(DATA_FOLDER, filename)
        try:
            with open(filepath, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                header = next(csv_reader)
                first_data_row = next(csv_reader, None)
                if first_data_row:
                    level_index = header.index("Level") if "Level" in header else -1
                    lap_distance_index = header.index("LapDistance") if "LapDistance" in header else -1
                    age_index = header.index("Age") if "Age" in header else -1
                    duration_index = header.index("Duration(seconds)") if "Duration(seconds)" in header else -1
                    distance_index = header.index("Distance(meters)") if "Distance(meters)" in header else -1

                    level = first_data_row[level_index] if level_index != -1 and len(first_data_row) > level_index else "N/A"
                    lap_distance = first_data_row[lap_distance_index] if lap_distance_index != -1 and len(first_data_row) > lap_distance_index else "N/A"
                    age = first_data_row[age_index] if age_index != -1 and len(first_data_row) > age_index else "N/A"
                    duration_seconds = first_data_row[duration_index] if duration_index != -1 and len(first_data_row) > duration_index else "N/A"
                    exercise_distance = first_data_row[distance_index] if distance_index != -1 and len(first_data_row) > distance_index else "N/A"

                    datetime_str_from_filename = filename[len("heart_rate_log_"): -len(".csv")]
                    try:
                        datetime_obj = datetime.datetime.strptime(datetime_str_from_filename, "%Y%m%d-%H%M%S")
                        formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        formatted_datetime = "日期时间解析失败"

                    preview_data.append({
                        "filename": filename,
                        "datetime": formatted_datetime,
                        "level": level,
                        "lap_distance": lap_distance,
                        "age": age,
                        "duration_seconds": duration_seconds, 
                        "exercise_distance": exercise_distance, 
                    })
        except Exception as e:
            print(f"读取文件 {filename} 预览信息时出错: {e}")

    def get_datetime_from_filename(item):
        filename_datetime_str = item['filename'][len("heart_rate_log_"): -len(".csv")]
        try:
            return datetime.datetime.strptime(filename_datetime_str, "%Y%m%d-%H%M%S")
        except ValueError:
            return datetime.datetime.min

    preview_data_sorted = sorted(preview_data, key=get_datetime_from_filename, reverse=True)
    return preview_data_sorted


if __name__ == '__main__':
    test_filename = "heart_rate_log_test.csv"
    test_session_data = [
        (time.time(), 70),
        (time.time() + 1, 72),
        (time.time() + 2, 75),
    ]
    test_level = "5"
    test_lap_distance = 200
    test_age = 30
    test_duration = 600
    test_laps = 3
    test_exercise_distance = 1500

    save_exercise_data(test_filename, test_session_data, test_level, test_lap_distance, test_age, test_duration, test_laps, test_exercise_distance)

    loaded_data = load_exercise_data(test_filename)
    if loaded_data:
        print("\n加载的数据:")
        for row in loaded_data:
            print(row)

    preview_info = get_history_record_previews()
    if preview_info:
        print("\n历史记录预览信息:")
        for preview in preview_info:
            print(preview)
