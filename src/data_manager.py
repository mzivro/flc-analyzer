"""Data manager module"""

import numpy as np
from region import Region


class DataManager():
    """
    Data manager class responsible for managing region instances
    """
    def __init__(self):
        """Inits regions list and sets data loaded flag to false"""
        self.regions = []

        self.data_loaded = False

    def load_data(self, time, voltage):
        """Processes and loads data into regions"""
        ext_indexes = []  # extreme value indexes
        bor_indexes = []  # border value indexes
        local_max_index = 0
        local_min_index = 0
        increasing = False
        decreasing = False
        buffer = 0

        dv_dt = np.gradient(voltage, time)

        max_rise = max(dv_dt)
        min_fall = min(dv_dt)

        threshold = 0.8

        max_threshold = max_rise * threshold
        min_threshold = min_fall * threshold

        # get indexes of maximum and minimum values of dv/dt
        for i in range(len(time)):
            if dv_dt[i] > max_threshold:
                if dv_dt[i] > dv_dt[i - 1]:
                    local_max_index = i
            elif dv_dt[i] < min_threshold:
                if dv_dt[i] < dv_dt[i - 1]:
                    local_min_index = i
            else:
                if local_max_index:
                    ext_indexes.append(local_max_index)
                    local_max_index = 0

                if local_min_index:
                    ext_indexes.append(local_min_index)
                    local_min_index = 0

        # get borders of monotonic regions
        for i in range(ext_indexes[0], len(time)):
            if i in ext_indexes:
                if dv_dt[i] > 0:
                    j = i

                    while True:
                        if dv_dt[j - 1] <= 0:
                            bor_indexes.append(j)
                            break
                        else:
                            j = j - 1

                if dv_dt[i] < 0:
                    j = i

                    while True:
                        if dv_dt[j - 1] >= 0:
                            bor_indexes.append(j)
                            break
                        else:
                            j = j - 1

            if i > ext_indexes[-1]:
                break

        # get monotonic regions
        for i in range(bor_indexes[0], len(time)):
            if i in bor_indexes:
                if dv_dt[i] > 0:
                    if decreasing:
                        region_time = []
                        region_voltage = []
                        region_dv_dt = []

                        for j in range(buffer, i):
                            region_time.append(time[j])
                            region_voltage.append(voltage[j])
                            region_dv_dt.append(dv_dt[j])

                        region = Region(
                            region_time,
                            region_voltage,
                            region_dv_dt,
                            False
                        )

                        self.regions.append(region)

                    buffer = i
                    increasing = True
                    decreasing = False

                if dv_dt[i] < 0:
                    if increasing:
                        region_time = []
                        region_voltage = []
                        region_dv_dt = []

                        for j in range(buffer, i):
                            region_time.append(time[j])
                            region_voltage.append(voltage[j])
                            region_dv_dt.append(dv_dt[j])

                        region = Region(
                            region_time,
                            region_voltage,
                            region_dv_dt,
                            True
                        )

                        self.regions.append(region)

                    buffer = i
                    increasing = False
                    decreasing = True

            if i > bor_indexes[-1]:
                break

        # set data loaded flag to true
        self.data_loaded = True

    def clear_data(self):
        """Clears regions lists"""
        self.regions.clear()

    def is_data_loaded(self):
        """Checks if data is loaded"""
        return self.data_loaded

    def update_input_voltage(self, u_in):
        """Updates input voltages data in regions"""
        for region in self.regions:
            region.update_input_voltage(u_in)

    def update_thickness(self, d):
        """Updates cell thickness data in regions"""
        for region in self.regions:
            region.update_thickness(d)

    def update_area(self, S):
        """Updates cell area data in regions"""
        for region in self.regions:
            region.update_area(S)

    def update_capacitance(self, C):
        """Updates cell capacitance data in regions"""
        for region in self.regions:
            region.update_capacitance(C)

    def update_tilt_angle(self, t_ang):
        """Updates tilt angle data in regions"""
        for region in self.regions:
            region.update_tilt_angle(t_ang)

    def get_sp(self):
        """Returns averaged sp from all regions"""
        s_p = []

        for region in self.regions:
            s_p.append(region.get_sp())

        return sum(s_p) / len(s_p)

    def get_rv(self):
        """Returns averaged rv from all regions"""
        r_v = []

        for region in self.regions:
            r_v.append(region.get_rv())

        return sum(r_v) / len(r_v)

    def get_da(self):
        """Returns averaged da from all regions"""
        d_a = []

        for region in self.regions:
            d_a.append(region.get_da())

        return sum(d_a) / len(d_a)

    def get_inc_regions(self):
        """Returns border data from inc regions"""
        borders = []

        for region in self.regions:
            if region.is_increasing():
                borders.append(region.get_borders())

        return borders

    def get_dec_regions(self):
        """Returns border data from dec regions"""
        borders = []

        for region in self.regions:
            if not region.is_increasing():
                borders.append(region.get_borders())

        return borders

    def get_t40_60_points(self):
        """Returns t40-60 points data from all regions"""
        points = []

        for region in self.regions:
            points.append(region.get_t40_point())
            points.append(region.get_t60_point())

        return points

    def get_knee_points(self):
        """Returns knee points data from all regions"""
        points = []

        for region in self.regions:
            points.append(region.get_knee_point())

        return points

    def get_chosen_region(self, x):
        """Returns chosen region"""
        for region in self.regions:
            borders = region.get_borders()

            if x > borders[0] and x < borders[1]:
                return region
