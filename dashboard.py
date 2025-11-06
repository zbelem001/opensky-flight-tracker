""" Dashboard Streamlit épuré pour les vols en temps réel - Aéroport de Dubai (DXB) """
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
from datetime import datetime
import time

# ====================== CONFIGURATION DE LA PAGE ======================
st.set_page_config(
    page_title="DXB Live Flights",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== STYLES CSS ÉPURÉS ======================
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== CONSTANTES ======================
DUBAI_LAT = 25.2532
DUBAI_LON = 55.3657
FLIGHTS_PATH = "/tmp/flights_data"
STATS_PATH = "/tmp/flight_statistics"

# ====================== FONCTIONS CACHÉES ======================
@st.cache_data(ttl=10)  # Rafraîchissement toutes les 10 secondes max
def load_latest_flights():
    """Charge les données des 10 derniers fichiers Parquet (5 dernières minutes)"""
    try:
        files = sorted(glob.glob(f"{FLIGHTS_PATH}/*.parquet"), key=os.path.getmtime, reverse=True)[:10]
        if not files:
            return pd.DataFrame()

        dfs = [pd.read_parquet(f) for f in files]
        df = pd.concat(dfs, ignore_index=True)

        if 'processing_time' not in df.columns or df.empty:
            return pd.DataFrame()

        df['processing_time'] = pd.to_datetime(df['processing_time'])
        five_min_ago = pd.Timestamp.now() - pd.Timedelta(minutes=5)
        df = df[df['processing_time'] >= five_min_ago]

        # Dernière position par avion
        df = df.sort_values('processing_time', ascending=False).drop_duplicates('icao24')
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)  # Rafraîchissement toutes les 60 secondes pour les stats journalières
def load_daily_flights():
    """Charge toutes les données de la journée pour les statistiques cumulées"""
    try:
        files = glob.glob(f"{FLIGHTS_PATH}/*.parquet")
        if not files:
            return pd.DataFrame()

        dfs = []
        for f in files:
            try:
                df = pd.read_parquet(f)
                dfs.append(df)
            except:
                pass
        
        if not dfs:
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)

        if 'processing_time' not in df.columns or df.empty:
            return pd.DataFrame()

        df['processing_time'] = pd.to_datetime(df['processing_time'])
        
        # Filtrer pour garder seulement les données d'aujourd'hui
        today = pd.Timestamp.now().normalize()
        df = df[df['processing_time'] >= today]

        return df
    except Exception as e:
        return pd.DataFrame()


def compute_daily_stats(df):
    """Calcule les statistiques journalières des vols"""
    if df.empty:
        return {
            'total_flights': 0,
            'total_arrivals': 0,
            'total_departures': 0,
            'total_parked': 0,
            'total_inflight': 0,
            'unique_flights': 0,
            'hourly_distribution': pd.DataFrame()
        }
    
    # Comptage des vols uniques par statut
    unique_by_status = df.drop_duplicates(subset=['icao24', 'status'])
    
    stats = {
        'total_flights': df['icao24'].nunique(),
        'total_arrivals': len(unique_by_status[unique_by_status['status'] == 'arrivée']),
        'total_departures': len(unique_by_status[unique_by_status['status'] == 'départ']),
        'total_parked': len(unique_by_status[unique_by_status['status'] == 'stationnement']),
        'total_inflight': len(unique_by_status[unique_by_status['status'] == 'en_vol']),
        'unique_flights': df['icao24'].nunique(),
    }
    
    # Distribution par heure
    if 'processing_time' in df.columns:
        df_copy = df.copy()
        df_copy['hour'] = df_copy['processing_time'].dt.hour
        hourly = df_copy.groupby(['hour', 'status']).size().reset_index(name='count')
        stats['hourly_distribution'] = hourly
    else:
        stats['hourly_distribution'] = pd.DataFrame()
    
    return stats


def compute_stats(df):
    """Calcule les stats par fenêtre de 2 min"""
    if df.empty or 'processing_time' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df['window'] = df['processing_time'].dt.floor('2min')
    stats = df.groupby(['window', 'status']).agg(
        count=('callsign', 'count'),
        avg_altitude=('altitude_ft', 'mean'),
        avg_speed=('speed_kmh', 'mean')
    ).round(1).reset_index()
    return stats


