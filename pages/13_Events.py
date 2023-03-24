from pyzotero import zotero
import pandas as pd
import streamlit as st
from IPython.display import HTML
import streamlit.components.v1 as components
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
import datetime
import plotly.express as px
import numpy as np
import re
import matplotlib.pyplot as plt
import nltk
nltk.download('all')
from nltk.corpus import stopwords
nltk.download('stopwords')
from wordcloud import WordCloud
from gsheetsdb import connect
import datetime as dt
from urllib.parse import urlparse

st.set_page_config(layout = "centered", 
                    page_title='Intelligence studies network',
                    page_icon="https://images.pexels.com/photos/315918/pexels-photo-315918.png",
                    initial_sidebar_state="auto") 

st.title("Intelligence studies network")
st.header("Events on intelligence")
image = 'https://images.pexels.com/photos/315918/pexels-photo-315918.png'


with st.sidebar:

    st.image(image, width=150)
    st.sidebar.markdown("# Intelligence studies network")
    with st.expander('About'):
        st.write('''This website lists secondary sources on intelligence studies and intelligence history.
        The sources are originally listed in the [Intelligence bibliography Zotero library](https://www.zotero.org/groups/2514686/intelligence_bibliography).
        This website uses [Zotero API](https://github.com/urschrei/pyzotero) to connect the *Intelligence bibliography Zotero group library*.
        To see more details about the sources, please visit the group library [here](https://www.zotero.org/groups/2514686/intelligence_bibliography/library). 
        If you need more information about Zotero, visit [this page](https://www.intelligencenetwork.org/zotero).
        ''')
        components.html(
        """
        <a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
        src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
        © 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
        """
        )
    with st.expander('Source code'):
        st.info('''
        Source code of this app is available [here](https://github.com/YusufAliOzkan/zotero-intelligence-bibliography).
        ''')
    with st.expander('Disclaimer and acknowledgements'):
        st.warning('''
        This website and the Intelligence bibliography Zotero group library do not list all the sources on intelligence studies. 
        The list is created based on the creator's subjective views.
        ''')
        st.info('''
        The following sources are used to collate some of the articles and events: [KISG digest](https://kisg.co.uk/kisg-digests), [IAFIE digest compiled by Filip Kovacevic](https://www.iafie.org/Login.aspx)
        ''')
    with st.expander('Contact us'):
        st.write('If you have any questions or suggestions, please do get in touch with us by filling the form [here](https://www.intelligencenetwork.org/contact-us).')
        st.write('Report your technical issues or requests [here](https://github.com/YusufAliOzkan/zotero-intelligence-bibliography/issues).')

today = dt.date.today()
today2 = dt.date.today().strftime('%d/%m/%Y')
st.write('Today is: '+ str(today2))

# Create a connection object.
conn = connect()

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=10)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

