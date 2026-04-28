import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import re
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="East Africa Climate Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        padding: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        padding: 0.5rem;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🌍 East Africa Climate Vulnerability Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def get_google_drive_direct_url(share_url):
    """Convert Google Drive share URL to direct download URL"""
    patterns = [
        r'/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'file/d/([a-zA-Z0-9_-]+)'
    ]
    
    file_id = None
    for pattern in patterns:
        match = re.search(pattern, share_url)
        if match:
            file_id = match.group(1)
            break
    
    if not file_id:
        return None
    
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def download_csv_from_google_drive(share_url):
    """Download CSV from Google Drive"""
    try:
        download_url = get_google_drive_direct_url(share_url)
        if not download_url:
            return None
        
        response = requests.get(download_url)
        
        # Handle large files with confirmation
        if 'quota' in response.text.lower() or 'confirm' in response.text:
            confirm_match = re.search(r'confirm=([^&]+)', response.text)
            if confirm_match:
                confirm = confirm_match.group(1)
                download_url = f"{download_url}&confirm={confirm}"
                response = requests.get(download_url)
        
        df = pd.read_csv(io.BytesIO(response.content))
        return df
    except Exception as e:
        st.sidebar.warning(f"Error downloading: {e}")
        return None

@st.cache_data
def load_all_data():
    """Load all cleaned country data from Google Drive"""
    
    # ================================================================
    # IMPORTANT: ADD YOUR GOOGLE DRIVE LINKS BELOW
    # ================================================================
    # How to get links:
    # 1. Upload CSV to Google Drive
    # 2. Right-click → Share → "Anyone with link"
    # 3. Copy the link and paste below
    # ================================================================
    
    drive_links = {
        'ethiopia': 'https://drive.google.com/file/d/1WzxOx68C8RtqTykUxnUR3AvbfPmXzZek/view?usp=sharing',  # Add your link: 'https://drive.google.com/file/d/YOUR_ID/view?usp=sharing'
        'kenya': 'https://drive.google.com/file/d/1hpDjPfKihRCNScDy-KPL1xurTZt-CoGM/view?usp=drive_link',      # Add your link
        'nigeria': 'https://drive.google.com/file/d/1q2Tg1AOZR6RJ2lP5tX0ZA4JzcVnpDFMs/view?usp=drive_link',    # Add your link
        'tanzania': 'https://drive.google.com/file/d/133g8zUpcLf0T15X-UNRFMAjO6ncLZtHT/view?usp=drive_link',   # Add your link
        'sudan': 'https://drive.google.com/file/d/1ZH542Ytxr1lXzg-r6Clz3nqAC8X-xG6P/view?usp=drive_link'      # Add your link

        'ethiopia': 'https://drive.google.com/file/d/1WzxOx68C8RtqTykUxnUR3AvbfPmXzZek/view?usp=drive_link',  # PASTE YOUR ETHIOPIA CSV LINK HERE

        'kenya': 'https://drive.google.com/file/d/1hpDjPfKihRCNScDy-KPL1xurTZt-CoGM/view?usp=drive_link',      # PASTE YOUR KENYA CSV LINK HERE

        'nigeria': 'https://drive.google.com/file/d/1q2Tg1AOZR6RJ2lP5tX0ZA4JzcVnpDFMs/view?usp=drive_link',    # PASTE YOUR NIGERIA CSV LINK HERE

        'tanzania': 'https://drive.google.com/file/d/133g8zUpcLf0T15X-UNRFMAjO6ncLZtHT/view?usp=drive_link',   # PASTE YOUR TANZANIA CSV LINK HERE

        'sudan': 'https://drive.google.com/file/d/1ZH542Ytxr1lXzg-r6Clz3nqAC8X-xG6P/view?usp=drive_link'       # PASTE YOUR SUDAN CSV LINK HERE

    }
    
    dataframes = []
    
    for country, link in drive_links.items():
        if link:
            with st.spinner(f'Loading {country} data from Google Drive...'):
                df = download_csv_from_google_drive(link)
                if df is not None:
                    # Ensure required columns exist
                    if 'Date' not in df.columns and 'YEAR' in df.columns and 'DOY' in df.columns:
                        df['Date'] = pd.to_datetime(df['YEAR'] * 1000 + df['DOY'], format='%Y%j')
                    elif 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                    
                    df['Country'] = country.capitalize()
                    dataframes.append(df)
                    st.sidebar.success(f"✓ Loaded {country.capitalize()}")
                else:
                    st.sidebar.error(f"✗ Failed to load {country.capitalize()}")
        else:
            st.sidebar.warning(f"⚠ No Google Drive link provided for {country.capitalize()}")
    
    if not dataframes:
        st.error("❌ No data loaded. Please provide Google Drive links for at least one country.")
        st.stop()
    
    combined = pd.concat(dataframes, ignore_index=True)
    combined['Year'] = combined['Date'].dt.year
    combined['Month'] = combined['Date'].dt.month
    return combined

