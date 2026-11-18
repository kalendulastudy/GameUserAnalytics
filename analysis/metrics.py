"""Pure aggregation functions for the educational gaming user analytics project."""
from __future__ import annotations
import pandas as pd

COLUMNS = ['user_id', 'registration_date', 'event_date', 'session_start',
           'session_id', 'region', 'platform', 'traffic_source',
           'session_count', 'session_duration_minutes', 'action_count',
           'days_since_registration']


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = set(COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f'Missing columns: {sorted(missing_columns)}')
    out = df.copy()
    for col in ['registration_date', 'event_date', 'session_start']:
        out[col] = pd.to_datetime(out[col], errors='coerce')
    if out[COLUMNS].isna().any().any():
        raise ValueError('Dataset contains missing or invalid required values')
    if out['session_id'].duplicated().any():
        raise ValueError('session_id must be unique')
    if (out['session_duration_minutes'] <= 0).any() or (out['action_count'] < 0).any():
        raise ValueError('Invalid duration or action count')
    if (out['event_date'] < out['registration_date']).any():
        raise ValueError('A session cannot occur before player registration')
    return out


def filter_rows(df: pd.DataFrame, start, end, regions, platforms, sources):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    valid = (df['event_date'].dt.normalize().between(start, end) &
             df['region'].isin(regions) &
             df['platform'].isin(platforms) &
             df['traffic_source'].isin(sources))
    return df.loc[valid].copy()


def calculate_kpi(df: pd.DataFrame, start=None, end=None) -> dict:
    if df.empty:
        return dict(players=0, sessions=0, mean_dau=0, mean_duration=0, repeat_share=0)
    days = df['event_date'].dt.normalize()
    dau = df.groupby(days)['user_id'].nunique()
    if start is not None and end is not None:
        index = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq='D')
        dau = dau.reindex(index, fill_value=0)
    unique_day_counts = df.groupby('user_id')['event_date'].nunique()
    return dict(players=int(df['user_id'].nunique()),
                sessions=int(df['session_id'].nunique()),
                mean_dau=round(float(dau.mean()), 1),
                mean_duration=round(float(df['session_duration_minutes'].mean()), 1),
                repeat_share=round(float((unique_day_counts >= 2).mean()*100), 1))


def daily_active_users(df: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    dau = df.groupby(df.event_date.dt.normalize())['user_id'].nunique()
    if start is not None and end is not None:
        dau = dau.reindex(pd.date_range(start, end), fill_value=0)
    return dau.rename_axis('date').rename('dau').reset_index()


def breakdown(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.groupby(col, as_index=False).agg(players=('user_id', 'nunique'),
                 sessions=('session_id','nunique'),
                 mean_duration=('session_duration_minutes','mean'),
                 actions=('action_count','sum')).sort_values('players', ascending=False)


def user_scatter(df: pd.DataFrame, max_points: int=1200) -> pd.DataFrame:
    x = df.groupby('user_id',as_index=False).agg(avg_duration=('session_duration_minutes','mean'),
            avg_actions=('action_count','mean'), sessions=('session_id','nunique'),
            region=('region','first'))
    return x.sample(n=min(max_points,len(x)), random_state=42) if len(x)>max_points else x
