"""Experimental, non-authoritative BayesianRidge score calibration."""
from __future__ import annotations
import csv
import math
from pathlib import Path
MIN_LABELLED_ROWS=30
FEATURES=("critical_count","high_count","medium_count","graph_defects","failure_coverage","risk_index","command_risk_count")

def load_labelled(path):
    rows=list(csv.DictReader(Path(path).open(newline="",encoding="utf-8")));valid=[]
    for row in rows:
        if not row.get("human_quality_score"):continue
        valid.append(([float(row[x]) for x in FEATURES],float(row["human_quality_score"])))
    return valid

def run(path,minimum_rows=MIN_LABELLED_ROWS):
    rows=load_labelled(path)
    if len(rows)<minimum_rows:return {"enabled":False,"reason":f"At least {minimum_rows} legitimate labelled rows are required; found {len(rows)}.","authoritative":False}
    try:
        import numpy as np
        from sklearn.linear_model import BayesianRidge
        from sklearn.metrics import mean_absolute_error,mean_squared_error
        from sklearn.model_selection import train_test_split
    except ImportError:return {"enabled":False,"reason":"scikit-learn and NumPy are not installed.","authoritative":False}
    x=np.asarray([r[0] for r in rows]);y=np.asarray([r[1] for r in rows]);x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=.25,random_state=42);model=BayesianRidge().fit(x_train,y_train);pred,std=model.predict(x_test,return_std=True)
    return {"enabled":True,"experimental":True,"authoritative":False,"training_rows":len(x_train),"held_out_rows":len(x_test),"mae":round(float(mean_absolute_error(y_test,pred)),3),"rmse":round(math.sqrt(float(mean_squared_error(y_test,pred))),3),"mean_prediction_std":round(float(std.mean()),3)}
