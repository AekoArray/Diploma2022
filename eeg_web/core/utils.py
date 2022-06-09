import base64
import io
import math
import urllib.parse

from matplotlib import pyplot as plt
from numpy import arange

from core.models import Settings


class AnalysisHelper:

    def __init__(self, setting_id, test_signal):
        self.settings = Settings.objects.get(id=setting_id)
        self.s_h_min = self.settings.s_h_min
        self.s_h_max = self.settings.s_h_max
        self.s_w_min = self.settings.s_w_min
        self.s_w_max = self.settings.s_w_max

        self.w_h_min = self.settings.w_h_min
        self.w_h_max = self.settings.w_h_max
        self.w_w_min = self.settings.w_w_min
        self.w_w_max = self.settings.w_w_max

        self.FD = 178
        self.N = 178
        self.time_range = arange(self.N) / float(self.FD)
        self.test_signal = test_signal

    def get_answer_from_raw_data(self, pure_sig):
        oscillations = self.find_oscillations(pure_sig)
        self.filter_oscillations(oscillations, 35)
        w_h = self.get_width_and_height(oscillations)
        patterns = []
        for i in range(0, len(w_h) - 1):
            if self.find_pattern(w_h[i], self.s_h_min, self.s_h_max, self.s_w_min, self.s_w_max) and (
                    (not self.find_pattern(w_h[i - 1], self.s_h_min, self.s_h_max, self.s_w_min, self.s_w_max)) if (
                            not i == 0) else True):
                if self.find_pattern(w_h[i + 1], self.w_h_min, self.w_h_max, self.w_w_min, self.w_w_max):
                    patterns.append({"spike": w_h[i], "wave": w_h[i + 1]})
        has_pattern = not len(patterns) == 0
        return {
            "has_pattern": has_pattern,
            "patterns": patterns,
        }

    @staticmethod
    def filter_oscillations(osc, filter):
        i = 0
        length = len(osc)
        while not i == length:
            if (not i == 0) and abs(osc[i]["peak"][0] - osc[i]["first"][0]) < filter:
                osc[i - 1]["second"] = osc[i]["second"]
                osc[i - 1]["end_index"] = osc[i]["end_index"]
                osc.pop(i)
                length -= 1
            elif (not i == length - 1) and abs(osc[i]["peak"][0] - osc[i]["second"][0]) < filter:
                osc[i]["peak"] = osc[i + 1]["peak"]
                osc[i]["second"] = osc[i + 1]["second"]
                osc[i]["end_index"] = osc[i + 1]["end_index"]
                osc.pop(i + 1)
                length -= 1
                i += 1
            else:
                i += 1

    def find_oscillations(self, data):
        oscillations = []
        up = data[0] < data[1]
        start_index = 0
        end_index = 0
        if data[0] > data[1]:
            counter = 2
            peak = [data[0], self.time_range[0]]
            prev = [data[1], self.time_range[1]]
            first = [data[0], self.time_range[0]]
        else:
            counter = 1
            peak = 0
            first = [data[0], self.time_range[0]]
            prev = [data[0], self.time_range[0]]
        for i, time in zip(range(1, len(data)), self.time_range):
            new_up = False
            if prev[0] < data[i]:
                new_up = True
            if not up == new_up:
                if counter == 0:
                    start_index = i - 1
                    first = prev
                    counter += 1
                elif counter == 1:
                    if first < prev:
                        peak = prev
                        counter += 1
                    else:
                        start_index = i - 1
                        first = prev
                elif counter == 2:
                    second = prev
                    end_index = i - 1
                    counter = 1
                    oscillations.append(
                        {
                            "first": first,
                            "peak": peak,
                            "second": second,
                            "start_index": start_index,
                            "end_index": end_index
                        }
                    )
                    first = prev
                    start_index = i - 1
                    peak = 0
                    second = 0
                up = not up
            prev = [data[i], time]
        return oscillations

    @staticmethod
    def get_time(wave):
        return (wave["second"][1] - wave["first"][1]) * 1000

    @staticmethod
    def get_len(wave):
        return wave["peak"][0] - max(wave["first"][0], wave["second"][0])

    def get_width_and_height(self, osc):
        data = []
        for i in range(len(osc)):
            item = {}
            width = math.ceil(self.get_time(osc[i]))
            height = self.get_len(osc[i])
            item["start_point"] = osc[i]["start_index"]
            item["end_point"] = osc[i]["end_index"]
            item["width"] = width
            item["height"] = height
            data.append(item)
        return data

    @staticmethod
    def find_pattern(osc, height_min, height_max, wight_min, wight_max):
        return (height_min <= osc['height'] <= height_max) and (wight_min <= osc['width'] <= wight_max)

    def get_image_by_answer(self, answer):
        patterns = answer['patterns']
        indexes = []
        for i in range(len(patterns)):
            start_point = answer['patterns'][i]['spike']['start_point']
            end_point = answer['patterns'][i]['wave']['end_point']

            indexes.append([start_point, end_point])

        plt.switch_backend('AGG')

        len_indexes = len(indexes)
        for idx in range(len_indexes):
            curr = indexes[idx]
            red_x = (self.time_range[curr[0]:curr[1] + 1])
            red_y = (self.test_signal[curr[0]:curr[1] + 1])
            plt.plot(red_x, red_y, 'red')

            if idx == 0:
                x = self.time_range[:curr[0] + 1]
                y = self.test_signal[:curr[0] + 1]
                plt.plot(x, y, 'black')

            if idx + 1 == len_indexes:
                x = self.time_range[curr[1]:]
                y = self.test_signal[curr[1]:]
                plt.plot(x, y, 'black')

            if idx < len_indexes - 1:
                next_elem = indexes[idx + 1]
                x = self.time_range[curr[1]:next_elem[0] + 1]
                y = self.test_signal[curr[1]:next_elem[0] + 1]
                plt.plot(x, y, 'black')

        if len_indexes == 0:
            plt.plot(self.time_range, self.test_signal, 'black')

        plt.grid(True)
        plt.xlabel(u'Время, c')
        plt.ylabel(u'Напряжение, мВ')
        plt.title(u'Сигнал')

        fig = plt.gcf()
        fig.set_size_inches(13, 5)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())

        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        return uri
