import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Car Sharing Analytics",
    layout="wide",
    page_icon="🚗",
    initial_sidebar_state="expanded"
)

# ── Clean Light Theme CSS ─────────────────────────────────────
st.markdown("""
<style>
/* Background & text */
[data-testid="stAppViewContainer"] { background: #f5f7fa; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e0e4ed; }
h1, h2, h3 { color: #1a1a2e !important; }
p, li, label { color: #444 !important; }

/* KPI Cards — tall and spacious */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 28px 20px !important;
    border: 1px solid #e0e4ed;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    min-height: 120px;
}
[data-testid="stMetricLabel"] {
    color: #666 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetricValue"] {
    color: #1a1a2e !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin-top: 6px !important;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #555 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #3a4fd4 !important;
    border-bottom: 3px solid #3a4fd4 !important;
}

/* Divider */
hr { border-color: #e0e4ed !important; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #3a4fd4 0%, #6c3fc5 50%, #c23b8a 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    box-shadow: 0 4px 20px rgba(58,79,212,0.25);
}
.hero h1 { color: white !important; font-size: 2.2rem !important; margin: 0 !important; }
.hero p  { color: rgba(255,255,255,0.9) !important; font-size: 1.1rem !important; margin: 6px 0 0 0 !important; }

/* Section headers */
.section-header {
    border-left: 4px solid #3a4fd4;
    padding: 6px 16px;
    margin: 20px 0 14px 0;
    background: #eef0fb;
    border-radius: 0 8px 8px 0;
}
.section-header h3 { color: #1a1a2e !important; margin: 0 !important; font-size: 1.05rem !important; }

/* Winner badges */
.winner-a { background: #e8f0fe; border-left: 4px solid #3a4fd4; border-radius: 8px; padding: 10px 16px; margin: 4px 0; }
.winner-b { background: #fde8e8; border-left: 4px solid #ed6663; border-radius: 8px; padding: 10px 16px; margin: 4px 0; }
.winner-a p { color: #1a3a6e !important; margin: 0 !important; font-weight: 600; }
.winner-b p { color: #6e1a1a !important; margin: 0 !important; font-weight: 600; }

/* Map legend */
.map-legend { background: white; border-radius: 10px; padding: 14px; border: 1px solid #e0e4ed; margin-top: 8px; }
.map-legend p { color: #333 !important; margin: 2px 0 !important; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Load & prepare data ───────────────────────────────────────
@st.cache_data
def load_data():
    trips     = pd.read_csv("datasets/trips.csv")
    cars      = pd.read_csv("datasets/cars.csv")
    customers = pd.read_csv("datasets/customers.csv")
    cities    = pd.read_csv("datasets/cities.csv")
    ratings   = pd.read_csv("datasets/ratings.csv")
    trips['pickup_time']  = pd.to_datetime(trips['pickup_time'])
    trips['dropoff_time'] = pd.to_datetime(trips['dropoff_time'])
    trips['duration_h']   = (trips['dropoff_time'] - trips['pickup_time']).dt.total_seconds() / 3600
    trips['duration_h']   = trips['duration_h'].clip(lower=0)
    trips['day_of_week']  = trips['pickup_time'].dt.day_name()
    trips['hour']         = trips['pickup_time'].dt.hour
    trips['month_year']   = trips['pickup_time'].dt.to_period('M').astype(str)
    df = trips.merge(cars,      left_on='car_id',      right_on='id', suffixes=('_trip','_car'))
    df = df.merge(customers,    left_on='customer_id', right_on='id', suffixes=('','_customer'))
    df = df.merge(cities,       on='city_id')
    df = df.merge(ratings,      left_on='id_trip',     right_on='trip_id', suffixes=('','_rating'))
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Dashboard Filters")
st.sidebar.markdown("*Applies to Dashboard tab only*")
st.sidebar.divider()

selected_brands = st.sidebar.multiselect("🚘 Car Brand",  sorted(df["brand"].unique()),     default=sorted(df["brand"].unique()))
selected_cities = st.sidebar.multiselect("🏙️ City",       sorted(df["city_name"].unique()), default=sorted(df["city_name"].unique()))
selected_years  = st.sidebar.multiselect("📅 Car Year",   sorted(df["year"].unique()),      default=sorted(df["year"].unique()))
rating_range    = st.sidebar.slider("⭐ Rating", 1, 5, (1, 5))
revenue_range   = st.sidebar.slider("💶 Revenue (€)", int(df['revenue'].min()), int(df['revenue'].max()), (int(df['revenue'].min()), int(df['revenue'].max())))

st.sidebar.divider()
st.sidebar.markdown("### 📊 Dataset Info")
st.sidebar.markdown(f"- **{df.shape[0]:,}** total trips")
st.sidebar.markdown(f"- **{df['brand'].nunique()}** car brands")
st.sidebar.markdown(f"- **{df['city_name'].nunique()}** cities")
st.sidebar.markdown(f"- **2** years of data (2022–2023)")

dff = df[
    df["brand"].isin(selected_brands) &
    df["city_name"].isin(selected_cities) &
    df["year"].isin(selected_years) &
    df["rating"].between(*rating_range) &
    df["revenue"].between(*revenue_range)
]

# ── TABS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "⚖️ Comparison Tool", "🏆 Leaderboards", "🔎 Trip Explorer"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="hero"><h1>🚗 Car Sharing Analytics Dashboard</h1><p>Real-time insights across 8 European cities · 2022–2023</p></div>', unsafe_allow_html=True)

    if dff.empty:
        st.warning("⚠️ No data matches your filters. Adjust the sidebar.")
        st.stop()

    # ── KPIs ──
    st.markdown('<div class="section-header"><h3>📈 Key Performance Indicators</h3></div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("🚗 Total Trips",       f"{len(dff):,}")
    k2.metric("👥 Customers",         f"{dff['customer_id'].nunique():,}")
    k3.metric("💶 Total Revenue",     f"€{dff['revenue'].sum():,.0f}")
    k4.metric("💰 Avg Revenue/Trip",  f"€{dff['revenue'].mean():.0f}")
    k5.metric("⭐ Avg Rating",        f"{dff['rating'].mean():.2f} / 5")
    k6.metric("⏱️ Avg Trip Duration", f"{dff['duration_h'].mean():.1f} hrs")
    st.divider()

    # ── Revenue Map ──
    st.markdown('<div class="section-header"><h3>🗺️ Revenue by City — European Map</h3></div>', unsafe_allow_html=True)

    city_stats = dff.groupby('city_name').agg(
        lat=('city_lat', 'first'),
        lon=('city_long', 'first'),
        revenue=('revenue', 'sum'),
        trips=('id_trip', 'count'),
        avg_rating=('rating', 'mean')
    ).reset_index()

    # Normalize revenue to bubble size (100–2000)
    min_r, max_r = city_stats['revenue'].min(), city_stats['revenue'].max()
    city_stats['size'] = ((city_stats['revenue'] - min_r) / (max_r - min_r) * 1900 + 100).astype(int)
    city_stats['revenue_fmt'] = city_stats['revenue'].apply(lambda x: f"€{x:,.0f}")

    map_col, legend_col = st.columns([3, 1])

    with map_col:
        st.map(
            city_stats.rename(columns={'lat': 'latitude', 'lon': 'longitude'}),
            latitude='latitude',
            longitude='longitude',
            size='size',
            color='#3a4fd4'
        )

    with legend_col:
        st.markdown("**City Revenue Breakdown**")
        city_sorted = city_stats.sort_values('revenue', ascending=False)
        for _, row in city_sorted.iterrows():
            bar_pct = int((row['revenue'] / max_r) * 100)
            st.markdown(f"""
            <div class="map-legend">
                <p><b>{row['city_name']}</b></p>
                <p>💶 {row['revenue_fmt']}</p>
                <p>🚗 {int(row['trips'])} trips</p>
                <p>⭐ {row['avg_rating']:.2f}</p>
                <div style="background:#e0e4ed;border-radius:4px;height:6px;margin-top:6px;">
                    <div style="background:#3a4fd4;width:{bar_pct}%;height:6px;border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Geographic & Brand ──
    st.markdown('<div class="section-header"><h3>🌍 Geographic & Brand Overview</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏙️ Trips by City**")
        st.bar_chart(dff['city_name'].value_counts(), color="#4e89ae", height=280)
    with c2:
        st.markdown("**🚘 Trips by Car Brand**")
        st.bar_chart(dff['brand'].value_counts(), color="#ed6663", height=280)
    st.divider()

    # ── Revenue ──
    st.markdown('<div class="section-header"><h3>💶 Revenue Insights</h3></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**💰 Avg Revenue by Brand**")
        st.bar_chart(dff.groupby('brand')['revenue'].mean().sort_values(ascending=False).round(0), color="#f9c74f", height=280)
    with c4:
        st.markdown("**🏙️ Avg Revenue by City**")
        st.bar_chart(dff.groupby('city_name')['revenue'].mean().sort_values(ascending=False).round(0), color="#43aa8b", height=280)
    st.divider()

    # ── Time trends ──
    st.markdown('<div class="section-header"><h3>📅 Time & Behaviour Trends</h3></div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("**📈 Monthly Trip Volume**")
        monthly = dff.groupby('month_year').size().reset_index(name='Trips').sort_values('month_year')
        st.line_chart(monthly.set_index('month_year')['Trips'], color="#a786c9", height=250)
    with c6:
        st.markdown("**📆 Busiest Days of the Week**")
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        st.bar_chart(dff['day_of_week'].value_counts().reindex(day_order).dropna(), color="#f4845f", height=250)
    st.divider()

    # ── Ratings & Hours ──
    st.markdown('<div class="section-header"><h3>⭐ Ratings & Peak Hours</h3></div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        st.markdown("**⭐ Avg Rating by City**")
        st.bar_chart(dff.groupby('city_name')['rating'].mean().sort_values(ascending=False).round(2), color="#ffb703", height=250)
    with c8:
        st.markdown("**🕐 Trips by Hour of Day**")
        st.bar_chart(dff['hour'].value_counts().sort_index(), color="#219ebc", height=250)
    st.divider()

    # ── Monthly Revenue ──
    st.markdown('<div class="section-header"><h3>💶 Monthly Revenue Trend</h3></div>', unsafe_allow_html=True)
    monthly_rev = dff.groupby('month_year')['revenue'].sum().reset_index().sort_values('month_year')
    st.line_chart(monthly_rev.set_index('month_year')['revenue'], color="#f9c74f", height=220)
    st.divider()

    with st.expander("🔎 Explore Raw Data"):
        cols = ['pickup_time','brand','model','year','city_name','distance','duration_h','revenue','rating','name']
        st.markdown(f"Showing **{len(dff):,}** rows")
        st.dataframe(dff[cols].rename(columns={'pickup_time':'Pickup Time','brand':'Brand','model':'Model',
            'year':'Year','city_name':'City','distance':'Distance (km)','duration_h':'Duration (hrs)',
            'revenue':'Revenue (€)','rating':'Rating','name':'Customer'}).reset_index(drop=True), use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2 — COMPARISON TOOL
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="hero"><h1>⚖️ Comparison Tool</h1><p>Compare brands, cities or time periods side by side</p></div>', unsafe_allow_html=True)

    compare_type = st.radio("Compare by:", ["🚘 Car Brands", "🏙️ Cities", "📅 Time Periods"], horizontal=True)
    st.divider()

    def comparison_block(label_a, label_b, da, db):
        c1, c2 = st.columns(2)
        metrics = [
            ("🚗 Total Trips",        f"{len(da):,}",                   f"{len(db):,}"),
            ("💶 Avg Revenue (€)",    f"€{da['revenue'].mean():.2f}",   f"€{db['revenue'].mean():.2f}"),
            ("⭐ Avg Rating",         f"{da['rating'].mean():.2f}",     f"{db['rating'].mean():.2f}"),
            ("⏱️ Avg Duration (hrs)", f"{da['duration_h'].mean():.1f}", f"{db['duration_h'].mean():.1f}"),
            ("📍 Total Distance",     f"{da['distance'].sum():.1f} km", f"{db['distance'].sum():.1f} km"),
            ("💰 Total Revenue",      f"€{da['revenue'].sum():,.0f}",   f"€{db['revenue'].sum():,.0f}"),
        ]
        with c1:
            st.markdown(f"### 🔵 {label_a}")
            for name, va, _ in metrics: st.metric(name, va)
        with c2:
            st.markdown(f"### 🔴 {label_b}")
            for name, _, vb in metrics: st.metric(name, vb)
        st.divider()

        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown(f"**📈 Monthly Trips — {label_a}**")
            ma = da.groupby('month_year').size().reset_index(name='Trips').sort_values('month_year')
            st.line_chart(ma.set_index('month_year'), color="#4e89ae", height=220)
        with ch2:
            st.markdown(f"**📈 Monthly Trips — {label_b}**")
            mb = db.groupby('month_year').size().reset_index(name='Trips').sort_values('month_year')
            st.line_chart(mb.set_index('month_year'), color="#ed6663", height=220)

        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        ch3, ch4 = st.columns(2)
        with ch3:
            st.markdown(f"**📆 Busiest Days — {label_a}**")
            st.bar_chart(da['day_of_week'].value_counts().reindex(day_order).dropna(), color="#4e89ae", height=220)
        with ch4:
            st.markdown(f"**📆 Busiest Days — {label_b}**")
            st.bar_chart(db['day_of_week'].value_counts().reindex(day_order).dropna(), color="#ed6663", height=220)

        ch5, ch6 = st.columns(2)
        with ch5:
            st.markdown(f"**🕐 Peak Hours — {label_a}**")
            st.bar_chart(da['hour'].value_counts().sort_index(), color="#4e89ae", height=220)
        with ch6:
            st.markdown(f"**🕐 Peak Hours — {label_b}**")
            st.bar_chart(db['hour'].value_counts().sort_index(), color="#ed6663", height=220)

        st.divider()
        st.markdown("### 🏆 Head-to-Head Summary")
        results = [
            ("Revenue per trip",  da['revenue'].mean(),  db['revenue'].mean(),  "higher avg revenue"),
            ("Customer rating",   da['rating'].mean(),   db['rating'].mean(),   "better rated"),
            ("Trip volume",       len(da),               len(db),               "more trips"),
            ("Total earnings",    da['revenue'].sum(),   db['revenue'].sum(),   "higher total revenue"),
        ]
        for label, va, vb, desc in results:
            winner = label_a if va >= vb else label_b
            colour = "winner-a" if va >= vb else "winner-b"
            emoji  = "🔵" if va >= vb else "🔴"
            st.markdown(f'<div class="{colour}"><p>{emoji} <b>{winner}</b> has {desc} ({label})</p></div>', unsafe_allow_html=True)

    if compare_type == "🚘 Car Brands":
        brands = sorted(df["brand"].unique())
        c1, c2 = st.columns(2)
        ba = c1.selectbox("🔵 Brand A", brands, index=0)
        bb = c2.selectbox("🔴 Brand B", brands, index=1)
        if ba == bb: st.warning("Please pick two different brands.")
        else: comparison_block(ba, bb, df[df['brand']==ba], df[df['brand']==bb])

    elif compare_type == "🏙️ Cities":
        cities_list = sorted(df["city_name"].unique())
        c1, c2 = st.columns(2)
        ca = c1.selectbox("🔵 City A", cities_list, index=0)
        cb = c2.selectbox("🔴 City B", cities_list, index=1)
        if ca == cb: st.warning("Please pick two different cities.")
        else: comparison_block(ca, cb, df[df['city_name']==ca], df[df['city_name']==cb])

    elif compare_type == "📅 Time Periods":
        months = sorted(df['month_year'].unique())
        c1, c2 = st.columns(2)
        pa = c1.selectbox("🔵 Period A", months, index=0)
        pb = c2.selectbox("🔴 Period B", months, index=min(1, len(months)-1))
        if pa == pb: st.warning("Please pick two different periods.")
        else:
            comparison_block(pa, pb, df[df['month_year']==pa], df[df['month_year']==pb])


# ═══════════════════════════════════════════════════════════════
# TAB 3 — LEADERBOARDS
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="hero"><h1>🏆 Leaderboards</h1><p>Top performers across every category</p></div>', unsafe_allow_html=True)

    l1, l2 = st.columns(2)
    with l1:
        st.markdown("### 💰 Top 10 Cars by Total Revenue")
        top_rev = (df.groupby(['brand','model','year'])
            .agg(Total_Revenue=('revenue','sum'), Trips=('id_trip','count'), Avg_Rating=('rating','mean'))
            .round(2).sort_values('Total_Revenue', ascending=False).head(10).reset_index())
        top_rev['Total_Revenue'] = top_rev['Total_Revenue'].apply(lambda x: f"€{x:,.0f}")
        top_rev['Avg_Rating']    = top_rev['Avg_Rating'].apply(lambda x: f"{x:.2f} ⭐")
        st.dataframe(top_rev.rename(columns={'brand':'Brand','model':'Model','year':'Year',
            'Total_Revenue':'Total Revenue','Trips':'Trips','Avg_Rating':'Avg Rating'}), use_container_width=True)
    with l2:
        st.markdown("### ⭐ Top 10 Cars by Rating")
        top_rat = (df.groupby(['brand','model'])
            .agg(Avg_Rating=('rating','mean'), Trips=('id_trip','count'), Avg_Revenue=('revenue','mean'))
            .round(2).sort_values('Avg_Rating', ascending=False).head(10).reset_index())
        top_rat['Avg_Rating']  = top_rat['Avg_Rating'].apply(lambda x: f"{x:.2f} ⭐")
        top_rat['Avg_Revenue'] = top_rat['Avg_Revenue'].apply(lambda x: f"€{x:.0f}")
        st.dataframe(top_rat.rename(columns={'brand':'Brand','model':'Model',
            'Avg_Rating':'Avg Rating','Trips':'Trips','Avg_Revenue':'Avg Revenue'}), use_container_width=True)

    st.divider()
    l3, l4 = st.columns(2)
    with l3:
        st.markdown("### 🏙️ City Revenue Leaderboard")
        city_board = (df.groupby('city_name')
            .agg(Total_Revenue=('revenue','sum'), Trips=('id_trip','count'),
                 Avg_Rating=('rating','mean'), Avg_Revenue=('revenue','mean'))
            .round(2).sort_values('Total_Revenue', ascending=False).reset_index())
        city_board['Total_Revenue'] = city_board['Total_Revenue'].apply(lambda x: f"€{x:,.0f}")
        city_board['Avg_Revenue']   = city_board['Avg_Revenue'].apply(lambda x: f"€{x:.0f}")
        city_board['Avg_Rating']    = city_board['Avg_Rating'].apply(lambda x: f"{x:.2f} ⭐")
        st.dataframe(city_board.rename(columns={'city_name':'City','Total_Revenue':'Total Revenue',
            'Trips':'Trips','Avg_Rating':'Avg Rating','Avg_Revenue':'Avg Revenue/Trip'}), use_container_width=True)
    with l4:
        st.markdown("### 🚘 Brand Leaderboard")
        brand_board = (df.groupby('brand')
            .agg(Total_Revenue=('revenue','sum'), Trips=('id_trip','count'),
                 Avg_Rating=('rating','mean'), Avg_Revenue=('revenue','mean'))
            .round(2).sort_values('Total_Revenue', ascending=False).reset_index())
        brand_board['Total_Revenue'] = brand_board['Total_Revenue'].apply(lambda x: f"€{x:,.0f}")
        brand_board['Avg_Revenue']   = brand_board['Avg_Revenue'].apply(lambda x: f"€{x:.0f}")
        brand_board['Avg_Rating']    = brand_board['Avg_Rating'].apply(lambda x: f"{x:.2f} ⭐")
        st.dataframe(brand_board.rename(columns={'brand':'Brand','Total_Revenue':'Total Revenue',
            'Trips':'Trips','Avg_Rating':'Avg Rating','Avg_Revenue':'Avg Revenue/Trip'}), use_container_width=True)

    st.divider()
    st.markdown("### 🔥 Most Active Customers")
    cust_board = (df.groupby(['name','email'])
        .agg(Trips=('id_trip','count'), Total_Spent=('revenue','sum'), Avg_Rating=('rating','mean'))
        .round(2).sort_values('Trips', ascending=False).head(15).reset_index())
    cust_board['Total_Spent'] = cust_board['Total_Spent'].apply(lambda x: f"€{x:,.0f}")
    cust_board['Avg_Rating']  = cust_board['Avg_Rating'].apply(lambda x: f"{x:.2f} ⭐")
    st.dataframe(cust_board.rename(columns={'name':'Customer','email':'Email',
        'Trips':'Trips','Total_Spent':'Total Spent','Avg_Rating':'Avg Rating'}), use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 4 — TRIP EXPLORER
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="hero"><h1>🔎 Trip Explorer</h1><p>Search and filter individual trips in detail</p></div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    exp_brand  = e1.multiselect("🚘 Brand",  sorted(df['brand'].unique()),     default=sorted(df['brand'].unique()))
    exp_city   = e2.multiselect("🏙️ City",   sorted(df['city_name'].unique()), default=sorted(df['city_name'].unique()))
    exp_rating = e3.multiselect("⭐ Rating",  [1,2,3,4,5], default=[1,2,3,4,5])

    e4, e5 = st.columns(2)
    exp_rev  = e4.slider("💶 Revenue (€)", int(df['revenue'].min()), int(df['revenue'].max()), (int(df['revenue'].min()), int(df['revenue'].max())))
    exp_year = e5.multiselect("📅 Year", sorted(df['year'].unique()), default=sorted(df['year'].unique()))

    df_exp = df[
        df['brand'].isin(exp_brand) &
        df['city_name'].isin(exp_city) &
        df['rating'].isin(exp_rating) &
        df['revenue'].between(*exp_rev) &
        df['year'].isin(exp_year)
    ]

    st.markdown(f"**{len(df_exp):,} trips match your search**")
    st.divider()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Trips",         f"{len(df_exp):,}")
    s2.metric("Total Revenue", f"€{df_exp['revenue'].sum():,.0f}")
    s3.metric("Avg Rating",    f"{df_exp['rating'].mean():.2f}")
    s4.metric("Avg Duration",  f"{df_exp['duration_h'].mean():.1f} hrs")
    st.divider()

    display_cols = ['pickup_time','brand','model','year','city_name','distance','duration_h','revenue','rating','name','email']
    st.dataframe(
        df_exp[display_cols].rename(columns={
            'pickup_time':'Pickup','brand':'Brand','model':'Model','year':'Year',
            'city_name':'City','distance':'Distance (km)','duration_h':'Duration (hrs)',
            'revenue':'Revenue (€)','rating':'Rating','name':'Customer','email':'Email'
        }).sort_values('Pickup', ascending=False).reset_index(drop=True),
        use_container_width=True, height=500
    )