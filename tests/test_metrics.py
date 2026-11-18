import unittest
import pandas as pd
from analysis.metrics import prepare_data, calculate_kpi, daily_active_users

class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame([
            ('u1','2026-06-01','2026-06-01','2026-06-01 10:00',1,'Europe','PC','Organic',1,30,2,0),
            ('u1','2026-06-01','2026-06-02','2026-06-02 10:00',2,'Europe','PC','Organic',1,40,3,1),
            ('u2','2026-06-01','2026-06-01','2026-06-01 11:00',3,'Asia','iOS','Search',1,20,1,0),
        ],columns=['user_id','registration_date','event_date','session_start','session_id','region','platform','traffic_source','session_count','session_duration_minutes','action_count','days_since_registration'])
        self.df=prepare_data(self.df)

    def test_kpis(self):
        k=calculate_kpi(self.df,'2026-06-01','2026-06-02')
        self.assertEqual((k['players'],k['sessions'],k['mean_dau']),(2,3,1.5))
    def test_daily(self):
        self.assertEqual(daily_active_users(self.df)['dau'].tolist(),[2,1])
    def test_duplicate_rejected(self):
        d=pd.concat([self.df,self.df.iloc[[0]]])
        with self.assertRaises(ValueError): prepare_data(d)

if __name__=='__main__': unittest.main()
