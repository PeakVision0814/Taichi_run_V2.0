"""
Treadmill APP
==================
This module provides a GUI interface.
Author: Gaopeng Huang; Hui Guo
Email: perished_hgp@163.com; gh1848026781@163.com
Date Created: 2025-03-06
Last Modified: 2025-03-06
Version: 2.0.0
Copyright (c) 2025 PeakVision
All rights reserved.
This software is released under the GNU GENERAL PUBLIC LICENSE, see LICENSE for more information.
"""

import tkinter as tk
from tkinter import ttk
from treadmill_controller import TreadmillController

class TreadmillApp:
    def __init__(self, root):
        self.root = root
        self._configure_root()
        self.main_frame = self._create_main_frame()
        self.level_combo = self._create_level_selection()
        self.age_entry = self._create_age_entry()
        self.target_type_combo = self._create_target_type_selection()
        self.target_entry = self._create_target_entry()
        self.start_button, self.stop_button = self._create_control_buttons()
        self.heart_rate_label = self._create_status_label("当前心率：","0 bpm",5)
        self.speed_label = self._create_status_label("当前速率：","0 km/h",6)
        self.time_label = self._create_status_label("运动时间：","0 秒",7)
        self.distance_label = self._create_status_label("运动距离：","0 m",8)
        self.lap_label = self._create_status_label("当前圈程：","0",9)
        self.controller = None
        self.goal_reached_dialog = None

    def _configure_root(self):
        self._set_root_title("智能太极跑系统")
        self._set_root_geometry("350x450")
        self._set_root_resizable(False, False)
        self._set_root_protocol("WM_DELETE_WINDOW",
                                self.on_closing)

    def _set_root_title(self,title):
        self.root.title(title)

    def _set_root_geometry(self,geometry):
        self.root.geometry(geometry)

    def _set_root_resizable(self,width,height):
        self.root.resizable(width,height)

    def _set_root_protocol(self,protocol,command):
        self.root.protocol(protocol,command)

    def _create_main_frame(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)
        return main_frame

    def _create_level_selection(self):
        self._create_label(self.main_frame,"选择等级：",0,0)
        level_var = tk.StringVar()
        level_combo = self._create_combobox(self.main_frame,level_var,[str(i) for i in range(2, 11)],
                                            0,
                                            1)
        level_combo.bind("<<ComboboxSelected>>",
                         self.on_level_selected)
        return level_combo

    def _create_label(self,
                      parent,
                      text,
                      row,
                      column,
                      sticky='e',
                      padx=10,
                      pady=10):
        tk.Label(parent,text=text,anchor=sticky).grid(row=row,
                                     column=column,
                                     padx=padx,
                                     pady=pady,
                                     sticky=sticky)

    def _create_combobox(self,
                         parent,
                         textvariable,
                         values,
                         row,
                         column,
                         sticky='w',
                         padx=10,
                         pady=10):
        combo = ttk.Combobox(parent,
                             textvariable=textvariable,
                             values=values)
        combo.grid(row=row,
                   column=column,
                   padx=padx,
                   pady=pady,
                   sticky=sticky)
        return combo

    def _create_age_entry(self):
        self._create_label(self.main_frame,
                           "年龄：",
                           1,
                           0)
        age_entry = tk.Entry(self.main_frame)
        age_entry.grid(row=1,
                       column=1,
                       padx=10,
                       pady=10,
                       sticky='w')
        return age_entry

    def _create_target_type_selection(self):
        self._create_label(self.main_frame,
                           "选择目标类型：",2,0)
        target_type_var = tk.StringVar(value="无目标")
        target_type_combo = self._create_combobox(self.main_frame, target_type_var, ["无目标", 
                                                                                     "距离（米）", 
                                                                                     "时间（秒）", 
                                                                                     "心率（bpm）"], 
                                                                                     2, 
                                                                                     1)
        target_type_combo.bind("<<ComboboxSelected>>",
                               self.update_target_entry)
        return target_type_combo

    def _create_target_entry(self):
        self.target_label = self._create_label(self.main_frame,"目标：",3,0)
        target_entry = tk.Entry(self.main_frame)
        target_entry.grid(row=3,
                          column=1,
                          padx=10,
                          pady=10,
                          sticky='w')
        self._disable_entry(target_entry)
        return target_entry

    def _disable_entry(self,
                       entry):
        entry.config(state=tk.DISABLED)

    def _enable_entry(self,entry):
        entry.config(state=tk.NORMAL)

    def _create_control_buttons(self):
        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=4,column=0,columnspan=2,pady=10)
        start_button = self._create_button(button_frame, 
                                           "开始运动", 
                                           self.start_workout, 
                                           side=tk.LEFT)
        stop_button = self._create_button(button_frame, 
                                          "停止运动", 
                                          self.stop_workout, 
                                          side=tk.LEFT, 
                                          state=tk.DISABLED)
        return start_button, stop_button

    def _create_button(self,parent,text,command,side=tk.LEFT,padx=5,state=tk.NORMAL):
        button = tk.Button(parent,text=text,command=command,state=state)
        
        button.pack(side=side,padx=padx)
        return button

    def _create_status_label(self,text,initial_value,row):
        self._create_label(self.main_frame,text,row,0)
        status_label = tk.Label(self.main_frame,text=initial_value)
        status_label.grid(row=row,
                          column=1,
                          padx=10,
                          pady=10,
                          sticky='w'
        )
        return status_label

    def on_level_selected(self,event):
        level = self.level_combo.get()
        default_targets = self._get_default_targets()
        if level in default_targets:
            self._update_target_input("距离（米）",default_targets[level])
        else:
            self.update_target_entry(None)

    def _get_default_targets(self):
        return {
            "2": 4000,
            "3": 4200,
            "4": 4600,
            "5": 5000,
            "6": 5200,
            "7": 5200,
            "8": 5400,
            "9": 5400,
            "10": 5400
        }

    def _update_target_input(self,target_type,value):
        self.target_type_combo.set(target_type)
        self._enable_entry(self.target_entry)
        self._clear_and_set_entry(self.target_entry,value)

    def _clear_and_set_entry(self,entry,value):
        entry.delete(0,tk.END)
        entry.insert(0,str(value))

    def update_target_entry(self,event):
        target_type = self.target_type_combo.get()
        self._update_target_label_and_entry(target_type)

    def _update_target_label_and_entry(self,target_type):
        if target_type == "距离（米）":
            self._set_target_label_text("目标：")
            self._enable_entry(self.target_entry)
        elif target_type == "时间（秒）":
            self._set_target_label_text("目标：")
            self._enable_entry(self.target_entry)
        elif target_type == "无目标":
            self._set_target_label_text("目标：")
            self._disable_entry(self.target_entry)
        elif target_type == "心率（bpm）":
            self._set_target_label_text("目标：")
            self._enable_entry(self.target_entry)

    def _set_target_label_text(self,text):
        self.target_label.config(text=text)

    def start_workout(self):
        age, level = self._get_user_inputs()
        if age is None or level is None:
            return
        target_distance,max_time, target_heart_rate = self._determine_targets()
        self._initialize_controller(age,
                                    level,
                                    target_distance,
                                    max_time,
                                    target_heart_rate
                                    )
        self._update_button_states(start_running=True)

    def _get_user_inputs(self):
        age = self._get_age()
        level = self._get_level()
        return age, level

    def _get_age(self):
        try:
            age = int(self.age_entry.get())
            if 1 <= age <= 120:
                return age
            raise ValueError
        except ValueError:
            self._show_warning("请输入有效的年龄（1-120）")
            return None

    def _get_level(self):
        try:
            return int(self.level_combo.get())
        except ValueError:
            self._show_warning("请正确填写等级")
            return None

    def _determine_targets(self):
        target_type = self.target_type_combo.get()
        target_value = self.target_entry.get()
        if target_type != "无目标" and not target_value.isdigit():
            self._show_warning(
                "请正确填写目标值"
                )
            return None, None, None
        return self._assign_targets(
            target_type,int(target_value))

    def _assign_targets(self,target_type,target_value):
        if target_type == "距离（米）":
            return target_value, None, None
        elif target_type == "时间（秒）":
            return None, target_value, None
        elif target_type == "心率（bpm）":
            return None, None, target_value
        return None, None, None

    def _initialize_controller(
            self,
            age, 
            level, 
            target_distance, 
            max_time, 
            target_heart_rate):
        self.controller = TreadmillController(
            age, 
            level, 
            target_distance, 
            max_time, 
            target_heart_rate,
            update_callback=self.update_status,
            goal_reached_callback=self.show_goal_reached_dialog)
        self.controller.start()

    def stop_workout(self):
        self._stop_controller()
        self._destroy_goal_reached_dialog()
        self._update_button_states(start_running=False)

    def _stop_controller(self):
        if self.controller:
            self.controller.stop()
            self.controller = None

    def _destroy_goal_reached_dialog(self):
        if self.goal_reached_dialog:
            self.goal_reached_dialog.destroy()
            self.goal_reached_dialog = None

    def _update_button_states(self,start_running):
        if start_running:
            self._disable_button(self.start_button)
            self._enable_button(self.stop_button)
        else:
            self._enable_button(self.start_button)
            self._disable_button(self.stop_button)

    def _disable_button(self,button):
        button.config(state=tk.DISABLED)

    def _enable_button(self,button):
        button.config(state=tk.NORMAL)

    def show_goal_reached_dialog(self):
        self.goal_reached_dialog = tk.Toplevel(self.root)
        self.goal_reached_dialog.title("目标达成")
        self.goal_reached_dialog.geometry("300x150")
        tk.Label(self.goal_reached_dialog,text="目标达成，运动已结束！").pack(pady=20)
        self._create_goal_dialog_buttons()

    def _create_goal_dialog_buttons(self):
        button_frame = tk.Frame(self.goal_reached_dialog)
        button_frame.pack(pady=10)
        self._create_continue_button(button_frame)
        self._create_stop_button(button_frame)
        
    def _create_continue_button(self,button_frame):
        continue_button = tk.Button(button_frame,
            text="继续运动",
            command=self.on_goal_reached_dialog_continue
            )
        continue_button.pack(side=tk.LEFT,padx=10)

    def _create_stop_button(self,button_frame):
        stop_button = tk.Button(button_frame,
                                text="停止运动",
                                command=self.on_goal_reached_dialog_stop
                                )
        stop_button.pack(side=tk.LEFT,
                         padx=10
                         )

    def on_goal_reached_dialog_continue(self):
        self.goal_reached_dialog.destroy()
        if self.controller:
            self._reset_controller_goals()
            self.controller.resume()

    def _reset_controller_goals(self):
        self.controller.target_distance = None
        self.controller.max_time = None
        self.controller.target_heart_rate = None

    def on_goal_reached_dialog_stop(self):
        self.goal_reached_dialog.destroy()
        self.stop_workout()

    def update_status(self, message):
        if "心率" in message:
            # 直接解析并更新心率标签
            self.heart_rate_label.config(text=message.split(": ")[1])
        else:
            # 直接拆分消息并更新多个状态标签
            parts = message.split(", ")
            if len(parts) >= 3:
                speed_part, distance_part, duration_part = parts[:3]
                self.speed_label.config(text=speed_part.split(": ")[1])
                self.distance_label.config(text=distance_part.split(": ")[1])
                self.time_label.config(text=duration_part.split(": ")[1])    

    def _parse_status_message(self,message):
        return message.split(", ")

    def _update_status_labels(self,
                              speed,
                              distance,
                              time):
        self._update_speed_label(speed)
        self._update_distance_label(distance)
        self._update_time_label(time)
        self._update_lap_label(distance)

    def _update_speed_label(self,speed):
        self.speed_label.config(text=speed.split(": ")[1])

    def _update_distance_label(self,
                               distance
                               ):
        self.distance_label.config(text=distance.split(": ")[1])

    def _update_time_label(self,
                           time):
        self.time_label.config(text=time.split(": ")[1])

    def _update_lap_label(self,distance):
        distance_covered = float(
            distance.split(": ")[1].split(" ")[0]
            )
        laps = int(distance_covered // 200) + 1
        self.lap_label.config(text=str(laps))

    def _show_warning(self,message):
        warning_window = self._create_warning_window("警告","200x100")
        self._create_warning_label(warning_window,
                                   message)
        self._create_warning_button(warning_window,"确定")

    def _create_warning_window(self,title,geometry):
        warning_window = tk.Toplevel(self.root)
        warning_window.title(title)
        warning_window.geometry(geometry)
        return warning_window

    def _create_warning_label(self,
                              window,
                              message
                              ):
        tk.Label(window,
                 text=message).pack(pady=20)

    def _create_warning_button(self,
                               window,
                               text):
        tk.Button(window,
                  text=text,
                  command=window.destroy
                  ).pack()

    def on_closing(self):
        self._stop_controller()
        self.root.destroy()