tab1, tab2, tab3 = st.tabs(['Events', 'Conferences','Call for papers'])
with tab1:
    st.header('Events')
    sheet_url = st.secrets["public_gsheets_url"]
    rows = run_query(f'SELECT * FROM "{sheet_url}"')

    data = []
    columns = ['event_name', 'organiser', 'link', 'date', 'venue', 'details']

    # Print results.
    for row in rows:
        data.append((row.event_name, row.organiser, row.link, row.date, row.venue, row.details))

    pd.set_option('display.max_colwidth', None)
    df_gs = pd.DataFrame(data, columns=columns)

    df_gs['date_new'] = pd.to_datetime(df_gs['date'], dayfirst = True).dt.strftime('%d/%m/%Y')
    df_gs['month'] = pd.to_datetime(df_gs['date'], dayfirst = True).dt.strftime('%m')
    df_gs['year'] = pd.to_datetime(df_gs['date'], dayfirst = True).dt.strftime('%Y')
    df_gs['month_year'] = pd.to_datetime(df_gs['date'], dayfirst = True).dt.strftime('%Y-%m')
    df_gs.sort_values(by='date', ascending = True, inplace=True)
    df_gs = df_gs.drop_duplicates(subset=['event_name', 'link', 'date'], keep='first')
    
    df_gs['details'] = df_gs['details'].fillna('No details')
    df_gs = df_gs.fillna('')
    df_gs_plot = df_gs.copy()

    sheet_url_forms = st.secrets["public_gsheets_url_forms"]
    rows = run_query(f'SELECT * FROM "{sheet_url_forms}"')
    data = []
    columns = ['event_name', 'organiser', 'link', 'date', 'venue', 'details']
    # Print results.
    for row in rows:
        data.append((row.Event_name, row.Event_organiser, row.Link_to_the_event, row.Date_of_event, row.Event_venue, row.Details))
    pd.set_option('display.max_colwidth', None)
    df_forms = pd.DataFrame(data, columns=columns)

    df_forms['date_new'] = pd.to_datetime(df_forms['date'], dayfirst = True).dt.strftime('%d/%m/%Y')
    df_forms['month'] = pd.to_datetime(df_forms['date'], dayfirst = True).dt.strftime('%m')
    df_forms['year'] = pd.to_datetime(df_forms['date'], dayfirst = True).dt.strftime('%Y')
    df_forms['month_year'] = pd.to_datetime(df_forms['date'], dayfirst = True).dt.strftime('%Y-%m')
    df_forms.sort_values(by='date', ascending = True, inplace=True)
    df_forms = df_forms.drop_duplicates(subset=['event_name', 'link', 'date'], keep='first')
    
    df_forms['details'] = df_forms['details'].fillna('No details')
    df_forms = df_forms.fillna('')
    df_gs = pd.concat([df_gs, df_forms], axis=0)
    df_gs = df_gs.reset_index(drop=True)
    df_gs = df_gs.drop_duplicates(subset=['event_name', 'link', 'date'], keep='first')
    
    col1, col2 = st.columns(2)

    with col1:
        online_event = st.checkbox('Show online events only')
        if online_event:
            online = ['Online event', 'Hybrid event']
            df_gs = df_gs[df_gs['venue'].isin(online)]
        display = st.checkbox('Show details')      
    
    with col2:
        sort_by = st.radio('Sort by', ['Date', 'Most recently added', 'Organiser'])
        
    st.write('See [📊 Event visuals](#event-visuals)')


    filter = (df_gs['date']>=today)
    filter2 = (df_gs['date']<today)
    df_gs2 = df_gs.loc[filter2]
    df_gs = df_gs.loc[filter]
    if df_gs['event_name'].any() in ("", [], None, 0, False):
        st.write('No upcoming event!')

    if sort_by == 'Most recently added':
        df_gs = df_gs.sort_index(ascending=False)
        df_last = ('['+ df_gs['event_name'] + ']'+ '('+ df_gs['link'] + ')'', organised by ' + '**' + df_gs['organiser'] + '**' + '. Date: ' + df_gs['date_new'] + ', Venue: ' + df_gs['venue'])
        row_nu = len(df_gs.index)
        for i in range(row_nu):
            st.write(''+str(i+1)+') '+ df_last.iloc[i])
            if display:
                st.caption('Details:'+'\n '+ df_gs['details'].iloc[i])

    if sort_by == 'Organiser':
        organisers = df_gs['organiser'].unique()
        organisers = pd.DataFrame(organisers, columns=['Organisers'])
        row_nu_organisers = len(organisers.index)
        for i in range(row_nu_organisers):
            st.markdown('#### '+ organisers['Organisers'].iloc[i])
            # st.subheader(organisers['Organisers'].iloc[i])
            c = organisers['Organisers'].iloc[i]
            df_o = df_gs[df_gs['organiser']==c]
            df_last = ('['+ df_o['event_name'] + ']'+ '('+ df_o['link'] + ')'', organised by ' + '**' + df_o['organiser'] + '**' + '. Date: ' + df_o['date_new'] + ', Venue: ' + df_o['venue'])
            row_nu =len(df_o.index)
            for j in range(row_nu):
                st.write(''+str(j+1)+') ' +df_last.iloc[j])
                df_last.fillna('')
                if display:
                    st.caption('Details:'+'\n '+ df_o['details'].iloc[j])

    if sort_by == 'Date':
        df_gs = df_gs.reset_index(inplace=False)
        df_gs
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        for month in range(1, 13):
            month_str = str(month).zfill(2)
            if month_str in df_gs['month'].values:
                st.markdown(f'#### Events in {months[month-1]}')
                mon = df_gs[df_gs['month']==month_str]
                df_gs1 = (f"[{mon['event_name']}]" + f"({mon['link']})" + f", organised by **{mon['organiser']}**. Date: {mon['date_new']}, Venue: {mon['venue']}")
                df_gs1
                row_nu = len(mon.index)
                for i in range(row_nu):
                    st.write(f"{i+1}) {df_gs1.iloc[i]}")
                    if display:
                        st.caption('Details:'+'\n '+ mon['details'].iloc[i])




    st.header('Past events')
    with st.expander('Expand to see the list'):
        if st.checkbox('Events in 2023', key='2023'):            
            if '2023' in df_gs2['year'].values:
                y2023 = df_gs2[df_gs2['year']=='2023']
                y2023['link'] = y2023['link'].fillna('')
                row_nu2 = len(y2023.index)
                df_gs3 = ('['+ y2023['event_name'] + ']'+ '('+ y2023['link'] + ')'', organised by ' + '**' + y2023['organiser'] + '**' + '. Date: ' + y2023['date_new'] + ', Venue: ' + y2023['venue'])
                row_nu = len(df_gs.index)
                st.write(str(row_nu2) + ' events happened in 2023')
                for i in range(row_nu2):
                    st.write(''+str(i+1)+') '+ df_gs3.iloc[i])
        if st.checkbox('Events in 2022', key='2022'):
            if '2022' in df_gs2['year'].values:
                y2022 = df_gs2[df_gs2['year']=='2022']
                y2022['link'] = y2022['link'].fillna('')
                y2022 = y2022.drop_duplicates(subset=['event_name', 'link', 'date'], keep='first')
                row_nu2 = len(y2022.index)
                df_gs3 = ('['+ y2022['event_name'] + ']'+ '('+ y2022['link'] + ')'', organised by ' + '**' + y2022['organiser'] + '**' + '. Date: ' + y2022['date_new'] + ', Venue: ' + y2022['venue'])
                row_nu = len(df_gs.index)
                st.write(str(row_nu2) + ' events happened in 2022')
                for i in range(row_nu2):
                    st.write(''+str(i+1)+') '+ df_gs3.iloc[i])
    
    st.header('Event visuals')
    ap = ''
    ap2 = ''
    ap3 = ''
    selector = st.checkbox('Select a year')
    year = st.checkbox('Show years only')
    if selector:
        slider = st.slider('Select a year', 2022,2023,2023)
        slider = str(slider)
        df_gs_plot =df_gs_plot[df_gs_plot['year']==slider]
        ap = ' (in ' + slider+')'
    
    if year:
        date_plot=df_gs_plot['year'].value_counts()
        date_plot=date_plot.reset_index()
        date_plot=date_plot.rename(columns={'index':'Year','year':'Count'})
        date_plot=date_plot.sort_values(by='Year')
        fig = px.bar(date_plot, x='Year', y='Count')
        fig.update_xaxes(tickangle=-70)
        fig.update_layout(
            autosize=False,
            width=400,
            height=500)
        fig.update_layout(title={'text':'Events over time' +ap, 'y':0.95, 'x':0.5, 'yanchor':'top'})
        st.plotly_chart(fig, use_container_width = True)
    else:
        date_plot=df_gs_plot['month_year'].value_counts()
        date_plot=date_plot.reset_index()
        date_plot=date_plot.rename(columns={'index':'Date','month_year':'Count'})
        date_plot=date_plot.sort_values(by='Date')
        fig = px.bar(date_plot, x='Date', y='Count')
        fig.update_xaxes(tickangle=-70)
        fig.update_layout(
            autosize=False,
            width=400,
            height=500)
        fig.update_layout(title={'text':'Events over time' +ap, 'y':0.95, 'x':0.5, 'yanchor':'top'})
        st.plotly_chart(fig, use_container_width = True)

    organiser_plot = df_gs_plot['organiser'].value_counts()
    organiser_plot=organiser_plot.reset_index()
    organiser_plot=organiser_plot.rename(columns={'index':'Organiser', 'organiser':'Count'})
    organiser_plot=organiser_plot.sort_values(by='Count', ascending = False)
    organiser_plot_all=organiser_plot.copy()        
    all = st.checkbox('Show all organisers')
    if all:
        organiser_plot=organiser_plot_all
        ap2 = ' (all)'
    else:
        organiser_plot=organiser_plot.head(5)
        ap3 = ' (top 5) '
    fig = px.bar(organiser_plot, x='Organiser', y='Count', color='Organiser')
    fig.update_xaxes(tickangle=-65)
    fig.update_layout(
        autosize=False,
        width=400,
        height=700,
        showlegend=False)
    fig.update_layout(title={'text':'Events by organisers' + ap + ap2 +ap3, 'y':0.95, 'x':0.5, 'yanchor':'top'})
    st.plotly_chart(fig, use_container_width = True)
    with st.expander('See the list of event organisers'):
        row_nu_organiser= len(organiser_plot_all.index)
        organiser_plot_all=organiser_plot_all.sort_values('Organiser', ascending=True)
        for i in range(row_nu_organiser):
            st.caption(organiser_plot_all['Organiser'].iloc[i])


