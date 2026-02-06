import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="March Bradness", page_icon="🏀", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        margin-bottom: 0.5rem;
        background-color: #e8e8e8;
        border-radius: 8px 8px 0 0;
        padding: 4px 4px 0 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #d0d0d0;
        border-radius: 8px 8px 0 0;
        padding: 10px 30px;
        margin-right: 2px;
        border: 1px solid #c0c0c0;
        border-bottom: none;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
        position: relative;
        z-index: 1;
    }
    .stTabs [data-baseweb="tab-panel"] {
        border: 1px solid #c0c0c0;
        border-top: none;
        padding: 1rem;
        background-color: #ffffff;
    }
    .stRadio > div {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

CATEGORIES = {
    "Summit Registrants": 5,
    "CoCo App Creation": 30,
    "In-Person Meetings": 30,
    "Hands On Labs": 50,
    "CECs": 50,
    "Implementation Starts": 50,
    "New POCs Started": 80,
    "Technical Wins": 160,
    "Go-Lives": 160,
}

DATA_FILE = Path(__file__).parent / "march_bradness_data.json"
LOGO_FILE = Path(__file__).parent / "logo.png"
BANG_SOUND_FILE = Path(__file__).parent / "MikeBreenBang.mp3"


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"team_members": [], "weekly_data": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_week_key(date):
    start = date - timedelta(days=date.weekday())
    return start.strftime("%Y-%m-%d")


def calculate_points(activities):
    total = 0
    for category, count in activities.items():
        if category in CATEGORIES:
            total += CATEGORIES[category] * count
    return total


def get_leaderboard(data):
    scores = {}
    for member in data["team_members"]:
        total = 0
        for week_key, week_data in data["weekly_data"].items():
            if member in week_data:
                total += calculate_points(week_data[member])
        scores[member] = total
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def get_member_breakdown(data, member):
    breakdown = {cat: 0 for cat in CATEGORIES}
    for week_key, week_data in data["weekly_data"].items():
        if member in week_data:
            for cat, count in week_data[member].items():
                if cat in breakdown:
                    breakdown[cat] += count
    return breakdown


def get_member_weekly_points(data, member):
    weekly = {}
    for week_key, week_data in data["weekly_data"].items():
        if member in week_data:
            pts = calculate_points(week_data[member])
            if pts > 0:
                weekly[week_key] = pts
    return dict(sorted(weekly.items()))


def get_weekly_leaderboard(data, week_key):
    scores = {}
    if week_key in data["weekly_data"]:
        for member in data["team_members"]:
            if member in data["weekly_data"][week_key]:
                scores[member] = calculate_points(data["weekly_data"][week_key][member])
            else:
                scores[member] = 0
    else:
        for member in data["team_members"]:
            scores[member] = 0
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def get_all_weeks(data):
    weeks = set()
    for week_key in data["weekly_data"]:
        for member_data in data["weekly_data"][week_key].values():
            if any(v > 0 for v in member_data.values()):
                weeks.add(week_key)
                break
    return sorted(weeks, reverse=True)


st.session_state.setdefault("data", load_data())
st.session_state.setdefault("music_playing", True)

SNOWFLAKE_ICON_FILE = Path(__file__).parent / "snowflake_icon.png"

music_col1, music_col2 = st.columns([10, 1])
with music_col2:
    music_toggle = st.toggle("🔊", value=st.session_state.music_playing, help="Toggle music")
    if music_toggle != st.session_state.music_playing:
        st.session_state.music_playing = music_toggle
        st.rerun()

youtube_video_id = "a9euMKtYLK0"
autoplay = 1 if st.session_state.music_playing else 0
mute_param = 0 if st.session_state.music_playing else 1

st.markdown(
    f"""
    <iframe 
        id="youtube-player"
        width="0" 
        height="0" 
        src="https://www.youtube.com/embed/{youtube_video_id}?autoplay={autoplay}&mute={mute_param}&loop=1&playlist={youtube_video_id}&controls=0&showinfo=0&rel=0&enablejsapi=1"
        frameborder="0" 
        allow="autoplay; encrypted-media"
        style="display: none;">
    </iframe>
    """,
    unsafe_allow_html=True
)

if LOGO_FILE.exists():
    import base64
    with open(LOGO_FILE, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    
    snowflake_pattern = ""
    if SNOWFLAKE_ICON_FILE.exists():
        with open(SNOWFLAKE_ICON_FILE, "rb") as f:
            icon_data = base64.b64encode(f.read()).decode()
        snowflake_pattern = f"url('data:image/png;base64,{icon_data}')"
    
    st.markdown(
        f"""
        <div style="position: relative; width: 100%; height: 300px; overflow: hidden; margin-bottom: 0.5rem; border-radius: 8px;">
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: #000000; background-image: {snowflake_pattern}; background-repeat: repeat; background-size: 50px 50px; opacity: 0.7;"></div>
            <div style="position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
                <img src="data:image/png;base64,{logo_data}" 
                     style="max-height: 280px; object-fit: contain;">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

tab1, tab2, tab3 = st.tabs(["Leaderboard", "Enter Points", "Manage Team"])

with tab1:
    leaderboard = get_leaderboard(st.session_state.data)
    
    if not leaderboard:
        st.info("No team members yet. Add members in the 'Manage Team' tab.")
    else:
        all_weeks = get_all_weeks(st.session_state.data)
        
        view_mode = st.radio(
            "View",
            ["All Time", "By Week"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if view_mode == "By Week" and all_weeks:
            selected_week_view = st.selectbox("Select Week", all_weeks, format_func=lambda x: f"Week of {x}")
            weekly_lb = get_weekly_leaderboard(st.session_state.data, selected_week_view)
            
            with st.container(horizontal=True):
                week_total = sum(weekly_lb.values())
                st.metric("Week Total Points", f"{week_total:,}", border=True)
                st.metric("Team Members", len([m for m, p in weekly_lb.items() if p > 0]), border=True)
                if weekly_lb:
                    week_leader = list(weekly_lb.keys())[0]
                    if weekly_lb[week_leader] > 0:
                        st.metric("Week Leader", week_leader, f"{weekly_lb[week_leader]:,} pts", border=True)
            
            st.subheader(f"Week of {selected_week_view}")
            
            for rank, (member, points) in enumerate(weekly_lb.items(), 1):
                if points == 0:
                    continue
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                
                with st.expander(f"{medal} **{member}** — {points:,} points"):
                    week_data = st.session_state.data["weekly_data"].get(selected_week_view, {}).get(member, {})
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Activity Counts**")
                        for cat, count in week_data.items():
                            if count > 0:
                                pts = count * CATEGORIES[cat]
                                st.write(f"- {cat}: **{count}** ({pts:,} pts)")
                    with col2:
                        st.markdown("**Points by Category**")
                        chart_data = [{"Category": cat, "Points": count * CATEGORIES[cat]} for cat, count in week_data.items() if count > 0]
                        if chart_data:
                            st.bar_chart(pd.DataFrame(chart_data), x="Category", y="Points", horizontal=True)
        
        elif view_mode == "By Week" and not all_weeks:
            st.info("No weekly data yet. Enter points in the 'Enter Points' tab.")
        
        else:
            top_3 = list(leaderboard.items())[:3]
            if len(top_3) >= 3 and top_3[0][1] > 0:
                st.markdown(
                    """
                    <style>
                    .podium-container {
                        display: flex;
                        justify-content: center;
                        align-items: flex-end;
                        gap: 15px;
                        margin: 0 auto 1rem auto;
                        max-width: 900px;
                    }
                    .podium-place {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        text-align: center;
                    }
                    .podium-name {
                        font-weight: bold;
                        font-size: 1.1rem;
                        margin-bottom: 5px;
                        color: #000000;
                    }
                    .podium-points {
                        font-size: 0.9rem;
                        color: #555555;
                        margin-bottom: 8px;
                    }
                    .podium-block {
                        width: 220px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-size: 2rem;
                        font-weight: bold;
                        color: #ffffff;
                        border-radius: 8px 8px 0 0;
                    }
                    .gold-block {
                        background: linear-gradient(180deg, #c41e3a 0%, #8b1528 100%);
                        height: 100px;
                    }
                    .silver-block {
                        background: linear-gradient(180deg, #1a2744 0%, #0f1829 100%);
                        height: 70px;
                    }
                    .bronze-block {
                        background: linear-gradient(180deg, #6eb5e0 0%, #4a95c0 100%);
                        height: 50px;
                    }
                    .medal-emoji {
                        font-size: 2.5rem;
                        margin-bottom: 5px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                second = top_3[1] if len(top_3) > 1 else ("", 0)
                first = top_3[0]
                third = top_3[2] if len(top_3) > 2 else ("", 0)
                
                podium_html = f"""
                <div class="podium-container">
                    <div class="podium-place">
                        <div class="medal-emoji">🥈</div>
                        <div class="podium-name">{second[0]}</div>
                        <div class="podium-points">{second[1]:,} pts</div>
                        <div class="podium-block silver-block">2</div>
                    </div>
                    <div class="podium-place">
                        <div class="medal-emoji">🥇</div>
                        <div class="podium-name">{first[0]}</div>
                        <div class="podium-points">{first[1]:,} pts</div>
                        <div class="podium-block gold-block">1</div>
                    </div>
                    <div class="podium-place">
                        <div class="medal-emoji">🥉</div>
                        <div class="podium-name">{third[0]}</div>
                        <div class="podium-points">{third[1]:,} pts</div>
                        <div class="podium-block bronze-block">3</div>
                    </div>
                </div>
                """
                st.markdown(podium_html, unsafe_allow_html=True)
            
            with st.container(horizontal=True):
                total_points = sum(leaderboard.values())
                st.metric("Total Team Points", f"{total_points:,}", border=True)
                st.metric("Team Members", len(leaderboard), border=True)
                if leaderboard:
                    leader = list(leaderboard.keys())[0]
                    st.metric("Current Leader", leader, f"{leaderboard[leader]:,} pts", border=True)
            
            st.subheader("Standings")
            
            for rank, (member, points) in enumerate(leaderboard.items(), 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                
                with st.expander(f"{medal} **{member}** — {points:,} points"):
                    breakdown = get_member_breakdown(st.session_state.data, member)
                    weekly_points = get_member_weekly_points(st.session_state.data, member)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Activity Counts (All Time)**")
                        for cat, count in breakdown.items():
                            if count > 0:
                                pts = count * CATEGORIES[cat]
                                st.write(f"- {cat}: **{count}** ({pts:,} pts)")
                    
                    with col2:
                        st.markdown("**Points by Category**")
                        chart_data = []
                        for cat, count in breakdown.items():
                            if count > 0:
                                chart_data.append({"Category": cat, "Points": count * CATEGORIES[cat]})
                        if chart_data:
                            df = pd.DataFrame(chart_data)
                            st.bar_chart(df, x="Category", y="Points", horizontal=True)
                    
                    if weekly_points:
                        st.markdown("**Points by Week**")
                        week_df = pd.DataFrame([
                            {"Week": wk, "Points": pts} for wk, pts in weekly_points.items()
                        ])
                        st.bar_chart(week_df, x="Week", y="Points")

def get_member_weeks(data, member):
    weeks = []
    for week_key, week_data in data["weekly_data"].items():
        if member in week_data and any(v > 0 for v in week_data[member].values()):
            weeks.append(week_key)
    return sorted(weeks, reverse=True)

with tab2:
    if not st.session_state.data["team_members"]:
        st.warning("Add team members first in the 'Manage Team' tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_member = st.selectbox("Team Member", st.session_state.data["team_members"])
        with col2:
            selected_week = st.date_input("Week of", value=datetime.now())
        
        week_key = get_week_key(selected_week)
        
        existing_weeks = get_member_weeks(st.session_state.data, selected_member)
        if existing_weeks:
            st.caption(f"Editing week: **{week_key}** | Previous entries: {', '.join(existing_weeks)}")
        else:
            st.caption(f"Entering data for week starting: {week_key}")
        
        if week_key not in st.session_state.data["weekly_data"]:
            st.session_state.data["weekly_data"][week_key] = {}
        if selected_member not in st.session_state.data["weekly_data"][week_key]:
            st.session_state.data["weekly_data"][week_key][selected_member] = {cat: 0 for cat in CATEGORIES}
        
        current = st.session_state.data["weekly_data"][week_key][selected_member]
        
        st.subheader("Enter Activity Counts")
        
        new_values = {}
        cols = st.columns(3)
        for i, (category, point_value) in enumerate(CATEGORIES.items()):
            with cols[i % 3]:
                new_values[category] = st.number_input(
                    f"{category} ({point_value} pts each)",
                    min_value=0,
                    value=current.get(category, 0),
                    key=f"input_{category}_{selected_member}_{week_key}"
                )
        
        weekly_total = calculate_points(new_values)
        st.metric("Weekly Points Total", f"{weekly_total:,}", border=True)
        
        if st.button("Save Points", type="primary", use_container_width=True):
            st.session_state.data["weekly_data"][week_key][selected_member] = new_values
            save_data(st.session_state.data)
            st.session_state["play_bang"] = True
            st.success(f"Saved {weekly_total:,} points for {selected_member} (Week of {week_key})")
            st.rerun()
        
        if st.session_state.get("play_bang", False):
            if BANG_SOUND_FILE.exists():
                import base64
                with open(BANG_SOUND_FILE, "rb") as f:
                    bang_audio = base64.b64encode(f.read()).decode()
                st.markdown(
                    f"""
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{bang_audio}" type="audio/mp3">
                    </audio>
                    """,
                    unsafe_allow_html=True
                )
            st.session_state["play_bang"] = False

with tab3:
    st.subheader("Team Members")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        new_member = st.text_input("Add new team member", placeholder="Enter name")
    with col2:
        st.write("")
        st.write("")
        if st.button("Add Member", use_container_width=True):
            if new_member and new_member not in st.session_state.data["team_members"]:
                st.session_state.data["team_members"].append(new_member)
                save_data(st.session_state.data)
                st.success(f"Added {new_member}")
                st.rerun()
            elif new_member in st.session_state.data["team_members"]:
                st.error("Member already exists")
    
    if st.session_state.data["team_members"]:
        st.markdown("**Current Team:**")
        for idx, member in enumerate(st.session_state.data["team_members"]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(
                    "Name",
                    value=member,
                    key=f"edit_name_{idx}",
                    label_visibility="collapsed"
                )
            with col2:
                if st.button("Rename", key=f"rename_{idx}", use_container_width=True):
                    if new_name and new_name != member:
                        if new_name in st.session_state.data["team_members"]:
                            st.error("Name already exists")
                        else:
                            st.session_state.data["team_members"][idx] = new_name
                            for week_key in st.session_state.data["weekly_data"]:
                                if member in st.session_state.data["weekly_data"][week_key]:
                                    st.session_state.data["weekly_data"][week_key][new_name] = st.session_state.data["weekly_data"][week_key].pop(member)
                            save_data(st.session_state.data)
                            st.rerun()
            with col3:
                if st.button("Remove", key=f"remove_{member}", use_container_width=True):
                    st.session_state.data["team_members"].remove(member)
                    for week_key in st.session_state.data["weekly_data"]:
                        if member in st.session_state.data["weekly_data"][week_key]:
                            del st.session_state.data["weekly_data"][week_key][member]
                    save_data(st.session_state.data)
                    st.rerun()
    
    st.divider()
    st.subheader("Point Values Reference")
    ref_df = pd.DataFrame([
        {"Activity": cat, "Points": pts} 
        for cat, pts in CATEGORIES.items()
    ])
    st.dataframe(ref_df, hide_index=True, use_container_width=True)