# ============================================================================
# LOAD DATA
# ============================================================================

with st.spinner("Loading climate data from Google Drive..."):
    df = load_all_data()

if df.empty:
    st.error("No data available. Please check your Google Drive links.")
    st.stop()

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.markdown("## 🎛️ Dashboard Controls")

countries = sorted(df['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    options=countries,
    default=countries[:3] if len(countries) >= 3 else countries
)

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_range = st.sidebar.slider(
    "📅 Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year - 2),
    step=1
)

variable_options = {
    'T2M': '🌡️ Temperature at 2 Meters (°C)',
    'T2M_MAX': '🔥 Maximum Temperature (°C)',
    'T2M_MIN': '❄️ Minimum Temperature (°C)',
    'PRECTOTCORR': '💧 Precipitation (mm)',
    'RH2M': '💨 Relative Humidity (%)',
    'WS2M': '🌬️ Wind Speed at 2 Meters (m/s)'
}
selected_variable = st.sidebar.selectbox(
    "📊 Select Variable",
    options=list(variable_options.keys()),
    format_func=lambda x: variable_options[x]
)

filtered_df = df[
    (df['Country'].isin(selected_countries)) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Summary")
st.sidebar.metric("Total Records", f"{len(filtered_df):,}")
st.sidebar.metric("Countries Selected", len(selected_countries))
st.sidebar.metric("Date Range", f"{year_range[0]} - {year_range[1]}")

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Temperature Trends",
    "💧 Precipitation Analysis",
    "🔥 Extreme Events",
    "📊 Statistical Comparison",
    "🏆 Vulnerability Ranking"
])

# ============================================================================
# TAB 1: TEMPERATURE TRENDS
# ============================================================================

with tab1:
    st.markdown('<h2 class="sub-header">📈 Temperature Trends Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        monthly_temp = filtered_df.groupby(['Country', 'Year', 'Month'])['T2M'].mean().reset_index()
        monthly_temp['Date'] = pd.to_datetime(monthly_temp['Year'].astype(str) + '-' + monthly_temp['Month'].astype(str))
        
        fig = px.line(
            monthly_temp,
            x='Date',
            y='T2M',
            color='Country',
            title=f'Monthly Temperature Trends ({year_range[0]}-{year_range[1]})',
            labels={'T2M': 'Temperature (°C)', 'Date': 'Date'},
            template='plotly_white'
        )
        fig.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        temp_stats = filtered_df.groupby('Country')['T2M'].agg([
            ('Mean (°C)', 'mean'),
            ('Max (°C)', 'max'),
            ('Min (°C)', 'min')
        ]).round(2)
        st.markdown("### 📈 Temperature Summary")
        st.dataframe(temp_stats, use_container_width=True)
    
    st.markdown("### 🌸 Seasonal Temperature Patterns")
    seasonal_temp = filtered_df.groupby(['Country', 'Month'])['T2M'].mean().reset_index()
    
    fig = px.line(
        seasonal_temp,
        x='Month',
        y='T2M',
        color='Country',
        title='Average Monthly Temperature Cycle',
        labels={'T2M': 'Temperature (°C)', 'Month': 'Month'},
        template='plotly_white'
    )
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), 
                     ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: PRECIPITATION ANALYSIS
# ============================================================================

with tab2:
    st.markdown('<h2 class="sub-header">💧 Precipitation Variability Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            filtered_df,
            x='Country',
            y='PRECTOTCORR',
            color='Country',
            title='Precipitation Distribution by Country',
            labels={'PRECTOTCORR': 'Daily Precipitation (mm)'},
            template='plotly_white'
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        precip_stats = filtered_df.groupby('Country')['PRECTOTCORR'].agg([
            ('Mean (mm)', 'mean'),
            ('Std Dev', 'std'),
            ('CV (%)', lambda x: (x.std() / x.mean()) * 100 if x.mean() > 0 else 0)
        ]).round(2)
        st.markdown("### 💧 Precipitation Statistics")
        st.dataframe(precip_stats, use_container_width=True)
    
    st.markdown("### 🌧️ Monthly Precipitation Patterns")
    monthly_precip = filtered_df.groupby(['Country', 'Month'])['PRECTOTCORR'].mean().reset_index()
    
    fig = px.bar(
        monthly_precip,
        x='Month',
        y='PRECTOTCORR',
        color='Country',
        title='Average Monthly Precipitation',
        labels={'PRECTOTCORR': 'Precipitation (mm)', 'Month': 'Month'},
        template='plotly_white',
        barmode='group'
    )
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), 
                     ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 3: EXTREME EVENTS
