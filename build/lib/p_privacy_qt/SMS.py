import itertools
import os
import sys

import numpy as np
from itertools import chain
from collections import Counter
import pyfpgrowth
from multiset import Multiset
import copy
import datetime
import pandas as pd
import multiprocessing as mp


# get_occurances_... are faster than get_occurances_matches_...
# because similar elements are packed in one and counted by Counter

class SMS:  # Set-Multiset-Sequence calculator

    def __init__(self):
        self = self

    def create_simple_log(self, log, activity_att):
        simple_log = []
        for case_index, case in enumerate(log):
            trace = []
            for event_index, event in enumerate(case):
                life_cycle = ""
                activity = ""
                for key, value in event.items():
                    if key == activity_att[1]:
                        life_cycle = value
                    if key == activity_att[0]:
                        activity = value
                if life_cycle == "complete" or life_cycle == "":
                    trace.append(activity)
            simple_log.append(tuple(trace))

        return simple_log

    def get_unique_act(self, iter):
        act_list = chain.from_iterable(iter)
        return set(act_list)

    # def map_act_char(self, traces, offset):
    #     uniq_act = self.get_unique_act(traces)
    #     map_dict_act_chr = {}
    #     map_dict_chr_act = {}
    #     for index, item in enumerate(uniq_act):
    #         map_dict_act_chr[item] = chr(index+offset)
    #         map_dict_chr_act[chr(index+offset)] = item
    #
    #     return map_dict_act_chr, map_dict_chr_act

    def map_act_char(self, uniq_act):
        uniq_char = []
        map_dict_act_chr = {}
        map_dict_chr_act = {}
        for index, item in enumerate(uniq_act):
            map_dict_act_chr[item] = chr(index)
            map_dict_chr_act[chr(index)] = item
            uniq_char.append(chr(index))
        return map_dict_act_chr, map_dict_chr_act, uniq_char

    def convert_act_to_char(self, trace, map_dict_act_chr):
        trace_str = ""
        for item in trace:
            try:
                trace_str += map_dict_act_chr[item]
            except KeyError:
                map_dict_act_chr[item] = chr(len(map_dict_act_chr))
                trace_str += map_dict_act_chr[item]
        return trace_str

    def convert_char_to_act(self, trace, map_dict_chr_act):
        trace_act = []
        for item in trace:
            trace_act.append(map_dict_chr_act[item])
        return trace_act

    def convert_simple_log_act_to_char(self, simple_log, map_dict_act_chr):
        simple_log_char = copy.deepcopy(simple_log)
        traces_char = []
        for case, value in simple_log.items():
            trace_string = self.convert_act_to_char(simple_log[case]['trace'], map_dict_act_chr)
            simple_log_char[case]['trace'] = trace_string
            traces_char.append(trace_string)
        return simple_log_char, traces_char

    def convert_simple_log_char_to_act(self, simple_log, map_dict_chr_act):
        simple_log_act = copy.deepcopy(simple_log)
        traces_act = []
        for case, value in simple_log.items():
            trace_act = self.convert_char_to_act(simple_log[case]['trace'], map_dict_chr_act)
            simple_log_act[case]['trace'] = trace_act
            traces_act.append(trace_act)
        return simple_log_act, traces_act

    def create_simple_log_adv(self, log, event_attributes, life_cycle, all_life_cycle, sensitive_attributes,
                              time_accuracy, from_time_days, to_time_days):
        time_prefix = 'time:timestamp'
        life_cycle_prefix = ['lifecycle:transition']
        logsimple = {}
        traces = []
        sensitives = {el: [] for el in sensitive_attributes}
        columns = ['case_id', 'trace']
        columns += sensitive_attributes
        dataframe = pd.DataFrame(columns=columns)

        start_time, end_time = self.get_start_end_time(log)
        from_time = 0
        to_time = 0
        if from_time_days != 0 and to_time_days != 0:
            from_time = start_time - datetime.timedelta(days=from_time_days)
            from_time = from_time.replace(hour=00, minute=00, second=00, microsecond=000000)
            to_time = start_time + datetime.timedelta(days=to_time_days - 1)
            to_time = to_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        for case_index, case in enumerate(log):
            trace, sens = self.create_trace(case, event_attributes, life_cycle, all_life_cycle, life_cycle_prefix,
                                            time_prefix,
                                            sensitive_attributes, time_accuracy, from_time, to_time)
            if len(trace) > 0:
                df_row = {'case_id': case.attributes["concept:name"], 'trace': trace}
                logsimple[case.attributes["concept:name"]] = {"trace": tuple(trace), "sensitive": sens}
                traces.append(tuple(trace))
                for key in sens.keys():
                    sensitives[key].append(sens[key])
                    # for datafrane
                    df_row[key] = sens[key]
                dataframe = dataframe.append(df_row, ignore_index=True)

        return logsimple, traces, sensitives, dataframe

    def create_trace(self, case, event_attributes, life_cycle, all_life_cycle, life_cycle_prefix,
                     time_prefix, sensitive_attributes, time_accuracy, from_time, to_time):
        sens = {}
        trace = []
        # check sensitive attributes at case level
        sens_dict = {}
        for key, value in case.attributes.items():
            if key in sensitive_attributes:
                sens_dict[key] = value

        for event_index, event in enumerate(case):
            simple_attr_temp = []
            life_cycle_value = ''
            event_dict = {}
            time_matches = False
            for key, value in event.items():
                if key == time_prefix:
                    if from_time == 0 and to_time == 0:
                        time_matches = True
                    elif from_time < value and value <= to_time:
                        time_matches = True
                    if time_prefix in event_attributes:
                        if time_accuracy == 'original':
                            time = value
                        else:
                            if time_accuracy == "seconds":
                                time = value.replace(microsecond=0)
                            elif time_accuracy == "minutes":
                                time = value.replace(second=0, microsecond=0)
                            elif time_accuracy == "hours":
                                time = value.replace(minute=0, second=0, microsecond=0)
                            elif time_accuracy == "days":
                                time = value.replace(hour=0, minute=0, second=0, microsecond=0)
                        event_dict[key] = time

                if key in event_attributes and key != time_prefix:
                    event_dict[key] = value
                if key in sensitive_attributes:
                    sens_dict[key] = value
                if key in life_cycle_prefix:
                    life_cycle_value = value
            if (all_life_cycle or (life_cycle_value in life_cycle)) and time_matches:
                if len(event_dict) < 2:
                    simple_event = list(event_dict.values())[0]
                else:
                    for att in event_attributes:
                        if att in event_dict:
                            simple_attr_temp.append(event_dict[att])
                    simple_event = tuple(simple_attr_temp)
                trace.append(simple_event)

                # for saving the order
                for item in sensitive_attributes:
                    if item in sens_dict:
                        sens[item] = sens_dict[item]

        return trace, sens

    def get_start_end_time(self, log):
        start_time = log[0][0]['time:timestamp']
        end_time = log[len(log) - 1][len(log[len(log) - 1]) - 1]['time:timestamp']

        return start_time, end_time

    # def set_simple_log(self,simple_log):
    #     self.simple_log = simple_log

    def get_unique_elem(self, iter):
        act_list = chain.from_iterable(iter)
        return set(act_list)

    def find_subsets(self, uniq_act, k):
        return list(map(set, itertools.combinations(uniq_act, k)))

    def find_submultisets(self, uniq_act, k):
        return list(map(set, itertools.combinations(uniq_act, k)))

    def get_occurances_set(self, sub_set):
        sum_set = 0
        c = Counter(frozenset(s) for s in self.simple_log)
        for index, items in enumerate(c.items()):
            if sub_set.issubset(items[0]):
                sum_set += items[1]
        return sum_set

    def get_occurances_matches_set(self, sub_set, simple_log):
        sum_set = 0
        # c = Counter(frozenset(s) for s in self.simple_log)
        matches = []
        for key, value in simple_log.items():
            if sub_set.issubset(simple_log[key]['trace']):
                sum_set += 1
                matches.append(simple_log[key])
        return sum_set, matches

    def get_multiset_log(self, alist):
        mult_log = []
        for s in alist:
            mult_s = Counter(s)
            # mult_log.append(mult_s.items())
            dict = mult_s.items()
            mult_log.append(set(dict))
        return mult_log

    def get_multiset_log_n(self, simple_log):
        mult_log = []
        for key, value in simple_log.items():
            multiset_case = {}
            multiset_case['trace'] = Multiset(simple_log[key]['trace'])
            multiset_case['sensitive'] = simple_log[key]['sensitive']
            mult_log.append(multiset_case)
        return mult_log

    def get_multiset_of_sequences(self, sequences):
        mult_seq = []
        counter = 0
        for s in sequences:
            counter += 1
            mult_seq.append(Multiset(s))
        return mult_seq, counter

    def get_occurances_multiset(self, sub_mult):
        sum_mult = 0
        mult_log = self.get_multiset_log(self.simple_log)
        c = Counter(frozenset(s) for s in mult_log)
        for items in c.items():
            if sub_mult.issubset(items[0]):
                sum_mult += items[1]
        return sum_mult

    def get_occurances_matches_multiset(self, mult_log, sub_mult):
        sum_mult_count = 0
        matches = []
        for items in mult_log:
            if sub_mult.issubset(items):
                sum_mult_count += 1
                matches.append(items)
        return sum_mult_count, matches

    def get_occurances_matches_multiset_n(self, mult_log, sub_mult):
        sum_mult_count = 0
        matches = []
        for items in mult_log:
            if sub_mult._issubset(items['trace'], False):
                sum_mult_count += 1
                matches.append(items)
        return sum_mult_count, matches

    def get_set_mult(self, mult):
        set = {}
        for items in mult:
            set.add(items[0])
        return set

    def is_subsequence(self, x, y):
        """Test whether x is a subsequence of y"""
        x = list(x)
        for letter in y:
            if x and x[0] == letter:
                x.pop(0)
        return not x

    def get_occurances_seq(self, sub_seq):
        sum_seq = 0
        tuple_list = map(tuple, self.simple_log)
        c = Counter(tuple_list)
        for items in c.items():
            if self.is_subsequence(sub_seq, items[0]):
                sum_seq += items[1]
        return sum_seq

    def get_tuple_event_log(self, simple_log):
        tuple_event_log = []
        for key, value in simple_log.items():
            tuple_case = {}
            tuple_case['trace'] = tuple(simple_log[key]['trace'])
            tuple_case['sensitive'] = simple_log[key]['sensitive']
            tuple_event_log.append(tuple_case)
        return tuple_event_log

    def get_occurances_matches_seq(self, tuple_log, sub_seq):
        sum_seq = 0
        matches = []
        for items in tuple_log:
            if self.is_subsequence(sub_seq, items['trace']):
                sum_seq += 1
                matches.append(items)
        return sum_seq, matches

    def entropy_clculator(self, matched_list, type):
        if type == "att":
            list = []
            for item in matched_list:
                list_el = []
                for key, value in item.items():
                    list_el.append(key)
                    list_el.append(value)
                    list.append(tuple(list_el))
            tuple_list = map(tuple, list)
        else:
            tuple_list = map(tuple, matched_list)
        c = Counter(tuple_list)
        entropy = 0
        for items in c.items():
            pr = items[1] / len(matched_list)
            entropy += -pr * np.log2(pr)
        return entropy

    def max_entropy(self, matched_list):
        entropy = 0
        for items in matched_list:
            pr = 1 / len(matched_list)
            entropy += -pr * np.log2(pr)
        return entropy

    def get_first_last_act_set(self, simple_log):
        first_act = [item[0] for item in simple_log]
        last_act = [item[len(item) - 1] for item in simple_log]
        return set(first_act), set(last_act)

    def get_seq_patterns(self, simple_log, length):
        patterns = pyfpgrowth.find_frequent_patterns(simple_log, 0)
        seq = []
        for item in patterns.keys():
            if len(item) == length:
                seq.append(item)
        return seq

    def get_sub_seq(self, simple_log, length, multiprocess=True):
        if multiprocess:
            pool = mp.Pool()
            workers = []
            workers_number = os.cpu_count()
            data_chunks = self.chunkIt(simple_log, workers_number)
            results = []
            for worker in range(workers_number):
                print("Subsequence founder: In worker %d out of %d" % (worker + 1, workers_number))
                workers.append(pool.apply_async(self.foo_worker_subseq_without_q, args=(
                data_chunks[worker], length)))
            for work in workers:
                results += work.get()
            pool.close()
            pool.join()

            return list(set(results))

        else:
            sub_seqs = self.foo_worker_subseq_without_q(simple_log,length)
            return list(set(sub_seqs))

    def foo_worker_subseq_without_q(self,data,length):
        sub_seqs = []
        for item in data:
            indexes = [i for i in range(len(item))]
            sub_indexes = self.find_subsets(indexes, length)
            for sub_index in sub_indexes:
                list_sub_index = sorted(list(sub_index))
                sub_seq = [item[index] for index in list_sub_index]
                sub_seqs.append(tuple(sub_seq))
        return sub_seqs

    def all_subsequences(self,s):
        out = set()
        for r in range(1, len(s) + 1):
            for c in itertools.combinations(s, r):
                out.add(''.join(c))
        return out

    def get_sub_seq_t(self, simple_log, length):
        sub_seqs = []
        for item in simple_log:
            indexes = [i for i in range(len(item))]
            sub_indexes = self.find_subsets(indexes, length)
            for sub_index in sub_indexes:
                list_sub_index = sorted(list(sub_index))
                sub_seq = [item[index] for index in list_sub_index]
                if tuple(sub_seq) not in sub_seqs:
                    sub_seqs.append(tuple(sub_seq))
        return tuple(sub_seqs)

    def get_sub_mult(self, simple_log_mult, length):
        sub_mults = []
        for item in simple_log_mult:
            sub_mult = self.find_submultisets(item, length)
            for item in sub_mult:
                if item not in sub_mults:
                    sub_mults.append(item)
        return sub_mults

    def chunkIt(self, data, num):
        avg = len(data) / float(num)
        out = []
        last = 0.0
        while last < len(data):
            out.append(data[int(last):int(last + avg)])
            last += avg
        return out

    def disclosure_calc(self, bk_type, uniq_act, measurement_type, bk_length, existence_based, mult_log, tuple_log,
                        traces_char, simple_log_char, multiprocess=True, mp_technique='pool'):

        sum_uniq = 0
        zeros = 0
        sum_ent_att = 0
        sum_ent_trace = 0
        unique_match = False
        matches_list = []
        ent_list_att = []
        ent_list_trace = []
        result_dict = {}
        candidates = []
        len_candidates = 0

        if (bk_type == "multiset") and existence_based:
            cand_seq = self.get_sub_seq(traces_char, bk_length, multiprocess=multiprocess)
            candidates, len_candidates = self.get_multiset_of_sequences(cand_seq)

        elif (bk_type == "sequence") and existence_based:
            candidates = self.get_sub_seq(traces_char, bk_length, multiprocess= multiprocess)
            len_candidates = len(candidates)

        elif (bk_type == "multiset") and not existence_based:
            cand_seq = itertools.product(uniq_act, repeat=bk_length)
            cand_mult_base = copy.deepcopy(cand_seq)
            candidates, len_candidates = self.get_multiset_of_sequences(cand_mult_base)

        elif (bk_type == "sequence") and not existence_based:
            cand_seq = itertools.product(uniq_act, repeat=bk_length)
            candidates = list(cand_seq)
            len_candidates = len(candidates)

        elif bk_type == "set":
            candidates = self.find_subsets(uniq_act, bk_length)
            len_candidates = len(candidates)

        print("Candidates size %d" %(len_candidates))

        if multiprocess == True:
            results = []
            if mp_technique == "queue":
                workers_number = os.cpu_count()
                data_chunks = self.chunkIt(candidates, workers_number)
                mp.set_start_method('spawn')
                jobs = []
                for worker in range(workers_number):
                    print("In worker %d out of %d" % (worker + 1, workers_number))
                    q = mp.Queue()
                    p = mp.Process(target=self.foo_worker,
                                   args=(q, data_chunks[worker], tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type))
                    jobs.append(p)
                    p.start()
                    results.append(q.get())
                for job in jobs:
                    job.join()

            elif mp_technique == "pool":
                pool = mp.Pool()
                workers = []
                workers_number = os.cpu_count()
                data_chunks = self.chunkIt(candidates, workers_number)
                for worker in range(workers_number):
                    print("In worker %d out of %d" % (worker + 1, workers_number))
                    workers.append(pool.apply_async(self.foo_worker_without_q, args=(data_chunks[worker], tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type)))
                for work in workers:
                    results.append(work.get())
                pool.close()
                pool.join()


            for result in results:
                for key, value in result.items():
                    if key == 'sum_uniq':
                        sum_uniq += value
                    elif key == 'matches_list':
                        matches_list += value
                    elif key == 'unique_match':
                        unique_match = unique_match or value
                    elif key == 'sum_ent_trace':
                        sum_ent_trace += value
                    elif key == 'ent_list_trace':
                        ent_list_trace += value
                    elif key == 'sum_ent_att':
                        sum_ent_att += value
                    elif key == 'ent_list_att':
                        ent_list_att += value
                    elif key == 'zeros':
                        zeros += value

            result_dict = {'sum_uniq': sum_uniq, 'matches_list': matches_list, 'sum_ent_trace': sum_ent_trace,
                           'zeros': zeros,
                           'ent_list_trace': ent_list_trace, 'sum_ent_att': sum_ent_att, 'ent_list_att': ent_list_att,
                           'unique_match': unique_match}
        else:
            result_dict = self.intermediate_calculator(candidates, tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type)

        cd, td, ad = self.final_calculator(result_dict, measurement_type, len_candidates)

        return cd, td, ad

    def foo_worker(self, q, candidates, tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type):
        result_dict = self.intermediate_calculator(candidates, tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type)
        q.put(result_dict)

    def foo_worker_without_q(self, candidates, tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type):
        result_dict = self.intermediate_calculator(candidates, tuple_log, mult_log, simple_log_char, bk_length,
                                                   unique_match, bk_type)
        return result_dict

    def intermediate_calculator(self, candidates, tuple_log, mult_log, simple_log_char, bk_length, unique_match, bk_type):
        len_cand = len(candidates)
        matches_list = []
        sum_uniq = 0
        sum_ent_trace = 0
        ent_list_trace = []
        sum_ent_att = 0
        ent_list_att = []
        zeros = 0
        sum = 0
        matches = []
        for index, cand in enumerate(candidates):
            print("len %d --> in seq %d of %d" % (bk_length, index, len_cand))
            if bk_type == "sequence":
                sum, matches = self.get_occurances_matches_seq(tuple_log, cand)
            elif bk_type == "multiset":
                sum, matches = self.get_occurances_matches_multiset_n(mult_log, cand)
            elif bk_type == "set":
                sum, matches = self.get_occurances_matches_set(cand, simple_log_char)

            if sum != 0:
                matches_list.append(1 / sum)
                sum_uniq += 1 / sum
                if sum != 1:

                    # entropy traces
                    ent_trace = self.entropy_clculator([case['trace'] for case in matches], 'trace')
                    max_ent_trace = self.max_entropy([case['trace'] for case in matches])
                    sum_ent_trace += ent_trace / max_ent_trace
                    ent_list_trace.append(ent_trace / max_ent_trace)

                    # entropy attribute
                    ent_att = self.entropy_clculator([case['sensitive'] for case in matches], 'att')
                    max_ent_att = self.max_entropy([case['sensitive'] for case in matches])
                    sum_ent_att += ent_att / max_ent_att
                    ent_list_att.append(ent_att / max_ent_att)

                elif sum == 1:
                    unique_match = True
            else:
                zeros += 1

        result_dict = {'sum_uniq': sum_uniq, 'matches_list': matches_list, 'sum_ent_trace': sum_ent_trace,
                       'zeros': zeros,
                       'ent_list_trace': ent_list_trace, 'sum_ent_att': sum_ent_att, 'ent_list_att': ent_list_att,
                       'unique_match': unique_match}
        return result_dict

    def final_calculator(self, result_dict, measurement_type, len_mult):
        cd = 0
        td = 0
        ad = 0
        if measurement_type == "average":
            if result_dict['sum_uniq'] == 0:
                cd = 0
            else:
                cd = result_dict['sum_uniq'] / (len_mult - result_dict['zeros'])
            if result_dict['sum_ent_trace'] == 0 and result_dict['unique_match']:
                td = 1
            if result_dict['sum_ent_att'] == 0 and result_dict['unique_match']:
                ad = 1
            elif len_mult == 0:
                td = 0
                ad = 0
            elif (len_mult - result_dict['zeros']) == 0:
                td = 0
                ad = 0
            else:
                td = 1 - result_dict['sum_ent_trace'] / (len_mult - result_dict['zeros'])
                ad = 1 - result_dict['sum_ent_att'] / (len_mult - result_dict['zeros'])
        elif measurement_type == "worst_case":
            if len(result_dict['matches_list']) != 0:
                cd = max(result_dict['matches_list'])
            else:
                cd = 0
            if len(result_dict['ent_list_trace']) != 0:
                td = 1 - min(result_dict['ent_list_trace'])
            else:
                td = 0
            if len(result_dict['ent_list_att']) != 0:
                ad = 1 - min(result_dict['ent_list_att'])
            else:
                ad = 0

        return cd, td, ad

    def calc(self, log, event_attributes, life_cycle, all_life_cycle, sensitive, time_accuracy, bk_type, measurement_type,
             bk_length, existence_based, multiprocess=True, mp_technique='pool'):

        logsimple, traces, sensitives, df = self.create_simple_log_adv(log, event_attributes, life_cycle, all_life_cycle,
                                                                      sensitive, time_accuracy, 0, 0)
        uniq_activities = self.get_unique_act(traces)
        map_dict_act_chr, map_dict_chr_act, uniq_char = self.map_act_char(uniq_activities)
        simple_log_char, traces_char = self.convert_simple_log_act_to_char(logsimple, map_dict_act_chr)
        uniq_act = self.get_unique_elem(traces_char)
        mult_log = self.get_multiset_log_n(simple_log_char)
        tuple_log = self.get_tuple_event_log(simple_log_char)

        cd, td, ad = self.disclosure_calc(bk_type, uniq_act, measurement_type, bk_length, existence_based, mult_log,
                                         tuple_log,
                                         traces_char, simple_log_char, multiprocess=multiprocess,
                                         mp_technique=mp_technique)
        return cd, td, ad