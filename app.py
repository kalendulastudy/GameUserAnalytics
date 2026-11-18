"""Lab 10: Interactive dashboard for game-user behavior (synthetic dataset)."""
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

from analysis.metrics import (prepare_data, filter_rows, calculate_kpi,
                              daily_active_users, breakdown, user_scatter)

st.set_page_config(page_title='Game User Analytics', layout='wide', page_icon='🎮')

@st.cache_data(show_spinner=False)
def load_data():
    path = Path(__file__).resolve().parent / 'data' / 'raw' / 'user_sessions.csv'
    return prepare_data(pd.read_csv(path))

all_data = load_data()
first, last = all_data.event_date.min().date(), all_data.event_date.max().date()

st.title('🎮 Игровая аналитика: пользовательская активность')
st.caption('ЛР №10 · Синтетические данные · Основа — датасет ЛР №9 · Показатели динамически пересчитываются при фильтрации')

def reset_all():
    for key in ['regions', 'platforms', 'sources', 'period']:
        st.session_state.pop(key, None)

def on_region_change():
    st.session_state.pop('platforms', None)
    st.session_state.pop('sources', None)

def on_platform_change():
    st.session_state.pop('sources', None)

st.sidebar.header('Фильтры')
st.sidebar.button('Сбросить фильтры', on_click=reset_all, use_container_width=True)
period = st.sidebar.date_input('Период активности', value=(first,last),min_value=first,max_value=last, key="period")
if isinstance(period,tuple) and len(period)==2:
    start,end=period
else:
    start,end=first,last
if start>end: start,end=end,start

period_df=all_data[all_data.event_date.dt.date.between(start,end)]

# Cascading filtering: selected regions restrict available platform choices,
# and the chosen platforms restrict traffic-source choices.
region_opts=sorted(period_df.region.unique().tolist())
regions=st.sidebar.multiselect('Регионы',region_opts,default=region_opts, key='regions',on_change=on_region_change)
region_df=period_df[period_df.region.isin(regions)]
platform_opts=sorted(region_df.platform.unique().tolist())
platforms=st.sidebar.multiselect('Платформы',platform_opts,default=platform_opts,key='platforms',on_change=on_platform_change)
platforms=[x for x in platforms if x in platform_opts]
platform_df=region_df[region_df.platform.isin(platforms)]
source_opts=sorted(platform_df.traffic_source.unique().tolist())
sources=st.sidebar.multiselect('Источники трафика',source_opts,default=source_opts,key='sources')
sources=[x for x in sources if x in source_opts]

st.sidebar.caption('Каскад: регион → платформа → источник. Кнопка сбрасывает также выбранные даты.')

df=filter_rows(all_data,start,end,regions,platforms,sources)
kpi=calculate_kpi(df,start,end)
if df.empty:
    st.warning('В выбранных фильтрах нет записей. Измените условия или сбросьте фильтры.')
    st.stop()

c1,c2,c3,c4=st.columns(4)
c1.metric('Игроков',f'{kpi["players"]:,}'.replace(',',' '))
c2.metric('Сессий',f'{kpi["sessions"]:,}'.replace(',',' '))
c3.metric('Средний DAU',f'{kpi["mean_dau"]:.1f}')
c4.metric('Средняя длительность',f'{kpi["mean_duration"]:.1f} мин')

st.subheader('Динамика и аудитория')
l,r=st.columns([1.45,1])
with l:
    dau=daily_active_users(df,start,end)
    f=px.line(dau,x='date',y='dau',markers=True,
              labels={'date':'Дата','dau':'Активных игроков'},title='DAU по дням')
    f.update_traces(line_color='#2563eb',marker_size=4)
    st.plotly_chart(f,use_container_width=True)
with r:
    levels=['region','platform','traffic_source']
    options={'region':'Регионы','platform':'Платформы','traffic_source':'Источники трафика'}
    depth=st.selectbox('Уровень детализации (drill-down)',levels,format_func=lambda x:options[x])
    br=breakdown(df,depth)
    f=px.bar(br,x=depth,y='players',color=depth,title='Уникальные игроки по сегментам',
             labels={depth:options[depth],'players':'Игроков'})
    f.update_layout(showlegend=False)
    st.plotly_chart(f,use_container_width=True)

l,r=st.columns(2)
with l:
    segments=breakdown(df,'platform')
    fig=px.pie(segments,names='platform',values='sessions',hole=.53,title='Доли сессий по платформам')
    st.plotly_chart(fig,use_container_width=True)
with r:
    hm=df.pivot_table(index='traffic_source',columns='platform',values='session_id',aggfunc='nunique',fill_value=0)
    fig=px.imshow(hm,text_auto=True,aspect='auto',labels=dict(x='Платформа',y='Источник трафика',color='Сессий'),title='Матрица: источники × платформы',color_continuous_scale='Blues')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Поведение игроков')
l,r=st.columns(2)
with l:
    fig=px.histogram(df,x='session_duration_minutes',nbins=25,
                     labels={'session_duration_minutes':'Минут на сессию'},title='Распределение длительности сессий')
    fig.update_layout(yaxis_title='Число сессий')
    st.plotly_chart(fig,use_container_width=True)
with r:
    sample=user_scatter(df)
    fig=px.scatter(sample,x='avg_duration',y='avg_actions',color='region',
                   hover_data=['sessions'],opacity=.65,
                   labels={'avg_duration':'Средняя длительность, мин','avg_actions':'Действий за сессию','region':'Регион'},
                   title='Длительность и действия: выборка игроков')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Сводка по сегментам')
metric_table=breakdown(df,'traffic_source').rename(columns={'traffic_source':'Источник','players':'Игроков','sessions':'Сессий','mean_duration':'Средняя длительность (мин)','actions':'Действий'})
st.dataframe(metric_table.style.format({'Средняя длительность (мин)':'{:.1f}'}),use_container_width=True,hide_index=True)
st.download_button('Экспортировать отфильтрованные сессии (CSV)',
    data=df.to_csv(index=False).encode('utf-8-sig'),file_name='filtered_sessions.csv',mime='text/csv')
st.caption('Важно: средний DAU — среднее уникальных активных игроков за календарный день выбранного периода; уникальные игроки считаются отдельно в каждом сегменте. Синтетические данные не описывают реальную аудиторию.')