# ============================================================================

with tab3:
    st.markdown('<h2 class="sub-header">🔥 Extreme Events Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ☀️ Extreme Heat Days (>35°C)")
        heat_data = filtered_df[filtered_df['T2M_MAX'] > 35].groupby(['Country', 'Year']).size().reset_index(name='Heat_Days')
        
        if not heat_data.empty:
            fig = px.bar(
                heat_data,
                x='Year',
                y='Heat_Days',
                color='Country',
                title='Days with Maximum Temperature >35°C',
                labels={'Heat_Days': 'Number of Days', 'Year': 'Year'},
                template='plotly_white',
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No extreme heat events in selected data range")
    
    with col2:
        st.markdown("### 💧 Drought Frequency (<1mm)")
        dry_data = filtered_df[filtered_df['PRECTOTCORR'] < 1].groupby(['Country', 'Year']).size().reset_index(name='Dry_Days')
        
        if not dry_data.empty:
            fig = px.bar(
                dry_data,
                x='Year',
                y='Dry_Days',
                color='Country',
                title='Days with Precipitation <1mm (Dry Days)',
                labels={'Dry_Days': 'Number of Days', 'Year': 'Year'},
                template='plotly_white',
                barmode='group'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No dry day data available")
    
    st.markdown("### 🔥💧 Heat-Drought Relationship")
    
    country_heat_drought = filtered_df.groupby('Country').agg({
        'T2M_MAX': lambda x: (x > 35).mean() * 100,
        'PRECTOTCORR': lambda x: (x < 1).mean() * 100
    }).reset_index()
    country_heat_drought.columns = ['Country', 'Heat_Wave_Prop (%)', 'Drought_Prop (%)']
    
    fig = px.scatter(
        country_heat_drought,
        x='Heat_Wave_Prop (%)',
        y='Drought_Prop (%)',
        text='Country',
        size='Heat_Wave_Prop (%)',
        title='Heat Wave vs Drought Frequency by Country',
        labels={'Heat_Wave_Prop (%)': 'Proportion of Days >35°C (%)',
                'Drought_Prop (%)': 'Proportion of Days <1mm (%)'},
        template='plotly_white'
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 4: STATISTICAL COMPARISON
# ============================================================================

with tab4:
    st.markdown('<h2 class="sub-header">📊 Statistical Comparison</h2>', unsafe_allow_html=True)
    
    compare_var = st.selectbox(
        "Select variable to compare across countries",
        options=list(variable_options.keys()),
        format_func=lambda x: variable_options[x],
        key='compare_var'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            filtered_df,
            x='Country',
            y=compare_var,
            color='Country',
            title=f'{variable_options[compare_var]} Distribution by Country',
            labels={compare_var: variable_options[compare_var]},
            template='plotly_white'
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        stats_df = filtered_df.groupby('Country')[compare_var].agg([
            ('Mean', 'mean'),
            ('Median', 'median'),
            ('Std Dev', 'std'),
            ('Min', 'min'),
            ('Max', 'max')
        ]).round(2)
        st.markdown("### 📊 Summary Statistics")
        st.dataframe(stats_df, use_container_width=True)
    
    st.markdown("### 🔗 Correlation Matrix")
    numeric_cols = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'RH2M', 'WS2M']
    available_cols = [col for col in numeric_cols if col in filtered_df.columns]
    
    if len(available_cols) > 1:
        corr_matrix = filtered_df[available_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect='auto',
            color_continuous_scale='RdBu_r',
            title='Correlation Matrix of Climate Variables',
            labels=dict(color='Correlation')
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 5: VULNERABILITY RANKING
# ============================================================================

with tab5:
    st.markdown('<h2 class="sub-header">🏆 Climate Vulnerability Ranking</h2>', unsafe_allow_html=True)
    
    vulnerability_data = []
    
    for country in selected_countries:
        country_data = filtered_df[filtered_df['Country'] == country]
        
        if len(country_data) > 0:
            mean_temp = country_data['T2M'].mean()
            temp_range = (country_data['T2M_MAX'] - country_data['T2M_MIN']).mean()
            heat_risk = (country_data['T2M_MAX'] > 35).mean() * 100
            drought_risk = (country_data['PRECTOTCORR'] < 1).mean() * 100
            precip_var = country_data['PRECTOTCORR'].std() / country_data['PRECTOTCORR'].mean() if country_data['PRECTOTCORR'].mean() > 0 else 0
            
            vulnerability_data.append({
                'Country': country,
                'Mean Temp (°C)': round(mean_temp, 1),
                'Temp Range (°C)': round(temp_range, 1),
                'Heat Risk (%)': round(heat_risk, 1),
                'Drought Risk (%)': round(drought_risk, 1),
                'Precip CV': round(precip_var, 2)
            })
    
    if vulnerability_data:
        vuln_df = pd.DataFrame(vulnerability_data)
        
        if vuln_df['Heat Risk (%)'].max() > vuln_df['Heat Risk (%)'].min():
            vuln_df['Heat_Score'] = (vuln_df['Heat Risk (%)'] - vuln_df['Heat Risk (%)'].min()) / (vuln_df['Heat Risk (%)'].max() - vuln_df['Heat Risk (%)'].min())
        else:
            vuln_df['Heat_Score'] = 0
        
        if vuln_df['Drought Risk (%)'].max() > vuln_df['Drought Risk (%)'].min():
            vuln_df['Drought_Score'] = (vuln_df['Drought Risk (%)'] - vuln_df['Drought Risk (%)'].min()) / (vuln_df['Drought Risk (%)'].max() - vuln_df['Drought Risk (%)'].min())
        else:
            vuln_df['Drought_Score'] = 0
        
        if vuln_df['Precip CV'].max() > vuln_df['Precip CV'].min():
            vuln_df['CV_Score'] = (vuln_df['Precip CV'] - vuln_df['Precip CV'].min()) / (vuln_df['Precip CV'].max() - vuln_df['Precip CV'].min())
        else:
            vuln_df['CV_Score'] = 0
        
        vuln_df['Vulnerability_Score'] = (vuln_df['Heat_Score'] * 0.4 + vuln_df['Drought_Score'] * 0.4 + vuln_df['CV_Score'] * 0.2) * 10
        vuln_df = vuln_df.sort_values('Vulnerability_Score', ascending=False).reset_index(drop=True)
        vuln_df['Rank'] = vuln_df.index + 1
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig = px.bar(
                vuln_df,
                x='Country',
                y='Vulnerability_Score',
                color='Vulnerability_Score',
                color_continuous_scale='Reds',
                title='Climate Vulnerability Score (Higher = More Vulnerable)',
                labels={'Vulnerability_Score': 'Vulnerability Score (0-10)'},
                text='Vulnerability_Score'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Ranking Results")
            st.dataframe(vuln_df[['Rank', 'Country', 'Vulnerability_Score', 'Heat Risk (%)', 'Drought Risk (%)']], 
                        use_container_width=True)
        
        st.markdown("### 🔑 Key Findings for COP32")
        
        highest_vuln = vuln_df.iloc[0]['Country'] if len(vuln_df) > 0 else "No data"
        
        st.markdown(f"""
        <div class="insight-box">
        <b>🏆 Most Vulnerable Country:</b> {highest_vuln}<br><br>
        <b>⚠️ Primary Risks:</b><br>
        • Extreme heat: {vuln_df.iloc[0]['Heat Risk (%)'] if len(vuln_df) > 0 else 'N/A'}% of days >35°C<br>
        • Drought stress: {vuln_df.iloc[0]['Drought Risk (%)'] if len(vuln_df) > 0 else 'N/A'}% of days with <1mm precipitation<br>
        • Precipitation variability: CV = {vuln_df.iloc[0]['Precip CV'] if len(vuln_df) > 0 else 'N/A'}<br><br>
        <b>💡 Recommendation for COP32:</b><br>
        {highest_vuln} should be prioritized for climate adaptation funding, with focus on:<br>
        • Early warning systems for drought and heat<br>
        • Drought-resistant agriculture research<br>
        • Heat action plans and cooling infrastructure<br>
        • Water resource management and storage
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>🌍 Climate Vulnerability Dashboard | Data: 2015-2026 | For COP32 Position Paper</p>",
    unsafe_allow_html=True
)