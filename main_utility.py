from SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time
from EMD import EMD

# simple_log = (['a','a','c'], ['a','b','c'], ['a', 'a', 'a', 'a', 'c', 'b'], ['d','b','c'], ['a', 'a', 'b', 'd'],['a', 'a', 'd', 'b'])

event_log = "./event_logs/" + "Sepsis Cases - Event Log.xes"
log = xes_importer_factory.apply(event_log)

event_log_2 = "./event_logs/"+ "Sepsis Cases - Event Log.xes"
log_2 = xes_importer_factory.apply(event_log_2)

sms = SMS()
simple_log = sms.create_simple_log(log,["concept:name","lifecycle:transition"])
simple_log_2 = sms.create_simple_log(log_2,["concept:name","lifecycle:transition"])

start_time = time.time()

my_emd = EMD()
log_freq_1, log_only_freq_1 = my_emd.log_freq(simple_log)
log_freq_2 , log_only_freq_2 = my_emd.log_freq(simple_log_2)

cost_lp = my_emd.emd_distance_pyemd(log_only_freq_1,log_only_freq_2,log_freq_1,log_freq_2)
cost = my_emd.emd_distance(log_freq_1,log_freq_2)

data_utility = 1 - cost_lp
print("data_utility---%0.3f" %(data_utility))
