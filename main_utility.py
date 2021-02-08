
import time
from p_privacy_qt.EMD import EMD

# simple_log = (['a','a','c'], ['a','b','c'], ['a', 'a', 'a', 'a', 'c', 'b'], ['d','b','c'], ['a', 'a', 'b', 'd'],['a', 'a', 'd', 'b'])

sensitive = []
time_accuracy = "hours" # original, seconds, minutes, hours, days
event_attributes = ['concept:name']
#these life cycles are applied only when all_lif_cycle = False
life_cycle = ['complete', '', 'COMPLETE']
#when life cycle is in trace attributes then all_life_cycle has to be True
all_life_cycle = True # True will ignore the transitions specified in life_cycle

original_event_log = "./event_logs/" + "Sepsis Cases - Event Log.xes"
privacy_aware_log = "./event_logs/"+ "Sepsis Cases - Event Log.xes"

emd = EMD()
data_utility = emd.data_utility(original_event_log,privacy_aware_log,event_attributes,life_cycle,all_life_cycle,sensitive,time_accuracy)
print("data_utility# %0.3f" %(data_utility))
