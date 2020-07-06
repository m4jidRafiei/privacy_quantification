from os import truncate
import math

import itertools
import numpy as np
import pandas as pd
from itertools import chain
from collections import Counter
from Levenshtein import distance as levenshtein_distance


class EMD:

    def __init__(self):
        self = self

    def log_freq(self,simple_log):
        sum_seq = 0
        tuple_list = map(tuple, simple_log)
        c = Counter(tuple_list)
        return self.relative_freq(c)

    def relative_freq(self,counter):
        total_count = sum(counter.values())
        relative = {}
        for key in counter:
            relative[key] = round(counter[key] / total_count, 4)
        return relative

    def distance_array(self,log1,log2):
        array = np.zeros(shape=(len(log1), len(log2)))
        for index1,trace1 in enumerate(log1):
            for index2,trace2 in enumerate(log2):
                str1 = ''.join(trace1)
                str2 = ''.join(trace2)
                dist_01 = levenshtein_distance(str1,str2)/max(len(str1), len(str2))
                array[index1][index2] = round(dist_01,4)
                # array[index1][index2] = 10
                print(index1)

        df = pd.DataFrame(array, [''.join(item[0])+":"+str(item[1]) for item in log1.items()], [''.join(item[0])+":"+str(item[1]) for item in log2.items()])
        return df,array

    def emd_distance(self, log_freq_1, log_freq_2, distance_df):
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


    def truncate(self,number, digits):
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper