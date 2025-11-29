"""
Quick script to view MongoDB data from SEMSOL engagement monitoring.
Run this to see what's stored in your local MongoDB.
"""

from utils.mongodb_handler import SessionMetricsDB
from datetime import datetime, timedelta
import json

def main():
    print("=" * 70)
    print("🗄️  SEMSOL MongoDB Data Viewer")
    print("=" * 70)
    
    try:
        # Connect to MongoDB
        db = SessionMetricsDB(
            connection_string="mongodb://localhost:27017/",
            database_name="semsol_engagement"
        )
        print("✅ Connected to MongoDB\n")
        
        # 1. Show database statistics
        print("📊 DATABASE STATISTICS")
        print("-" * 70)
        sessions_count = db.sessions_collection.count_documents({})
        metrics_count = db.metrics_collection.count_documents({})
        print(f"Total Sessions: {sessions_count}")
        print(f"Total Metrics: {metrics_count}")
        print()
        
        # 2. Show recent sessions
        print("📋 RECENT SESSIONS (Last 10)")
        print("-" * 70)
        sessions = db.get_recent_sessions(limit=10)
        
        if not sessions:
            print("❌ No sessions found in database")
            print("\nTo add test data, run: python mongodb_examples.py")
        else:
            for i, session in enumerate(sessions, 1):
                print(f"\n{i}. Session ID: {session['session_id']}")
                print(f"   Start: {session['start_time']}")
                print(f"   Duration: {session['duration_seconds']:.1f}s")
                print(f"   Frames: {session['frames_processed']}")
                print(f"   Blinks: {session['total_blinks']}")
                
                # Show engagement summary
                summary = session['summary']['engagement_summary']
                print(f"   Engagement:")
                print(f"     - Highly Engaged: {summary['highly_engaged_percent']:.1f}%")
                print(f"     - Engaged: {summary['engaged_percent']:.1f}%")
                print(f"     - Partially Engaged: {summary['partially_engaged_percent']:.1f}%")
                print(f"     - Disengaged: {summary['disengaged_percent']:.1f}%")
        
        # 3. Show aggregate statistics
        if sessions_count > 0:
            print("\n" + "=" * 70)
            print("📈 AGGREGATE STATISTICS (All Sessions)")
            print("-" * 70)
            stats = db.get_engagement_statistics()
            
            if stats:
                print(f"Total Frames Analyzed: {stats.get('total_frames', 0):,}")
                print("\nEngagement Distribution:")
                
                labels = {1: "Highly Engaged", 2: "Engaged", 3: "Partially Engaged", 4: "Disengaged"}
                for level in [1, 2, 3, 4]:
                    if level in stats.get('engagement_distribution', {}):
                        data = stats['engagement_distribution'][level]
                        print(f"  {labels[level]:20s}: {data['percentage']:6.2f}% "
                              f"({data['count']:,} frames, avg confidence: {data['avg_confidence']:.2f})")
        
        # 4. Interactive menu
        print("\n" + "=" * 70)
        print("🔍 INTERACTIVE OPTIONS")
        print("-" * 70)
        print("1. View detailed metrics for a session")
        print("2. Export session to JSON")
        print("3. Export session to CSV")
        print("4. View sessions from last 24 hours")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1" and sessions:
            session_id = input("Enter session ID: ").strip()
            metrics_df = db.get_session_metrics(session_id)
            if not metrics_df.empty:
                print(f"\n📊 Metrics for {session_id}:")
                print(metrics_df.to_string())
            else:
                print("❌ No metrics found for this session")
        
        elif choice == "2" and sessions:
            session_id = input("Enter session ID: ").strip()
            session = db.get_session(session_id)
            if session:
                filename = f"{session_id}.json"
                with open(filename, 'w') as f:
                    json.dump(session, f, indent=2, default=str)
                print(f"✅ Exported to {filename}")
            else:
                print("❌ Session not found")
        
        elif choice == "3" and sessions:
            session_id = input("Enter session ID: ").strip()
            metrics_df = db.get_session_metrics(session_id)
            if not metrics_df.empty:
                filename = f"{session_id}.csv"
                metrics_df.to_csv(filename, index=False)
                print(f"✅ Exported to {filename}")
            else:
                print("❌ No metrics found")
        
        elif choice == "4":
            yesterday = datetime.now() - timedelta(days=1)
            recent_sessions = db.get_sessions_by_date_range(yesterday, datetime.now())
            print(f"\n📅 Found {len(recent_sessions)} sessions in last 24 hours:")
            for session in recent_sessions:
                print(f"  - {session['session_id']} ({session['start_time']})")
        
        db.close()
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running: net start MongoDB")
        print("2. Check connection string in mongodb_config.py")
        print("3. Verify MongoDB is installed: mongo --version")

if __name__ == "__main__":
    main()