# ====================== CRÉATION DES VISUALISATIONS ======================
def create_map(df):
    if df.empty:
        return None

    color_map = {'arrivée': '#10b981', 'départ': '#3b82f6', 'stationnement': '#ef4444', 'en_vol': '#f59e0b'}
    df['color'] = df['status'].map(color_map)

    fig = go.Figure()

    # Aéroport
    fig.add_trace(go.Scattermapbox(
        lat=[DUBAI_LAT], lon=[DUBAI_LON],
        mode='markers', marker=dict(size=18, color='#dc2626', symbol='airport'),
        name='DXB', text='Aéroport de Dubai (DXB)', hoverinfo='text'
    ))

    # Vols
    for status in df['status'].unique():
        subset = df[df['status'] == status]
        fig.add_trace(go.Scattermapbox(
            lat=subset['latitude'], lon=subset['longitude'],
            mode='markers', marker=dict(size=10, color=subset['color'].iloc[0]),
            name=status.capitalize(),
            text=subset.apply(lambda x: f"{x['callsign']}<br>"
                                       f"Alt: {x['altitude_ft']:.0f} ft<br>"
                                       f"Vit: {x['speed_kmh']:.0f} km/h", axis=1),
            hoverinfo='text'
        ))

    fig.update_layout(
        mapbox=dict(style="carto-positron", center=dict(lat=DUBAI_LAT, lon=DUBAI_LON), zoom=9.5),
        height=550, margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_hourly_distribution_chart(hourly_df):
    """Crée un graphique de distribution horaire des vols"""
    if hourly_df.empty:
        return None
    
    color_map = {'arrivée': '#10b981', 'départ': '#3b82f6', 'stationnement': '#ef4444', 'en_vol': '#f59e0b'}
    
    fig = px.bar(
        hourly_df,
        x='hour',
        y='count',
        color='status',
        title='📊 Distribution Horaire des Vols (Aujourd\'hui)',
        labels={'hour': 'Heure', 'count': 'Nombre de vols', 'status': 'Statut'},
        color_discrete_map=color_map,
        barmode='group'
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        hovermode='x unified'
    )
    
    return fig


def create_status_bar(df):
    if df.empty:
        return None
    counts = df['status'].value_counts().reset_index()
    fig = px.bar(
        counts, x='status', y='count',
        color='status',
        color_discrete_map={'arrivée': '#10b981', 'départ': '#3b82f6', 'stationnement': '#ef4444', 'en_vol': '#f59e0b'},
        labels={'count': 'Nombre de vols', 'status': 'Statut'},
        text='count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=320, showlegend=False, xaxis_title=None)
    return fig


def create_altitude_hist(df):
    if df.empty or df['altitude_ft'].isna().all():
        return None
    df_alt = df[df['altitude_ft'] > 0].copy()
    fig = px.histogram(
        df_alt, x='altitude_ft', nbins=25,
        labels={'altitude_ft': 'Altitude (pieds)'},
        color_discrete_sequence=['#6366f1']
    )
    fig.update_layout(height=320, bargap=0.1)
    return fig


def create_timeline(stats_df):
    if stats_df.empty:
        return None
    fig = px.area(
        stats_df, x='window', y='count', color='status',
        color_discrete_map={'arrivée': '#10b981', 'départ': '#3b82f6', 'stationnement': '#ef4444', 'en_vol': '#f59e0b'},
        labels={'count': 'Vols', 'window': 'Temps'}
    )
    fig.update_layout(height=320)
    return fig


# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Contrôles")
    refresh_rate = st.slider("Rafraîchissement (s)", 5, 30, 10, 5)
    st.markdown("---")
    st.caption("""
    **Source** : OpenSky Network  
    **Traitement** : Apache Spark + Kafka  
    **Dashboard** : Streamlit
    """)

# ====================== MAIN DASHBOARD ======================
st.markdown('<h1 class="main-header">✈️ DXB Live Flights</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Suivi en temps réel des vols autour de l’aéroport international de Dubai</p>', unsafe_allow_html=True)

placeholder = st.empty()

while True:
    with placeholder.container():
        # Chargement des données
        df = load_latest_flights()  # Dernières 5 minutes
        daily_df = load_daily_flights()  # Toute la journée
        stats = compute_stats(df)
        daily_stats = compute_daily_stats(daily_df)

        if df.empty:
            st.warning("⏳ Aucune donnée disponible. Vérifiez Kafka & Spark.")
            time.sleep(refresh_rate)
            continue

        # === STATISTIQUES JOURNALIÈRES ===
        st.markdown("### 📅 Statistiques de la Journée")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("✈️ Total Vols", daily_stats['total_flights'])
        
        with col2:
            st.metric("🛬 Arrivées", daily_stats['total_arrivals'])
        
        with col3:
            st.metric("🛫 Départs", daily_stats['total_departures'])
        
        with col4:
            st.metric("🅿️ Stationnés", daily_stats['total_parked'])
        
        with col5:
            st.metric("🌍 En vol", daily_stats['total_inflight'])
        
        # Graphique de distribution horaire
        if not daily_stats['hourly_distribution'].empty:
            st.plotly_chart(
                create_hourly_distribution_chart(daily_stats['hourly_distribution']),
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### ⏱️ État Actuel (5 dernières minutes)")

        # === MÉTRIQUES EN TEMPS RÉEL ===
        col1, col2, col3, col4 = st.columns(4)
        status_counts = df['status'].value_counts()
        with col1:
            st.metric("🛬 Arrivées", status_counts.get('arrivée', 0))
        with col2:
            st.metric("🛫 Départs", status_counts.get('départ', 0))
        with col3:
            st.metric("🅿️ Au sol", status_counts.get('stationnement', 0))
        with col4:
            st.metric("✈️ Total", len(df))

        st.markdown("---")

        # === CARTE ===
        st.subheader("📍 Carte en Temps Réel")
        map_fig = create_map(df)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)

        # === GRAPHIQUES ===
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_status_bar(df), use_container_width=True)
        with col2:
            st.plotly_chart(create_altitude_hist(df), use_container_width=True)

        if not stats.empty:
            st.subheader("📈 Évolution (2 min)")
            st.plotly_chart(create_timeline(stats), use_container_width=True)

        # === TABLEAU RÉCENT ===
        st.subheader("📋 Derniers Vols Reçus")
        display_cols = ['callsign', 'origin_country', 'status', 'altitude_ft', 'speed_kmh', 'processing_time']
        recent = df[display_cols].sort_values('processing_time', ascending=False).head(10)
        recent['processing_time'] = recent['processing_time'].dt.strftime('%H:%M:%S')
        st.dataframe(recent, use_container_width=True, hide_index=True)

        # === FOOTER ===
        st.caption(f"🔄 Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

    time.sleep(refresh_rate)