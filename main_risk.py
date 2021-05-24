from datetime import datetime
from p_privacy_qt.SMS import SMS
from pm4py.objects.log.importer.xes import factory as xes_importer_factory

if __name__ == '__main__':
    existence_based = False  # it is faster when there is no super long traces in the event log
    measurement_type = "worst_case"  # average or worst_case
    sensitive = ['Diagnose']  # attribute disclosure (ad) is calcualted for this attribute(s)
    event_attributes = ['concept:name']  # to simplify the traces
    # time_accuracy is needed only when time is included in the event_attributes
    time_accuracy = "minutes"  # original, seconds, minutes, hours, days
    life_cycle = ['complete', '', 'COMPLETE']  # these life cycles are applied only when all_lif_cycle = False
    all_life_cycle = True  # when life cycle is in trace attributes then all_life_cycle has to be True
    event_log = "./event_logs/BPI Challenge 2017_App_minutes_6_60_0.2_set.xes"
    log = xes_importer_factory.apply(event_log)
    bk_type = 'set'  # set,multiset,sequence
    bk_length = 6  # int
    multiprocess = True
    mp_technique = 'pool'  # pool or queue (pool is always faster!)
    sms = SMS()
    all_uniques = []
    # for x in range(bk_length):
    cd, td, ad, uniq_matched_cases = sms.calc(log, event_attributes, life_cycle, all_life_cycle, sensitive, time_accuracy,
                              bk_type, measurement_type, bk_length, existence_based, multiprocess=multiprocess, mp_technique=mp_technique )
    all_uniques.append(uniq_matched_cases)

    print("%s ---len %d---cd %0.3f---td %0.3f---ad %0.3f---%d" % (bk_type, bk_length, cd, td, ad, len(uniq_matched_cases)))
    print("done")
