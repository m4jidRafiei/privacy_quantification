from SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time


existence_based =  True  #it is faster when there is no super long traces in the event log
measurement_type = "average"  #average or worst_case
sensitive = []
time_accuracy = "minutes"
time_info = False
trace_attributes = ['concept:name', 'lifecycle:transition']
#these life cycles are applied only when all_lif_cycle = False
life_cycle = ['complete', '', 'COMPLETE']
#when life cycle is in trace attributes then all_life_cycle has to be True
all_life_cycle = True

event_log = "./event_logs/Sepsis Cases - Event Log.xes"
log = xes_importer_factory.apply(event_log)

sms = SMS()
# simple_log = sms.create_simple_log(log,["concept:name", "lifecycle:transition"])
logsimple, traces, sensitives = sms.create_simple_log_adv(log,trace_attributes,life_cycle,all_life_cycle,sensitive,time_info,time_accuracy)
sms.set_simple_log(traces)

multiset_log = sms.get_multiset_log_n(traces)

# multiset_log1 = sms.get_multiset_log(simple_log)

uniq_act = sms.get_unique_elem(traces)
print(uniq_act)

start_time = time.time()
file_name =  event_log[0:-4]+"_1"+".csv"

min_len = min(len(uniq_act),3)
for i in range(1,min_len+1):
    sms.disclosure_calc("set",uniq_act,measurement_type,file_name, i, existence_based,traces,multiset_log)
    sms.disclosure_calc("mult", uniq_act, measurement_type, file_name, i, existence_based, traces, multiset_log)
    sms.disclosure_calc("seq", uniq_act, measurement_type, file_name, i, existence_based, traces, multiset_log)
