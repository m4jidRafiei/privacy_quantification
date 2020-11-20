from p_privacy_qt.SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time
from p_privacy_qt.EMD import EMD

# simple_log = (['a','a','c'], ['a','b','c'], ['a', 'a', 'a', 'a', 'c', 'b'], ['d','b','c'], ['a', 'a', 'b', 'd'],['a', 'a', 'd', 'b'])

sensitive = []
time_accuracy = "minutes"
time_info = False
trace_attributes = ['concept:name']
#these life cycles are applied only when all_lif_cycle = False
life_cycle = ['complete', '', 'COMPLETE']
#when life cycle is in trace attributes then all_life_cycle has to be True
all_life_cycle = True # True will ignore the transitions specified in life_cycle

original_event_log = "./event_logs/" + "BPI_Challenge_2012_APP.xes"
privacy_aware_log = "./event_logs/"+ "BPI_Challenge_2012_APP anon relative.xes"

original_log = xes_importer_factory.apply(original_event_log)
privacy_log = xes_importer_factory.apply(privacy_aware_log)

sms = SMS()
logsimple, traces, sensitives = sms.create_simple_log_adv(original_log,trace_attributes,life_cycle,all_life_cycle,sensitive,time_info,time_accuracy)
logsimple_2, traces_2, sensitives_2 = sms.create_simple_log_adv(privacy_log,trace_attributes,life_cycle,all_life_cycle,sensitive,time_info,time_accuracy)

#log 1 convert to char
map_dict_act_chr,map_dict_chr_act = sms.map_act_char(traces)
simple_log_char_1 = sms.convert_simple_log_act_to_char(traces,map_dict_act_chr)

#log 2 convert to char
# map_dict_act_chr_2,map_dict_chr_act_2 = sms.map_act_char(traces_2)
simple_log_char_2 = sms.convert_simple_log_act_to_char(traces_2,map_dict_act_chr)

start_time = time.time()

my_emd = EMD()
# log_freq_1, log_only_freq_1 = my_emd.log_freq(traces)
# log_freq_2 , log_only_freq_2 = my_emd.log_freq(traces_2)

log_freq_1, log_only_freq_1 = my_emd.log_freq(simple_log_char_1)
log_freq_2 , log_only_freq_2 = my_emd.log_freq(simple_log_char_2)

cost_lp = my_emd.emd_distance_pyemd(log_only_freq_1,log_only_freq_2,log_freq_1,log_freq_2)
# cost_lp = my_emd.emd_distance(log_freq_1,log_freq_2)

data_utility = 1 - cost_lp
print("data_utility---%0.3f" %(data_utility))