with tab2:
    st.subheader('Conferences')
    sheet_url2 = st.secrets["public_gsheets_url2"]
    rows = run_query(f'SELECT * FROM "{sheet_url2}"')

    data = []
    columns = ['conference_name', 'organiser', 'link', 'date', 'date_end', 'venue', 'details', 'location']

    # Print results.
    for row in rows:
        data.append((row.conference_name, row.organiser, row.link, row.date, row.date_end, row.venue, row.details, row.location))

    pd.set_option('display.max_colwidth', None)
    df_con = pd.DataFrame(data, columns=columns)

    df_con['date_new'] = pd.to_datetime(df_con['date'], dayfirst = True).dt.strftime('%d/%m/%Y')
    df_con['date_new_end'] = pd.to_datetime(df_con['date_end'], dayfirst = True).dt.strftime('%d/%m/%Y')
    df_con.sort_values(by='date', ascending = True, inplace=True)

    df_con['details'] = df_con['details'].fillna('No details')
    df_con['location'] = df_con['location'].fillna('No details')
    
    col1, col2 = st.columns(2)
    with col1:
        display = st.checkbox('Show details', key='conference')
    with col2:
        last_added = st.checkbox('Sort by most recently added', key='conference2')

    filter = (df_con['date_end']>=today)
    df_con = df_con.loc[filter]
    if df_con['conference_name'].any() in ("", [], None, 0, False):
        st.write('No upcoming conference!')

    if last_added:
        df_con = df_con.sort_index(ascending=False)
        df_con1 = ('['+ df_con['conference_name'] + ']'+ '('+ df_con['link'] + ')'', organised by ' + '**' + df_con['organiser'] + '**' + '. Date(s): ' + df_con['date_new'] + ' - ' + df_con['date_new_end'] + ', Venue: ' + df_con['venue'])
        row_nu = len(df_con.index)
        for i in range(row_nu):
            st.write(''+str(i+1)+') '+ df_con1.iloc[i])
            if display:
                st.caption('Conference place:'+'\n '+ df_con['location'].iloc[i])
                st.caption('Details:'+'\n '+ df_con['details'].iloc[i])

    else:
        df_con1 = ('['+ df_con['conference_name'] + ']'+ '('+ df_con['link'] + ')'', organised by ' + '**' + df_con['organiser'] + '**' + '. Date(s): ' + df_con['date_new'] + ' - ' + df_con['date_new_end'] + ', Venue: ' + df_con['venue'])
        row_nu = len(df_con.index)
        for i in range(row_nu):
            st.write(''+str(i+1)+') '+ df_con1.iloc[i])
            if display:
                st.caption('Conference place:'+'\n '+ df_con['location'].iloc[i])
                st.caption('Details:'+'\n '+ df_con['details'].iloc[i])
        
