"""FLC Analyzer GUI module"""

import os
import csv
import tkinter as tk
from tkinter import colorchooser
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from data_manager import DataManager
from scope import Scope


class FLCAnalyzer(tk.Tk):
    """
    Graphical user interfance (GUI) to FLC 
    (ferroelectric liquid crystals) analysis.

    This class reads data from CSV or downloads it through 
    Scope class, handles them through DataManager class and visualize data.
    
    Default parameters (like voltage, thickness, area etc.) are initiated 
    on startup, but they may be changed by the user.

    Attributes
    ----------
    data_manager : DataManager
        Manages data.
    scope : Scope
        Can connect to oscilloscope and download data from it.
    ax : matplotlib.axes.Axes
        Chart object visualizing data.
    canvas : FigureCanvasTkAgg
        Canvas that enables to display chart on GUI.
    toolbar : NavigationToolbar2Tk
        Chart toolbar that enables to modify chart's view.
    Various tkinter widgets.

    Methods
    -------
    validate_entry(text)
        Entry input validator that validates only numeric values.
    validate_tilt_angle(text)
        Entry tilt validator only validates values between 1 and 89.
    change_values(self, *args)
        Changes values in regions if new data is loaded
        or input params are changed.
    choose_color(param)
        Changes graph color according to passed parameter and
        updates graph.
    update_alpha(*args)
        Updates alpha values when scale is changed then updates graph.
    on_click(event)
        Derives x, y coords of mouse click then updates right panels
        if data is loaded.
    load_data_from_scope()
        Tries to get time and voltage data from oscilloscope
        through local network, passes them to data manager and
        draws graph.
    load_data_from_file()
        Tries to get time and voltage data from csv file
        passes them to data manager and draws graph.
    draw_plot(time, voltage)
        Clears graph, marks regions and points and draws new graph
    mark_regions(self)
        Clears all existing rectangles then draws new one.
    mark_points(self)
        Clears all existing points then draws new one.
    update_right_panels(x)
        Clears entries on right panel then writes new values.
    update_bottom_left_panel()
        Clears entries on left panel then writes new values.
    """
    def __init__(self):
        """
        Inits main window of FLC Analyzer app.

        Creates all GUI components, sets default parameters, inits
        DataManager and Scope classes, configures chart and sets
        events (like clicks or input changes).
        """
        # init gui, data manager and scope
        super().__init__()
        self.title("FLC analyzer")    # give a title
        self.resizable(False, False)  # disable resizing
        self.data_manager = DataManager()
        self.scope = Scope()

        # declare default strings for entries
        self.u_in_string = tk.StringVar(value="10.0")
        self.d_string = tk.StringVar(value="3.0")
        self.S_string = tk.StringVar(value="100.0")
        self.C_string = tk.StringVar(value="30.0")
        self.t_ang_string = tk.StringVar(value="45.0")

        # declare default colors for graph
        self.plot_color = tk.StringVar(value="000000")
        self.inc_region_color = tk.StringVar(value="#8FF0A4")
        self.dec_region_color = tk.StringVar(value="#F66151")
        self.knee_point_color = tk.StringVar(value="#C64600")
        self.t40_60_points_color = tk.StringVar(value="#1A5FB4")

        self.inc_alpha_region = 0.1
        self.dec_alpha_region = 0.1

        # create main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # left top sector
        left_top_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        left_top_frame.grid(
            row=0, column=0, padx=5, pady=5, sticky="nsew"
        )

        tk.Label(left_top_frame, text="IP Address").pack(
            fill=tk.BOTH, expand=True
        )
        self.ip_address_entry = tk.Entry(left_top_frame)
        self.ip_address_entry.pack(fill=tk.BOTH, expand=True)

        tk.Label(left_top_frame, text="Channel").pack(
            fill=tk.BOTH, expand=True
        )
        self.channel_entry = tk.Entry(left_top_frame)
        self.channel_entry.pack(fill=tk.BOTH, expand=True)

        load_from_oscil_button = tk.Button(
            left_top_frame, text="Load data from oscilloscope",
            command=self.load_data_from_scope
        )
        load_from_oscil_button.pack(fill=tk.BOTH, expand=True)

        load_from_file_button = tk.Button(
            left_top_frame, text="Load data from file",
            command=self.load_data_from_file
        )
        load_from_file_button.pack(fill=tk.BOTH, expand=True)

        quit_button = tk.Button(
            left_top_frame, text="Quit", command=quit
        )
        quit_button.pack(fill=tk.BOTH, expand=True)

        # left middle sector
        left_middle_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        left_middle_frame.grid(
            row=1, column=0, padx=5, pady=5, sticky="nsew"
        )

        tk.Label(left_middle_frame, text="Input Voltage (o-p):").grid(
            row=0, column=0, padx=5, pady=0, sticky="w"
        )
        input_voltage_entry = tk.Entry(
            left_middle_frame, validate="key",
            validatecommand=(self.register(self.validate_entry), "%P"),
            textvariable=self.u_in_string
        )
        input_voltage_entry.grid(
            row=1, column=0, padx=5, pady=0, sticky="w"
        )
        self.u_in_string.trace_add("write", self.change_values)

        tk.Label(left_middle_frame, text="V").grid(
            row=1, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(left_middle_frame, text="Thickness:").grid(
            row=2, column=0, padx=5, pady=0, sticky="w"
        )
        thickness_entry = tk.Entry(
            left_middle_frame, validate="key",
            validatecommand=(self.register(self.validate_entry), "%P"),
            textvariable=self.d_string
        )
        thickness_entry.grid(row=3, column=0, padx=5, pady=0, sticky="w")
        self.d_string.trace_add("write", self.change_values)

        tk.Label(left_middle_frame, text="μm").grid(
            row=3, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(left_middle_frame, text="Area:").grid(
            row=4, column=0, padx=5, pady=0, sticky="w"
        )
        area_entry = tk.Entry(
            left_middle_frame, validate="key",
            validatecommand=(self.register(self.validate_entry), "%P"),
            textvariable=self.S_string
        )
        area_entry.grid(row=5, column=0, padx=5, pady=0, sticky="w")
        self.S_string.trace_add("write", self.change_values)

        tk.Label(left_middle_frame, text="mm^2").grid(
            row=5, column=1, padx=0, pady=0,sticky="w"
        )

        tk.Label(left_middle_frame, text="Capacitance:").grid(
            row=6, column=0, padx=5, pady=0, sticky="w"
        )
        capacitance_entry = tk.Entry(
            left_middle_frame, validate="key",
            validatecommand=(self.register(self.validate_entry), "%P"),
            textvariable=self.C_string
        )
        capacitance_entry.grid(
            row=7, column=0, padx=5, pady=0, sticky="w"
        )
        self.C_string.trace_add("write", self.change_values)

        tk.Label(left_middle_frame, text="nF").grid(
            row=7, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(left_middle_frame, text="Tilt angle:").grid(
            row=8, column=0, padx=5, pady=0, sticky="w"
        )
        tilt_angle_entry = tk.Entry(
            left_middle_frame, validate="key",
            validatecommand=(self.register(self.validate_tilt_angle), "%P"),
            textvariable=self.t_ang_string
        )
        tilt_angle_entry.grid(
            row=9, column=0, padx=5, pady=0, sticky="w"
        )
        self.t_ang_string.trace_add("write", self.change_values)

        tk.Label(left_middle_frame, text="°").grid(
            row=9, column=1, padx=0, pady=0, sticky="w"
        )

        # left bottom sector
        left_bottom_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        left_bottom_frame.grid(
            row=2, column=0, padx=5, pady=5, sticky="nsew"
        )

        tk.Label(left_bottom_frame, text="Spontaneous polarization:").grid(
            row=0, column=0, padx=5, pady=0, sticky="w"
        )
        self.ps_entry = tk.Entry(left_bottom_frame)
        self.ps_entry.grid(
            row=1, column=0, padx=5, pady=0, sticky="w"
        )
        self.ps_entry.config(state="readonly")
        tk.Label(left_bottom_frame, text="nC/cm^2").grid(
            row=1, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(left_bottom_frame, text="Rotational viscosity:").grid(
            row=2, column=0, padx=5, pady=0, sticky="w"
        )
        self.rv_entry = tk.Entry(left_bottom_frame)
        self.rv_entry.grid(
            row=3, column=0, padx=5, pady=0, sticky="w"
        )
        self.rv_entry.config(state="readonly")
        tk.Label(left_bottom_frame, text="P").grid(
            row=3, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(left_bottom_frame, text="Dielectric anisotropy:").grid(
            row=4, column=0, padx=5, pady=0, sticky="w"
        )
        self.da_entry = tk.Entry(left_bottom_frame)
        self.da_entry.grid(
            row=5, column=0, padx=5, pady=0, sticky="w"
        )
        self.da_entry.config(state="readonly")
        tk.Label(left_bottom_frame, text="").grid(
            row=5, column=1, padx=0, pady=0, sticky="w"
        )

        # middle sector
        middle_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=0
        )
        middle_frame.grid(
            row=0, column=1, rowspan=3, padx=5, pady=5, sticky="nsew"
        )

        # create and configure graph
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=middle_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, middle_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # right top sector
        right_top_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        right_top_frame.grid(
            row=0, column=2, padx=5, pady=5, sticky="nsew"
        )

        self.inc_region_alpha_scale = tk.Scale(
            right_top_frame, from_=0, to=100, orient="horizontal",
            label="inc region alpha scale", command=self.update_alpha
        )
        self.inc_region_alpha_scale.set(10)
        self.inc_region_alpha_scale.pack(fill=tk.BOTH, expand=True)

        self.dec_region_alpha_scale = tk.Scale(
            right_top_frame, from_=0, to=100, orient="horizontal",
            label="dec region alpha scale", command=self.update_alpha
        )
        self.dec_region_alpha_scale.set(10)
        self.dec_region_alpha_scale.pack(fill=tk.BOTH, expand=True)

        plot_color_button = tk.Button(
            right_top_frame, text="Choose plot color",
            command=lambda: self.choose_color("plot")
        )
        plot_color_button.pack(fill=tk.BOTH, expand=True)

        inc_region_color_button = tk.Button(
            right_top_frame, text="Choose inc region color",
            command=lambda: self.choose_color("inc")
        )
        inc_region_color_button.pack(fill=tk.BOTH, expand=True)

        dec_region_color_button = tk.Button(
            right_top_frame, text="Choose dec region color",
            command=lambda: self.choose_color("dec")
        )
        dec_region_color_button.pack(fill=tk.BOTH, expand=True)

        knee_point_color_button = tk.Button(
            right_top_frame, text="Choose knee point color",
            command=lambda: self.choose_color("knee")
        )
        knee_point_color_button.pack(fill=tk.BOTH, expand=True)

        t40_60_point_color_button = tk.Button(
            right_top_frame, text="Choose t40-60 color",
            command=lambda: self.choose_color("t4060")
        )
        t40_60_point_color_button.pack(fill=tk.BOTH, expand=True)

        # right middle sector
        right_middle_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        right_middle_frame.grid(
            row=1, column=2, padx=5, pady=5, sticky="nsew"
        )

        tk.Label(right_middle_frame, text="Up:").grid(
            row=0, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_up_entry = tk.Entry(right_middle_frame)
        self.local_up_entry.grid(
            row=1, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_up_entry.config(state="readonly")
        tk.Label(right_middle_frame, text="V").grid(
            row=1, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(right_middle_frame, text="Uc:").grid(
            row=2, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_uc_entry = tk.Entry(right_middle_frame)
        self.local_uc_entry.grid(
            row=3, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_uc_entry.config(state="readonly")
        tk.Label(right_middle_frame, text="V").grid(
            row=3, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(right_middle_frame, text="τ:").grid(
            row=4, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_tau_entry = tk.Entry(right_middle_frame)
        self.local_tau_entry.grid(
            row=5, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_tau_entry.config(state="readonly")
        tk.Label(right_middle_frame, text="μs").grid(
            row=5, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(right_middle_frame, text="α:").grid(
            row=6, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_alpha_entry = tk.Entry(right_middle_frame)
        self.local_alpha_entry.grid(
            row=7, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_alpha_entry.config(state="readonly")

        # right bottom sector
        right_bottom_frame = tk.Frame(
            self.main_frame, relief=tk.RIDGE, borderwidth=2
        )
        right_bottom_frame.grid(
            row=2, column=2,padx=5, pady=5, sticky="nsew"
        )

        tk.Label(right_bottom_frame, text="Spontaneous polarization:").grid(
            row=0, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_ps_entry = tk.Entry(right_bottom_frame)
        self.local_ps_entry.grid(
            row=1, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_ps_entry.config(state="readonly")
        tk.Label(right_bottom_frame, text="nC/cm^2").grid(
            row=1, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(right_bottom_frame, text="Rotational viscosity:").grid(
            row=2, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_rv_entry = tk.Entry(right_bottom_frame)
        self.local_rv_entry.grid(
            row=3, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_rv_entry.config(state="readonly")
        tk.Label(right_bottom_frame, text="P").grid(
            row=3, column=1, padx=0, pady=0, sticky="w"
        )

        tk.Label(right_bottom_frame, text="Dielectric anisotropy:").grid(
            row=4, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_da_entry = tk.Entry(right_bottom_frame)
        self.local_da_entry.grid(
            row=5, column=0, padx=5, pady=0, sticky="w"
        )
        self.local_da_entry.config(state="readonly")

    def validate_entry(self, text):
        """
        Entry input validator that validates only numeric values.

        Parameters
        ----------
        text : str
            Text string derived from input.

        Returns
        -------
        bool
            True if passes validation, False if otherwise.

        Raises
        ------
        ValueError
            If text string is not convertible to float.
        """
        if text == "":
            return True

        try:
            if float(text) == 0.0:
                return False
            else:
                return True
        except ValueError:
            return False

    def validate_tilt_angle(self, text):
        """
        Entry tilt validator only validates values between 1 and 89.

        Parameters
        ----------
        text : str
            Text string derived from input.

        Returns
        -------
        bool
            True if passes validation, False if otherwise.

        Raises
        ------
        ValueError
            If text string is not convertible to float.
        """
        if text == "":
            return True

        try:
            a = float(text)
            if a >= 1.0 and a <= 89.0:
                return True
            else:
                return False
        except ValueError:
            return False

    def change_values(self, *args):
        """
        Changes values in regions if new data is loaded or
        input params are changed.

        Raises
        ------
        ValueError
            If entry input is not convertible to float.
        """

        try:
            u_in = float(self.u_in_string.get())
            d = float(self.d_string.get())
            S = float(self.S_string.get())
            C = float(self.C_string.get())
            t_ang = float(self.t_ang_string.get())

            if self.data_manager.is_data_loaded():
                self.data_manager.update_input_voltage(u_in)
                self.data_manager.update_thickness(d)
                self.data_manager.update_area(S)
                self.data_manager.update_capacitance(C)
                self.data_manager.update_tilt_angle(t_ang)
                self.update_bottom_left_panel()
        except ValueError:
            pass

    def choose_color(self, param):
        """
        Changes graph color according to passed parameter and
        updates graph.

        Parameters
        ----------
        param : str
            Text string indicating chosen object on graph.
        """
        new_color_code = colorchooser.askcolor()[1]

        # set color according to passed param
        if param == "plot":
            self.plot_color.set(new_color_code)
        elif param == "inc":
            self.inc_region_color.set(new_color_code)
        elif param == "dec":
            self.dec_region_color.set(new_color_code)
        elif param == "knee":
            self.knee_point_color.set(new_color_code)
        elif param == "t4060":
            self.t40_60_points_color.set(new_color_code)
        else:
            pass

        # updates colors
        if self.data_manager.is_data_loaded():
            line = self.ax.lines[0]
            line.set_color(self.plot_color.get())
            self.mark_regions()
            self.mark_points()
            self.canvas.draw()
            self.toolbar.update()

    def update_alpha(self, *args):
        """
        Updates alpha values when scale is changed then updates graph.
        """
        self.inc_alpha_region = self.inc_region_alpha_scale.get() / 100.0
        self.dec_alpha_region = self.dec_region_alpha_scale.get() / 100.0

        self.mark_regions()
        self.canvas.draw()
        self.toolbar.update()

    def on_click(self, event):
        """
        Derives x, y coords of mouse click then updates right panels
        if data is loaded.

        Parameters
        ----------
        event : MouseEvent
            Event indicating mouse click on chart.
        """
        if event.inaxes:
            x = event.xdata
            if self.data_manager.is_data_loaded():
                self.update_right_panels(x)

    def load_data_from_scope(self):
        """
        Tries to get time and voltage data from oscilloscope
        through local network, passes them to data manager and
        draws graph.
        """
        ip_address = self.ip_address_entry.get()
        channel = self.channel_entry.get()

        time, voltage = self.scope.get_waveform(ip_address, channel)

        if time.any() and voltage.any():
            self.data_manager.clear_data()
            self.data_manager.load_data(time, voltage)
            self.change_values(None)
            self.draw_plot(time, voltage)
            self.update_bottom_left_panel()

    def load_data_from_file(self):
        """
        Tries to get time and voltage data from csv file
        passes them to data manager and draws graph.
        """
        time = []
        voltage = []

        # asking for a file
        initial_dir = os.getcwd()
        filepath = tk.filedialog.askopenfilename(
            initialdir=initial_dir, title="Choose CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filepath:
            try:
                with open(filepath, newline='', encoding='latin1') as file:
                    reader = csv.reader(file)
                    skip_row = 100  # skipping some lines on the beginning
                    time_col = 0
                    volt_col = 1
                    for row in reader:
                        if skip_row > 0:
                            skip_row = skip_row - 1
                        elif row[time_col] == "":
                            time_col += 1
                            volt_col += 1
                        elif row[volt_col] == "":
                            volt_col += 1
                        else:  # loading data
                            time.append(float(row[time_col]))
                            voltage.append(float(row[volt_col]))
            except Exception as e:
                tk.messagebox.showinfo("Error", f"{e}")

        if time and voltage:
            self.data_manager.clear_data()
            self.data_manager.load_data(time, voltage)
            self.change_values(None)
            self.draw_plot(time, voltage)
            self.update_bottom_left_panel()

    def draw_plot(self, time, voltage):
        """
        Clears graph, marks regions and points and draws new graph

        Parameters
        ----------
        time : list of float
            Time data
        voltage : list of float
            Voltage data
        """
        self.ax.clear()      # clears graph

        self.mark_regions()  # marks regions
        self.mark_points()   # marks characteristic points

        # configure and draw new graph
        self.ax.plot(time, voltage, color=self.plot_color.get())
        self.ax.autoscale()
        self.ax.set_xlabel('Time (t)')
        self.ax.set_ylabel('Voltage (v)')
        self.ax.grid(True)
        self.canvas.draw()
        self.toolbar.update()

    def mark_regions(self):
        """
        Clears all existing rectangles then draws new one.
        """
        # clear rectangles if some already exists
        for patch in self.ax.patches:
            if isinstance(patch, matplotlib.patches.Rectangle):
                patch.remove()

        # derive region border data from data manager
        inc_regions = self.data_manager.get_inc_regions()
        dec_regions = self.data_manager.get_dec_regions()

        # mark increasing regions
        for region_borders in inc_regions:
            self.ax.axvspan(
                region_borders[0],
                region_borders[1],
                color=self.inc_region_color.get(),
                alpha=self.inc_alpha_region
            )

        # mark decreasing regions
        for region_borders in dec_regions:
            self.ax.axvspan(
                region_borders[0],
                region_borders[1],
                color=self.dec_region_color.get(),
                alpha=self.dec_alpha_region
            )

    def mark_points(self):
        """
        Clears all existing points then draws new one.
        """
        # clears points of some already exists
        for obj in self.ax.collections:
            if isinstance(obj, matplotlib.collections.PathCollection):
                obj.remove()

        # derives knee point coords from data manager
        points = self.data_manager.get_knee_points()

        # marks knee point on graph
        for point in points:
            self.ax.scatter(
                point[0],
                point[1],
                color=self.knee_point_color.get()
            )

        # derives t40-60 point coords
        points = self.data_manager.get_t40_60_points()

        # then draws them on graph
        for point in points:
            self.ax.scatter(
                point[0],
                point[1],
                color=self.t40_60_points_color.get()
            )

    def update_right_panels(self, x):
        """
        Clears entries on right panel then writes new values.

        Parameters
        ----------
        x : float
            X coord of mouse click event on chart.
        """
        # set entry states to normal
        self.local_up_entry.config(state="normal")
        self.local_uc_entry.config(state="normal")
        self.local_tau_entry.config(state="normal")
        self.local_alpha_entry.config(state="normal")
        self.local_ps_entry.config(state="normal")
        self.local_rv_entry.config(state="normal")
        self.local_da_entry.config(state="normal")

        # clears all existing content
        self.local_up_entry.delete(0, tk.END)
        self.local_uc_entry.delete(0, tk.END)
        self.local_tau_entry.delete(0, tk.END)
        self.local_alpha_entry.delete(0, tk.END)
        self.local_ps_entry.delete(0, tk.END)
        self.local_rv_entry.delete(0, tk.END)
        self.local_da_entry.delete(0, tk.END)

        # gets chosen region from data manager
        region = self.data_manager.get_chosen_region(x)

        # inserts new content to entries
        if region:
            up = region.get_up()
            uc = region.get_uc()
            tau = region.get_tau()
            alpha = region.get_alpha()
            ps = region.get_sp()
            rv = region.get_rv()
            da = region.get_da()

            self.local_up_entry.insert(0, f"{up:.3f}")
            self.local_uc_entry.insert(0, f"{uc:.3f}")
            self.local_tau_entry.insert(0, f"{tau:.3f}")
            self.local_alpha_entry.insert(0, f"{alpha:.3f}")
            self.local_ps_entry.insert(0, f"{ps:.3f}")
            self.local_rv_entry.insert(0, f"{rv:.3f}")
            self.local_da_entry.insert(0, f"{da:.3f}")

        # sets entries state to read only
        self.local_up_entry.config(state="readonly")
        self.local_uc_entry.config(state="readonly")
        self.local_tau_entry.config(state="readonly")
        self.local_alpha_entry.config(state="readonly")
        self.local_ps_entry.config(state="readonly")
        self.local_rv_entry.config(state="readonly")
        self.local_da_entry.config(state="readonly")

    def update_bottom_left_panel(self):
        """
        Clears entries on left panel then writes new values.
        """
        # set entry states to normal
        self.ps_entry.config(state="normal")
        self.rv_entry.config(state="normal")
        self.da_entry.config(state="normal")

        # clears all existing content
        self.ps_entry.delete(0, tk.END)
        self.rv_entry.delete(0, tk.END)
        self.da_entry.delete(0, tk.END)

        # inserts new content to entries
        sp = self.data_manager.get_sp()
        rv = self.data_manager.get_rv()
        da = self.data_manager.get_da()

        self.ps_entry.insert(0, f"{sp:.3f}")
        self.rv_entry.insert(0, f"{rv:.3f}")
        self.da_entry.insert(0, f"{da:.3f}")

        # sets entries state to read only
        self.ps_entry.config(state="readonly")
        self.rv_entry.config(state="readonly")
        self.da_entry.config(state="readonly")
