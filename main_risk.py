from datetime import datetime
from p_privacy_qt.SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory

if __name__ == '__main__':
    existence_based =  False  #it is faster when there is no super long traces in the event log
    measurement_type = "average"  #average or worst_case
    sensitive = ['Diagnose'] #attribute disclosure (ad) is calcualted for this attribute(s)
    event_attributes = ['concept:name'] #to simplify the traces
    #time_accuracy is needed only when time is included in the event_attributes
    time_accuracy = "hours" # original, seconds, minutes, hours, days
    life_cycle = ['complete', '', 'COMPLETE'] #these life cycles are applied only when all_lif_cycle = Fals
    all_life_cycle = True #when life cycle is in trace attributes then all_life_cycle has to be True
    event_log = "./event_logs/Sepsis Cases - Event Log.xes"
    log = xes_importer_factory.apply(event_log)
    bk_type = 'sequence' #set,multiset,sequence
    bk_length = 3 #int
    multiprocess = True
    mp_technique = 'pool' #pool or queue

    sms = SMS()
    logsimple, traces, sensitives, df = sms.create_simple_log_adv(log,event_attributes,life_cycle,all_life_cycle,sensitive,time_accuracy,0,0)
    uniq_activities = sms.get_unique_act(traces)
    map_dict_act_chr,map_dict_chr_act, uniq_char = sms.map_act_char(uniq_activities)

    simple_log_char, traces_char = sms.convert_simple_log_act_to_char(logsimple,map_dict_act_chr)
    # sms.set_simple_log(traces_char)
    uniq_act = sms.get_unique_elem(traces_char)
    mult_log = sms.get_multiset_log_n(simple_log_char)
    tuple_log = sms.get_tuple_event_log(simple_log_char)
    start = datetime.now()
    cd, td, ad = sms.disclosure_calc(bk_type,uniq_act,measurement_type, bk_length, existence_based, mult_log, tuple_log, traces_char, simple_log_char, multiprocess=multiprocess, mp_technique=mp_technique)
    end = datetime.now() - start
    print("%s ---len %d---cd %0.3f---td %0.3f---ad %0.3f" % (bk_type, bk_length, cd, td, ad))
    print(end)