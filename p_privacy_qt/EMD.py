import math
import numpy as np
import pandas as pd
from collections import Counter
from Levenshtein import distance as levenshtein_distance
from pyemd import emd, emd_with_flow


class EMD:

    def __init__(self):
        self = self

    def log_freq(self,simple_log):
        sum_seq = 0
        tuple_list = map(tuple, simple_log)
        c = Counter(tuple_list)
        return self.relative_freq(c, len(c.items()))

    def relative_freq(self,counter, n):
        only_freq = np.zeros(n)
        total_count = sum(counter.values())
        relative = {}
        for index, key in enumerate(counter):
            relative[key] = round(counter[key] / total_count, 4)
            only_freq[index] = round(counter[key] / total_count, 4)
        return relative,only_freq

    def distance_array(self,log1,log2):
        array = np.zeros(shape=(len(log1), len(log2)))
        for index1,trace1 in enumerate(log1):
            print("variant: " + str(index1))
            for index2,trace2 in enumerate(log2):
                str1 = ''.join(trace1)
                str2 = ''.join(trace2)
                dist_01 = levenshtein_distance(str1,str2)/max(len(str1), len(str2))
                array[index1][index2] = round(dist_01,4)
                # array[index1][index2] = 10

        df = pd.DataFrame(array, [''.join(item[0])+":"+str(item[1]) for item in log1.items()], [''.join(item[0])+":"+str(item[1]) for item in log2.items()])
        return df,array

    def emd_distance(self, log_freq_1, log_freq_2):
        distance_df, array = self.distance_array(log_freq_1, log_freq_2)
        cost = 0
        for ind, item in enumerate(log_freq_1.items()):
            freq = item[1]
            row = distance_df.iloc[ind]
            min_col = row.idxmin()
            while freq > 0:
                freq_to_transfer = min(freq, float(min_col.split(':')[1]))
                diff = freq - float(min_col.split(':')[1])
                if diff < 0:
                    diff = 0
                cell_value = distance_df.at[''.join(item[0]) + ":" + str(item[1]), min_col]
                distance_df.at[''.join(item[0]) + ":" + str(item[1]), min_col] = cell_value * freq_to_transfer
                cost += cell_value * freq_to_transfer
                # distance_df = distance_df.rename(index={''.join(item[0])+":"+str(freq): ''.join(item[0])+":"+str(diff)})
                freq = diff
                row = row.drop(labels=[min_col])
                min_col = row.idxmin()
        return self.truncate(cost,3)


    def emd_distance_pyemd(self,log_only_freq_1,log_only_freq_2,log_freq_1,log_freq_2):
        checked = False
        if len(log_only_freq_2) < len(log_only_freq_1):
            checked = True
            diff = len(log_only_freq_1) - len(log_only_freq_2)
            for i in range(diff):
                fake_str = 'a' + str(i)
                log_freq_2[tuple(fake_str)] = 0
                log_only_freq_2 = np.append(log_only_freq_2, 0)
        elif len(log_only_freq_1) < len(log_only_freq_2) and not checked:
            diff = len(log_only_freq_2) - len(log_only_freq_1)
            for i in range(diff):
                fake_str = 'a' + str(i)
                log_freq_1[tuple(fake_str)] = 0
                log_only_freq_1 = np.append(log_only_freq_1, 0)
        distance_df, array = self.distance_array(log_freq_1, log_freq_2)
        # if len(log_only_freq_1) > array.shape[0]:
        #     len(log_only_freq_1).pop()
        #     log_freq_1.pop()
        # if len(log_only_freq_2) > array.shape[1]:
        #     len(log_only_freq_2).pop()
        #     log_freq_2.pop()
        cost_lp = emd(log_only_freq_1, log_only_freq_2, array)
        if cost_lp > 1:
            cost_lp = 1
        return cost_lp


    def truncate(self,number, digits):
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper