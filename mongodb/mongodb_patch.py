"""
MongoDB Integration Patch for app.py
=====================================

This file contains the exact code snippets to add MongoDB integration to your app.py.
Follow the instructions below to integrate MongoDB support.

BACKUP FIRST: Make sure you have a backup of app.py before making changes!
"""

# ==============================================================================
# STEP 1: Add imports at the top (after line 26, after "from PIL import Image")
# ==============================================================================

IMPORTS_TO_ADD = """
# MongoDB integration
try:
    from utils.mongodb_handler import SessionMetricsDB, save_session_to_mongodb
    from mongodb_config import MONGODB_CONFIG, AUTO_SAVE_CONFIG
    from datetime import timedelta
    MONGODB_AVAILABLE = True
except ImportError as e:
    MONGODB_AVAILABLE = False
    print(f"⚠️ MongoDB not available: {e}")
"""

# ==============================================================================
# STEP 2: Add MongoDB settings to sidebar (after line 161, after gaze_weight_path)
# ==============================================================================

MONGODB_SIDEBAR_SETTINGS = """
st.sidebar.divider()

# MongoDB Settings
st.sidebar.markdown("### 🗄️ Database Storage")
enable_mongodb = st.sidebar.checkbox(
    "Enable MongoDB Auto-Save", 
    value=AUTO_SAVE_CONFIG['enabled'] if MONGODB_AVAILABLE else False,
    help="Automatically save sessions to MongoDB when stopped",
    disabled=not MONGODB_AVAILABLE
)

if enable_mongodb and MONGODB_AVAILABLE:
    mongodb_status_placeholder = st.sidebar.empty()
    
    # Test MongoDB connection
    try:
        test_db = SessionMetricsDB(
            connection_string=MONGODB_CONFIG['connection_string'],
            database_name=MONGODB_CONFIG['database_name']
        )
        test_db.close()
        mongodb_status_placeholder.success("✅ MongoDB Connected")
    except Exception as e:
        mongodb_status_placeholder.error(f"❌ MongoDB: {str(e)[:40]}")
        enable_mongodb = False
elif not MONGODB_AVAILABLE:
    st.sidebar.warning("⚠️ MongoDB not installed")
"""

# ==============================================================================
# STEP 3: Modify the "Stop Monitoring" button (around line 187-190)
# ==============================================================================

# FIND THIS CODE:
OLD_STOP_BUTTON_CODE = """
else:
    if st.sidebar.button("⏹ Stop Monitoring", type="secondary", use_container_width=True):
        st.session_state.monitoring = False
        st.session_state.session_data['session_end'] = datetime.now()
        st.rerun()
"""

# REPLACE WITH THIS:
NEW_STOP_BUTTON_CODE = """
else:
    if st.sidebar.button("⏹ Stop Monitoring", type="secondary", use_container_width=True):
        st.session_state.monitoring = False
        st.session_state.session_data['session_end'] = datetime.now()
        
        # Auto-save to MongoDB if enabled
        if enable_mongodb and MONGODB_AVAILABLE:
            try:
                # Generate visualizations and report
                visualizations = generate_session_visualizations(st.session_state.session_data)
                if visualizations:
                    session_report = generate_session_report(
                        st.session_state.session_data, 
                        visualizations
                    )
                    
                    # Save to MongoDB
                    session_id = save_session_to_mongodb(
                        st.session_state.session_data,
                        session_report,
                        MONGODB_CONFIG['connection_string']
                    )
                    
                    # Store session_id for reference
                    st.session_state.last_saved_session_id = session_id
                    st.sidebar.success(f"✅ Saved: {session_id}")
                    
            except Exception as e:
                st.sidebar.error(f"⚠️ DB save failed: {str(e)[:50]}")
        
        st.rerun()
"""

# ==============================================================================
# STEP 4: Add Session History Tab (MAJOR CHANGE - wrap existing monitoring code)
# ==============================================================================

# FIND THIS (around line 585):
OLD_MONITORING_START = """
if st.session_state.monitoring:
    col1, col2 = st.columns([2, 1])
"""

# REPLACE WITH THIS:
NEW_TAB_STRUCTURE_START = """
# Create tabs for Live Monitoring and History
tab1, tab2 = st.tabs(["🎥 Live Monitoring", "📊 Session History"])

with tab1:
    # Live monitoring content
    if st.session_state.monitoring:
        col1, col2 = st.columns([2, 1])
"""

# Then at the END of the monitoring code (after the while loop ends, around line 800+),
# ADD THIS BEFORE THE FINAL cleanup section:

SESSION_HISTORY_TAB_CODE = """
with tab2:
    st.subheader("📊 Session History")
    
    if not enable_mongodb or not MONGODB_AVAILABLE:
        st.warning("⚠️ Enable MongoDB in sidebar to view session history")
        st.info("MongoDB allows you to store and query past monitoring sessions.")
    else:
        try:
            db = SessionMetricsDB(
                connection_string=MONGODB_CONFIG['connection_string'],
                database_name=MONGODB_CONFIG['database_name']
            )
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                num_sessions = st.number_input("Sessions to show", 1, 50, 10)
            with col2:
                days_back = st.number_input("Days back", 1, 365, 7)
            with col3:
                if st.button("🔄 Refresh History"):
                    st.rerun()
            
            # Get sessions
            sessions = db.get_recent_sessions(limit=num_sessions)
            
            if not sessions:
                st.info("📭 No sessions found in database")
                st.markdown("**To add test data:** Run `python add_test_data.py`")
            else:
                st.success(f"Found {len(sessions)} sessions")
                
                # Display sessions
                for session in sessions:
                    with st.expander(
                        f"📅 {session['session_id']} - "
                        f"{session['start_time'].strftime('%Y-%m-%d %H:%M:%S')} "
                        f"({session['duration_seconds']:.0f}s, {session['frames_processed']} frames)"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📊 Session Info**")
                            st.write(f"Duration: {session['duration_seconds']:.1f}s")
                            st.write(f"Frames: {session['frames_processed']:,}")
                            st.write(f"Blinks: {session['total_blinks']}")
                            st.write(f"Start: {session['start_time'].strftime('%H:%M:%S')}")
                        
                        with col2:
                            st.markdown("**🎯 Engagement Summary**")
                            summary = session['summary']['engagement_summary']
                            st.write(f"🟢 Highly Engaged: {summary['highly_engaged_percent']:.1f}%")
                            st.write(f"🟡 Engaged: {summary['engaged_percent']:.1f}%")
                            st.write(f"🟠 Partially Engaged: {summary['partially_engaged_percent']:.1f}%")
                            st.write(f"🔴 Disengaged: {summary['disengaged_percent']:.1f}%")
                        
                        # View detailed metrics
                        if st.button("📊 View Detailed Metrics", key=f"view_{session['session_id']}"):
                            with st.spinner("Loading metrics..."):
                                metrics_df = db.get_session_metrics(session['session_id'])
                                
                                if not metrics_df.empty:
                                    st.dataframe(metrics_df, use_container_width=True, height=300)
                                    
                                    # Download button
                                    csv = metrics_df.to_csv(index=False)
                                    st.download_button(
                                        "⬇️ Download CSV",
                                        csv,
                                        f"{session['session_id']}.csv",
                                        "text/csv",
                                        key=f"download_{session['session_id']}"
                                    )
                                else:
                                    st.warning("No metrics found for this session")
                        
                        # Delete session
                        col_del1, col_del2 = st.columns([3, 1])
                        with col_del2:
                            if st.button("🗑️ Delete", key=f"delete_{session['session_id']}", type="secondary"):
                                if db.delete_session(session['session_id']):
                                    st.success("✅ Session deleted")
                                    st.rerun()
                                else:
                                    st.error("❌ Delete failed")
            
            # Aggregate statistics
            if sessions:
                st.divider()
                st.subheader("📈 Aggregate Statistics")
                
                stats = db.get_engagement_statistics()
                if stats:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Frames Analyzed", f"{stats.get('total_frames', 0):,}")
                        
                        # Show engagement breakdown
                        st.markdown("**Engagement Distribution:**")
                        labels = {1: "Highly Engaged", 2: "Engaged", 3: "Partially Engaged", 4: "Disengaged"}
                        for level in [1, 2, 3, 4]:
                            if level in stats.get('engagement_distribution', {}):
                                data = stats['engagement_distribution'][level]
                                st.write(f"{labels[level]}: {data['percentage']:.1f}% ({data['count']:,} frames)")
                    
                    with col2:
                        # Create pie chart
                        if 'engagement_distribution' in stats:
                            labels_list = ['Highly Engaged', 'Engaged', 'Partially Engaged', 'Disengaged']
                            values = [
                                stats['engagement_distribution'].get(i, {}).get('count', 0) 
                                for i in [1, 2, 3, 4]
                            ]
                            
                            fig = go.Figure(data=[go.Pie(
                                labels=labels_list,
                                values=values,
                                marker=dict(colors=['#00ff00', '#ffff00', '#ffa500', '#ff0000']),
                                hole=0.3
                            )])
                            fig.update_layout(
                                title='Overall Engagement Distribution',
                                height=300,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)
            
            db.close()
            
        except Exception as e:
            st.error(f"❌ Error loading session history: {e}")
            st.info("Make sure MongoDB is running and accessible")
"""

# ==============================================================================
# INSTRUCTIONS
# ==============================================================================

INSTRUCTIONS = """
HOW TO APPLY THIS PATCH:
========================

1. BACKUP YOUR app.py:
   copy app.py app_backup_before_mongodb.py

2. Open app.py in your editor

3. Add the imports (STEP 1):
   - Find line ~26 (after "from PIL import Image")
   - Add the IMPORTS_TO_ADD code

4. Add MongoDB sidebar settings (STEP 2):
   - Find line ~161 (after gaze_weight_path text input)
   - Add the MONGODB_SIDEBAR_SETTINGS code

5. Modify Stop button (STEP 3):
   - Find the "Stop Monitoring" button code (around line 187-190)
   - Replace OLD_STOP_BUTTON_CODE with NEW_STOP_BUTTON_CODE

6. Add tabs structure (STEP 4):
   - Find where monitoring starts (around line 585)
   - Wrap the monitoring code in tab1
   - Add SESSION_HISTORY_TAB_CODE at the end (before cleanup)

7. Test:
   streamlit run app.py

ALTERNATIVE: Use the pre-made file
===================================
I can create a complete app_with_mongodb.py file for you.
Just rename it to app.py when ready.
"""

print(__doc__)
print(INSTRUCTIONS)
