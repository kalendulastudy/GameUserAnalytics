"""Validate raw data and export the clean snapshot for the research repository."""
from pathlib import Path
import pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.metrics import prepare_data, calculate_kpi

root=Path(__file__).resolve().parents[1]
raw=root/'data'/'raw'/'user_sessions.csv'
out=root/'data'/'processed'/'user_sessions_clean.csv'
df=prepare_data(pd.read_csv(raw))
out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(out,index=False,date_format='%Y-%m-%d %H:%M:%S')
print('Данные валидны:',len(df),'сессий,',df.user_id.nunique(),'пользователей')
print('Метрики:',calculate_kpi(df,df.event_date.min(),df.event_date.max()))
print('Очищенная копия:',out)
