from p_privacy_qt.SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time


existence_based =  True  #it is faster when there is no super long traces in the event log
measurement_type = "worst_case"  #average or worst_case
sensitive = []
#is needed only when time is included in the event_attributes
time_accuracy = "hours" # original, seconds, minutes, hours, days
event_attributes = ['concept:name']
#these life cycles are applied only when all_lif_cycle = False
life_cycle = ['complete', '', 'COMPLETE']
#when life cycle is in trace attributes then all_life_cycle has to be True
all_life_cycle = True

event_log = "./event_logs/running_example.xes"
log = xes_importer_factory.apply(event_log)

bk_type = 'set' #set,multiset,sequence
bk_length = 2 #int

sms = SMS()
# simple_log = sms.create_simple_log(log,["concept:name", "lifecycle:transition"])
logsimple, traces, sensitives = sms.create_simple_log_adv(log,event_attributes,life_cycle,all_life_cycle,sensitive,time_accuracy)

map_dict_act_chr,map_dict_chr_act = sms.map_act_char(traces)
simple_log_char_1 = sms.convert_simple_log_act_to_char(traces,map_dict_act_chr)

sms.set_simple_log(simple_log_char_1)

multiset_log = sms.get_multiset_log_n(simple_log_char_1)

# multiset_log1 = sms.get_multiset_log(simple_log)

uniq_act = sms.get_unique_elem(simple_log_char_1)

start_time = time.time()

# min_len = min(len(uniq_act),3)

cd, td = sms.disclosure_calc(bk_type,uniq_act,measurement_type, bk_length, existence_based,simple_log_char_1,multiset_log)

print("%s ---len %d---cd %0.3f---td %0.3f" % (bk_type, bk_length, cd, td))