with tab3:
    st.subheader('Call for papers')
    sheet_url3 = st.secrets["public_gsheets_url3"]
    rows = run_query(f'SELECT * FROM "{sheet_url3}"')

    data = []
    columns = ['name', 'organiser', 'link', 'date', 'details']

    # Print results.
    for row in rows:
        data.append((row.name, row.organiser, row.link, row.deadline, row.details))

    pd.set_option('display.max_colwidth', None)
    df_cfp = pd.DataFrame(data, columns=columns)

    df_cfp['date_new'] = pd.to_datetime(df_cfp['date'], dayfirst = True).dt.strftime('%d/%m/%Y')
    df_cfp.sort_values(by='date', ascending = True, inplace=True)

    df_cfp['details'] = df_cfp['details'].fillna('No details')
    df_cfp = df_cfp.fillna('')

    df_cfp = df_cfp.drop_duplicates(subset=['name', 'link', 'date'], keep='first')
    
    display = st.checkbox('Show details', key='cfp')

    filter = (df_cfp['date']>=today)
    df_cfp = df_cfp.loc[filter]
    if df_cfp['name'].any() in ("", [], None, 0, False):
        st.write('No upcoming Call for papers!')

    df_cfp1 = ('['+ df_cfp['name'] + ']'+ '('+ df_cfp['link'] + ')'', organised by ' + '**' + df_cfp['organiser'] + '**' + '. Deadline: ' + df_cfp['date_new'])
    row_nu = len(df_cfp.index)
    for i in range(row_nu):
        st.write(''+str(i+1)+') '+ df_cfp1.iloc[i])
        if display:
            st.caption('Details:'+'\n '+ df_cfp['details'].iloc[i])

st.write('---')
components.html(
"""
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" 
src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />
© 2022 All rights reserved. This website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
"""
)