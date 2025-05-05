"""Region module"""

import numpy as np
import matplotlib.pyplot as plt


class Region:
    """Region class which holds and process local data in monotonic region"""
    def __init__(self, time, voltage, dv_dt, increasing):
        """Loads and processes region data"""
        self.time = time
        self.voltage = voltage
        self.increasing = increasing
        self.knee_point_time = 0       # knee point x
        self.knee_point_voltage = 0    # knee point y
        self.t40_time = 0              # t40 x
        self.t40_voltage = 0           # t40 y
        self.t60_time = 0              # t60 x
        self.t60_voltage = 0           # t60 y
        self.u_p = 0                   # repolarization voltage
        self.u_c = 0                   # conductivity voltage
        self.tau = 0                   # switching time
        self.alpha = 0                 # alpha parameter
        self.u_in = 10.0               # input voltage
        self.d = 3e-6                  # cell thickness
        self.S = 100e-6                # cell area
        self.C = 30e-9                 # capacitance
        self.t_ang = np.radians(45.0)  # tilt angle
        self.s_p = 0                   # spontaneous polarization
        self.e0 = 8.854e-12            # dielectric permittivity in vacuum

        t_norm = []                  # time of response
        u_norm = []                  # normalized response
        u_norm_diff = []             # normalized response differentiated
        alpha_table = []             # table for alpha values for each point

        max_voltage = max(voltage)
        min_voltage = min(voltage)
        max_rise = max(dv_dt)
        max_fall = min(dv_dt)

        percent = 0.9
        max_threshold = max_rise * percent
        min_threshold = max_fall * percent

        # calculate knee point
        p = 0  # pointer index
        k = 0  # knee point index

        if self.increasing:
            # move pointer index to max threshold
            for i in range(p, len(time)):
                if dv_dt[i] > max_threshold:
                    p = i
                    break

            # move pointer index to pike of the rise and
            # break if reached below threshold
            for i in range(p + 1, len(time)):
                if dv_dt[i] > dv_dt[i - 1]:
                    p = i

                if dv_dt[i] < max_threshold:
                    break

            # move pointer index to next local minimum
            # of the rise where knee point is located
            for i in range(p, len(time)):
                if dv_dt[i + 1] > dv_dt[i]:
                    p = i
                    k = i
                    break

            # calculate polarization voltage
            self.u_p = max_voltage - voltage[p]

            # save x, y coords of knee point
            self.knee_point_time = time[p]
            self.knee_point_voltage = voltage[p]

            # now calculate tau parameter
            self.u_c = voltage[p] - min_voltage  # capacitance voltage
            t40_threshold = min_voltage + self.u_c + self.u_p * 0.4
            t60_threshold = min_voltage + self.u_c + self.u_p * 0.6

            # find t40 x, y coords
            for i in range(p, len(time)):
                if voltage[i] < t40_threshold:
                    continue
                else:
                    self.t40_time = time[i]
                    self.t40_voltage = voltage[i]
                    p = i
                    break

            # find t60 x, y coords
            for i in range(p, len(time)):
                if voltage[i] < t60_threshold:
                    continue
                else:
                    self.t60_time = time[i]
                    self.t60_voltage = voltage[i]
                    break

            # calculate tau parameter
            self.tau = (self.t60_time - self.t40_time) / 0.405465

            # now calculate alpha parameter
            # first normalize voltage to u = -cos(phi(t))
            # from knee point to the end of region

            # calculate threshold to exclude points near min and max up volts
            voltage_low_threshold = min_voltage + self.u_c + self.u_p * 0.05
            voltage_high_threshold = min_voltage + self.u_c + self.u_p * 0.95

            # normalize up voltage with exclusion of near min and max up volts
            # and points between t40 and t60
            for i in range(k, len(time)):
                if voltage[i] < voltage_low_threshold:
                    continue
                elif voltage[i] > voltage_high_threshold:
                    continue
                elif time[i] > self.t40_time and time[i] < self.t60_time:
                    continue
                else:
                    t = time[i] - self.knee_point_time
                    t_norm.append(t)

                    u = voltage[i] - self.knee_point_voltage
                    u /= (0.5 * self.u_p)
                    u -= 1
                    u_norm.append(u)
        else:
            # move pointer index to min threshold
            for i in range(p, len(time)):
                if dv_dt[i] < min_threshold:
                    p = i
                    break

            # move pointer index to pike of the fall and
            # break if reached above threshold
            for i in range(p + 1, len(time)):
                if dv_dt[i] < dv_dt[i - 1]:
                    p = i

                if dv_dt[i] > min_threshold:
                    break

            # move pointer index to next local maximum
            # of the fall where knee point is located
            for i in range(p, len(time)):
                if dv_dt[i + 1] < dv_dt[i]:
                    p = i
                    k = i
                    break

            # calculate polarization voltage
            self.u_p = voltage[p] - min_voltage

            # save x, y coords of knee point
            self.knee_point_time = time[p]
            self.knee_point_voltage = voltage[p]

            # now calculate tau parameter
            self.u_c = max_voltage - voltage[p]  # capacitance voltage
            t40_threshold = max_voltage - self.u_c - self.u_p * 0.4
            t60_threshold = max_voltage - self.u_c - self.u_p * 0.6

            # find t40 x, y coords
            for i in range(p, len(time)):
                if voltage[i] > t40_threshold:
                    continue
                else:
                    self.t40_time = time[i]
                    self.t40_voltage = voltage[i]
                    p = i
                    break

            # find t60 x, y coords
            for i in range(p, len(time)):
                if voltage[i] > t60_threshold:
                    continue
                else:
                    self.t60_time = time[i]
                    self.t60_voltage = voltage[i]
                    break

            # calculate tau parameter
            self.tau = (self.t60_time - self.t40_time) / 0.405465

            # now calculate alpha parameter
            # first normalize voltage to u = -cos(phi(t))
            # from knee point to the end of region

            # calculate threshold to exclude points near min and max up volts
            voltage_high_threshold = max_voltage - self.u_c - self.u_p * 0.05
            voltage_low_threshold = max_voltage - self.u_c - self.u_p * 0.95

            # normalize up voltage with exclusion of near min and max u_p volts
            # and points between t40 and t60
            for i in range(k, len(time)):
                if voltage[i] > voltage_high_threshold:
                    continue
                elif voltage[i] < voltage_low_threshold:
                    continue
                elif time[i] > self.t40_time and time[i] < self.t60_time:
                    continue
                else:
                    t = time[i] - self.knee_point_time
                    t_norm.append(t)

                    u = self.knee_point_voltage - voltage[i]
                    u /= (0.5 * self.u_p)
                    u -= 1
                    u_norm.append(u)

        # differentiate norm values
        u_norm_diff = np.gradient(u_norm, t_norm)

        # fill alpha table with values for each point
        for i in range(len(t_norm)):
            a = 1 - (u_norm_diff[i] * self.tau) / (1 - u_norm[i]**2)
            b = 1 / u_norm[i]

            alpha_table.append(a * b)

        # calculate alpha value by averaging alpha values from all points
        self.alpha = sum(alpha_table) / len(alpha_table)

    def is_increasing(self):
        """Checks if region is increasing"""
        return self.increasing

    def update_input_voltage(self, u_in):
        """Updates input voltage"""
        self.u_in = u_in

    def update_thickness(self, d):
        """Updates cell thickness"""
        d /= 1000000.0
        self.d = d

    def update_area(self, S):
        """Updates cell area"""
        S /= 1000000.0
        self.S = S

    def update_capacitance(self, C):
        """Updates cell capacitance"""
        C /= 1000000000.0
        self.C = C

    def update_tilt_angle(self, t_ang):
        """Updates tilt angle"""
        self.t_ang = np.radians(t_ang)

    def get_up(self):
        """Return Up"""
        return self.u_p

    def get_uc(self):
        """Return Uc"""
        return self.u_c

    def get_tau(self):
        """Returns tau"""
        tau = self.tau
        tau *= 1000000
        return tau

    def get_alpha(self):
        """Returns alpha"""
        return self.alpha

    def get_sp(self):
        """Returns Ps"""
        self.s_p = (self.u_p * self.C) / (2 * self.S)
        s_p = self.s_p * 100000
        return s_p

    def get_rv(self):
        """Returs rv"""
        r_v = (self.tau * self.s_p * self.u_in) / (self.d)
        r_v *= 10
        return r_v

    def get_da(self):
        """Returns da"""
        d_a = self.alpha * self.s_p * self.d
        d_a /= (self.u_in * self.e0 * np.sin(self.t_ang)**2)
        return d_a

    def get_borders(self):
        """Returns border coords"""
        return [self.time[0], self.time[-1]]

    def get_knee_point(self):
        """Returns knee point coords"""
        return [self.knee_point_time, self.knee_point_voltage]

    def get_t40_point(self):
        """Returns t40 point coords"""
        return [self.t40_time, self.t40_voltage]

    def get_t60_point(self):
        """Returns t60 point coords"""
        return [self.t60_time, self.t60_voltage]
