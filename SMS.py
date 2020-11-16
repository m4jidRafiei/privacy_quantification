import itertools
import numpy as np
from itertools import chain
from collections import Counter
import pyfpgrowth
from multiset import Multiset
import copy

#get_occurances_... are faster than get_occurances_matches_...
#because similar elements are packed in one and counted by Counter

class SMS: #Set-Multiset-Sequence calculator

    def __init__(self):
        self = self


    def create_simple_log(self,log,activity_att):
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
                        activity  = value
                if life_cycle == "complete" or life_cycle=="":
                    trace.append(activity)
            simple_log.append(tuple(trace))

        return simple_log

    def get_unique_act(self, iter):
        act_list = chain.from_iterable(iter)
        return set(act_list)

    def map_act_char(self, traces):
        uniq_act = self.get_unique_act(traces)
        map_dict_act_chr = {}
        map_dict_chr_act = {}
        for index, item in enumerate(uniq_act):
            map_dict_act_chr[item] = chr(index)
            map_dict_chr_act[chr(index)] = item

        return map_dict_act_chr, map_dict_chr_act

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
        simple_log_char = []
        for trace in simple_log:
            trace_string = self.convert_act_to_char(trace, map_dict_act_chr)
            simple_log_char.append(trace_string)
        return simple_log_char

    def convert_simple_log_char_to_act(self, simple_log, map_dict_chr_act):
        simple_log_act = []
        for trace in simple_log:
            trace_act = self.convert_char_to_act(trace, map_dict_chr_act)
            simple_log_act.append(trace_act)
        return simple_log_act

    def create_simple_log_adv(self,log, trace_attributes, life_cycle, all_life_cycle, sensitive_attributes, time_info ,time_accuracy):
        # If time_based is true then the background knowledge type have to be sequence
        time_prefix = ['time:timestamp']
        life_cycle_prefix = ['lifecycle:transition']
        logsimple = {}
        traces = []
        sensitives = {el: [] for el in sensitive_attributes}

        for case_index, case in enumerate(log):
            trace, sens = self.create_trace(case, trace_attributes, life_cycle, all_life_cycle, life_cycle_prefix,
                                            time_prefix, time_info, sensitive_attributes, time_accuracy)
            logsimple[case.attributes["concept:name"]] = {"trace": tuple(trace), "sensitive": sens}
            traces.append(tuple(trace))
            # sample all values for a specific sensitive attribute (key) in dict
            for key in sens.keys():
                # sample all values for a specific sensitive attribute (key) in dict
                sensitives[key].append(sens[key])

        return logsimple, traces, sensitives


    def create_trace(self, case, trace_attributes, life_cycle, all_life_cycle, life_cycle_prefix, time_prefix,time_info,sensitive_attributes,time_accuracy):
        sens = {}
        trace = []
        for event_index, event in enumerate(case):
            simple_attr_temp = []
            life_cycle_value = ''
            event_dict = {}
            for key, value in event.items():
                if time_info and key in time_prefix:
                    if event_index == 0:
                        starttime = value
                        time = 0
                    else:
                        if time_accuracy == "seconds":
                            time = (value - starttime).total_seconds()
                        elif time_accuracy == "minutes":
                            time = (value.replace(second=0, microsecond=0)
                                    - starttime.replace(second=0, microsecond=0)).total_seconds() / 60
                        elif time_accuracy == "hours":
                            time = (value.replace(minute=0, second=0, microsecond=0)
                                    - starttime.replace(minute=0, second=0, microsecond=0)).total_seconds() / 360
                        elif time_accuracy == "days":
                            time = (value.replace(hour=0, minute=0, second=0, microsecond=0)
                                    - starttime.replace(hour=0, minute=0, second=0,
                                                        microsecond=0)).total_seconds() \
                                   / 8640

                if key in trace_attributes:
                    event_dict[key] = value
                if key in sensitive_attributes:
                    sens[key] = value
                if key in life_cycle_prefix:
                    life_cycle_value = value
            if all_life_cycle or (life_cycle_value in life_cycle):
                if len(event_dict) < 2:
                    simple_event = list(event_dict.values())[0]
                else:
                    for att in trace_attributes:
                        if att in event_dict:
                            simple_attr_temp.append(event_dict[att])
                    simple_event = tuple(simple_attr_temp)
                trace.append(simple_event)

        return trace, sens



    def set_simple_log(self,simple_log):
        self.simple_log = simple_log


    def get_unique_elem(self,iter):
        act_list = chain.from_iterable(iter)
        return set(act_list)

    def find_subsets(self,uniq_act, k):
        return list(map(set, itertools.combinations(uniq_act, k)))

    def find_submultisets(self, uniq_act, k):
        return list(map(set, itertools.combinations(uniq_act, k)))


    def get_occurances_set(self,sub_set):
        sum_set = 0
        c = Counter(frozenset(s) for s in self.simple_log)
        for index,items in enumerate(c.items()):
            if sub_set.issubset(items[0]):
                sum_set += items[1]
        return sum_set

    def get_occurances_matches_set(self,sub_set):
        sum_set = 0
        # c = Counter(frozenset(s) for s in self.simple_log)
        matches = []
        for index,items in enumerate(self.simple_log):
            if sub_set.issubset(items):
                sum_set += 1
                matches.append(items)
        return sum_set,matches

    def get_multiset_log(self,alist):
        mult_log = []
        for s in alist:
            mult_s = Counter(s)
            # mult_log.append(mult_s.items())
            dict = mult_s.items()
            mult_log.append(set(dict))
        return mult_log


    def get_multiset_log_n(self,alist):
        mult_log = []
        for s in alist:
            mult_log.append(Multiset(s))
        return mult_log

    def get_occurances_multiset(self,sub_mult):
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
        return sum_mult_count,matches


    def get_occurances_matches_multiset_n(self, mult_log, sub_mult):
        sum_mult_count = 0
        matches = []
        for items in mult_log:
            if sub_mult._issubset(items,False):
                sum_mult_count += 1
                matches.append(items)
        return sum_mult_count,matches

    def get_set_mult(self,mult):
        set = {}
        for items in mult:
            set.add(items[0])
        return set

    def is_subsequence(self,x,y):
        """Test whether x is a subsequence of y"""
        x = list(x)
        for letter in y:
            if x and x[0] == letter:
                x.pop(0)
        return not x


    def get_occurances_seq(self,sub_seq):
        sum_seq = 0
        tuple_list = map(tuple, self.simple_log)
        c = Counter(tuple_list)
        for items in c.items():
            if self.is_subsequence(sub_seq, items[0]):
                sum_seq += items[1]
        return sum_seq

    def get_tuple_event_log(self):
        tuple_event_log = []
        for items in self.simple_log:
            tuple_event_log.append(tuple(items))
        return tuple_event_log

    def get_occurances_matches_seq(self,tuple_log,sub_seq):
        sum_seq = 0
        matches =[]
        for items in tuple_log:
            if self.is_subsequence(sub_seq, items):
                sum_seq += 1
                matches.append(items)
        return sum_seq,matches

    def entropy_clculator(self,matched_list):
        tuple_list = map(tuple, matched_list)
        c = Counter(tuple_list)
        entropy = 0
        for items in c.items():
            pr = items[1]/len(matched_list)
            entropy += -pr*np.log2(pr)
        return entropy

    def max_entropy(self,matched_list):
        entropy = 0
        for items in matched_list:
            pr = 1/len(matched_list)
            entropy += -pr*np.log2(pr)
        return entropy

    def get_first_last_act_set(self,simple_log):
        first_act = [item[0] for item in simple_log]
        last_act = [item[len(item)-1] for item in simple_log]
        return set(first_act),set(last_act)

    def get_seq_patterns(self,simple_log,length):
        patterns = pyfpgrowth.find_frequent_patterns(simple_log, 0)
        seq = []
        for item in patterns.keys():
            if len(item) == length:
                seq.append(item)
        return seq

    def get_sub_seq(self,simple_log,length):
        sub_seqs = []
        for item in simple_log:
            indexes = [i for i in range(len(item))]
            sub_indexes = self.find_subsets(indexes,length)
            for sub_index in sub_indexes:
                list_sub_index = sorted(list(sub_index))
                sub_seq = [item[index] for index in list_sub_index]
                if sub_seq not in sub_seqs:
                    sub_seqs.append(sub_seq)
        return sub_seqs

    def get_sub_seq_t(self,simple_log,length):
        sub_seqs = []
        for item in simple_log:
            indexes = [i for i in range(len(item))]
            sub_indexes = self.find_subsets(indexes,length)
            for sub_index in sub_indexes:
                list_sub_index = sorted(list(sub_index))
                sub_seq = [item[index] for index in list_sub_index]
                if tuple(sub_seq) not in sub_seqs:
                    sub_seqs.append(tuple(sub_seq))
        return tuple(sub_seqs)


    def get_sub_mult(self,simple_log_mult,length):
        sub_mults = []
        for item in simple_log_mult:
            sub_mult = self.find_submultisets(item,length)
            for item in sub_mult:
                if item not in sub_mults:
                    sub_mults.append(item)
        return sub_mults

    def disclosure_calc(self, bk_type, uniq_act,measurement_type, file_name, bk_length, existence_based, simple_log, multiset_log):

        f = open(file_name, "a")

        sum_uniq = 0
        cd = 0
        td = 0
        zeros = 0
        sum = 0
        sum_ent = 0
        unique_match = False
        max_matches = 0
        min_ent = 1
        matches_list =[]
        ent_list = []

        if (bk_type == "mult" or bk_type=="seq") and existence_based:
            cand_seq = self.get_sub_seq(simple_log, bk_length)
            cand_multiset = self.get_multiset_log_n(cand_seq)
            len_mult = len(cand_multiset)

        elif (bk_type == "mult" or bk_type=="seq") and not existence_based:
            cand_seq = itertools.product(uniq_act, repeat=bk_length)
            seq_mult = itertools.product(uniq_act, repeat=bk_length)
            cand_multiset = self.get_multiset_log_n(seq_mult)
            len_mult = len(cand_multiset)

        if bk_type == "set":
            cand_set = self.find_subsets(uniq_act, bk_length)
            for sub_set in cand_set:
                sum, matches = self.get_occurances_matches_set(sub_set)
                if sum != 0:
                    matches_list.append(1 / sum)
                    sum_uniq += 1 / sum
                    if sum != 1:
                        ent = self.entropy_clculator(matches)
                        max_ent = self.max_entropy(matches)
                        sum_ent += ent / max_ent
                        ent_list.append(ent / max_ent)
                    elif sum == 1:
                        unique_match = True
                else:
                    zeros += 1
            if measurement_type == "average":
                if sum_uniq == 0:
                    cd = 0
                else:
                    cd = sum_uniq / (len(cand_set) - zeros)
                if sum_ent == 0 and unique_match:
                    td = 1
                elif (len(cand_set) - zeros) == 0:
                    td = 0
                elif len(cand_set) == 0:
                    td = 0
                else:
                    td = 1 - sum_ent / (len(cand_set) - zeros)
            elif measurement_type == "worst_case":
                if len(matches_list) != 0:
                    cd = max(matches_list)
                else:
                    cd = 0
                if len(ent_list) != 0:
                    td = 1 - min(ent_list)
                else:
                    td = 0

            print("Set ---len %d---cd %0.3f---td %0.3f" % (bk_length, cd, td))
            f.write("set,len,%d,cd,%0.3f,td,%0.3f\n" % (bk_length, cd, td))
            f.close()

        elif bk_type == "mult":
            for counter, sub_mult in enumerate(cand_multiset):
                print("len %d --> in mult %d of %d" % (bk_length, counter, len_mult))
                sum, matches = self.get_occurances_matches_multiset_n(multiset_log, sub_mult)
                if sum != 0:
                    matches_list.append(1 / sum)
                    sum_uniq += 1 / sum
                    if sum != 1:
                        ent = self.entropy_clculator(matches)
                        max_ent = self.max_entropy(matches)
                        sum_ent += ent / max_ent
                        ent_list.append(ent / max_ent)
                    elif sum == 1:
                        unique_match = True
                else:
                    zeros += 1
            if measurement_type == "average":
                if sum_uniq == 0:
                    cd = 0
                else:
                    cd = sum_uniq / (len_mult - zeros)
                if sum_ent == 0 and unique_match:
                    td = 1
                elif (len_mult - zeros) == 0:
                    td = 0
                elif len_mult == 0:
                    td = 0
                else:
                    td = 1 - sum_ent / (len_mult - zeros)
            elif measurement_type == "worst_case":
                if len(matches_list) != 0:
                    cd = max(matches_list)
                else:
                    cd = 0
                if len(ent_list) != 0:
                    td = 1 - min(ent_list)
                else:
                    td = 0

            print("Mul ---len %d---cd %0.3f---td %0.3f" % (bk_length, cd, td))
            f.write("mult,len,%d,cd,%0.3f,td,%0.3f\n" % (bk_length, cd, td))
            f.close()


        elif bk_type == "seq":
            in_loop = False
            for index, sub_seq in enumerate(cand_seq):
                print("len %d --> in seq %d of %d" % (bk_length, index, len_mult))
                in_loop = True
                sum, matches = self.get_occurances_matches_seq(simple_log, sub_seq)
                if sum != 0:
                    matches_list.append(1/sum)
                    sum_uniq += 1 / sum
                    if sum != 1:
                        ent = self.entropy_clculator(matches)
                        max_ent = self.max_entropy(matches)
                        sum_ent += ent / max_ent
                        ent_list.append(ent / max_ent)
                    elif sum == 1:
                        unique_match = True
                else:
                    zeros += 1
            if measurement_type == "average":
                if sum_uniq == 0:
                    cd = 0
                else:
                    cd = sum_uniq / ((index + 1) - zeros)
                if sum_ent == 0 and unique_match:
                    td = 1
                elif not in_loop:
                    td = 0
                elif ((index + 1) - zeros) == 0:
                    td = 0
                else:
                    td = 1 - sum_ent / ((index + 1) - zeros)
            elif measurement_type == "worst_case":
                if len(matches_list) != 0:
                    cd = max(matches_list)
                else:
                    cd = 0
                if len(ent_list) != 0:
                    td = 1 - min(ent_list)
                else:
                    td = 0
            print("Seq ---len %d---cd %0.3f---td %0.3f \n" % (bk_length, cd, td))
            f.write("seq,len,%d,cd,%0.3f,td,%0.3f\n" % (bk_length, cd, td))
            f.close()

