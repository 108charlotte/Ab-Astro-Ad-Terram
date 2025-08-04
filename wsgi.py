from app import create_app
import os

app = create_app()

# Initialize database on startup if it doesn't exist
with app.app_context():
    from app.db import get_db, init_db, populate_db
    
    db_path = app.config['DATABASE']
    
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")
    
    # Initialize database if it doesn't exist
    if not os.path.exists(db_path):
        print("Database file not found, initializing...")
        try:
            init_db()
            populate_db()
            print("Database initialized and populated successfully!")
        except Exception as e:
            print(f"Database initialization error: {e}")
    else:
        print("Database file exists, checking if populated...")
        try:
            db = get_db()
            result = db.execute("SELECT COUNT(*) FROM locations").fetchone()
            if result[0] == 0:
                print("Database empty, populating...")
                populate_db()
                print("Database populated!")
            else:
                print(f"Database has {result[0]} locations, ready to go!")
        except Exception as e:
            print(f"Database check failed, reinitializing: {e}")
            init_db()
            populate_db()

if __name__ == "__main__":
    app.run()