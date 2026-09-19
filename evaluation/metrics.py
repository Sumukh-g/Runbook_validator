from dataclasses import dataclass
@dataclass(frozen=True)
class Metrics:
    true_positive:int; false_positive:int; false_negative:int; precision:float; recall:float; f1:float
def calculate(expected:set[str],actual:set[str])->Metrics:
    tp=len(expected&actual); fp=len(actual-expected); fn=len(expected-actual)
    precision=tp/(tp+fp) if tp+fp else 0.; recall=tp/(tp+fn) if tp+fn else 0.; f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    return Metrics(tp,fp,fn,round(precision,3),round(recall,3),round(f1,3))
