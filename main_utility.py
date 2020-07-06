import itertools
from SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
import time
from EMD import EMD


# simple_log = (['a','a','c'], ['a','a','c'], ['a','b','c'], ['a', 'a', 'a', 'a', 'c', 'b'], ['d','b'], ['a', 'a', 'b', 'd'],['a', 'a', 'd', 'b'])
# simple_log_2 = (['a','a','c'], ['a','a','c'], ['a','b','c'], ['a', 'a', 'a', 'a', 'c', 'b'], ['d','b'], ['a', 'a', 'b', 'd'],['a', 'a', 'd', 'b'])

event_log = "./event_logs/" + "running_example.xes"
log = xes_importer_factory.apply(event_log)

event_log_2 = "./event_logs/"+ "running_example.xes"
log_2 = xes_importer_factory.apply(event_log_2)

sms = SMS()
simple_log = sms.create_simple_log(log,["concept:name","lifecycle:transition"])
simple_log_2 = sms.create_simple_log(log_2,["concept:name","lifecycle:transition"])

start_time = time.time()

emd = EMD()
log_freq_1 = emd.log_freq(simple_log)
log_freq_2 = emd.log_freq(simple_log_2)
distance_df,array = emd.distance_array(log_freq_1,log_freq_2)

cost = emd.emd_distance(log_freq_1,log_freq_2,distance_df)
data_utility = 1 - cost
print("data_utility---%0.3f" %(data_utility))

print("--- %s seconds ---" % (time.time() - start_time))


