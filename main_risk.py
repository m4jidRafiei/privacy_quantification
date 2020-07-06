from SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time


existence_based =  True  #it is faster when there is no super long traces in the event log
measurement_type = "average"  #average or worst_case

event_log = "./event_logs/running_example.xes"
log = xes_importer_factory.apply(event_log)

sms = SMS()
simple_log = sms.create_simple_log(log,["concept:name", "lifecycle:transition"])
sms.set_simple_log(simple_log)

multiset_log = sms.get_multiset_log_n(simple_log)

uniq_act = sms.get_unique_act(simple_log)
print(uniq_act)

start_time = time.time()
file_name =  event_log[0:-4]+"_1"+".csv"

min_len = min(len(uniq_act),8)
for i in range(1,min_len+1):

    sms.disclosure_calc("set",uniq_act,measurement_type,file_name, i, existence_based,simple_log,multiset_log)
    sms.disclosure_calc("mult", uniq_act, measurement_type, file_name, i, existence_based, simple_log, multiset_log)
    sms.disclosure_calc("seq", uniq_act, measurement_type, file_name, i, existence_based, simple_log, multiset_log)


print("--- %s seconds ---" % (time.time() - start_time))


