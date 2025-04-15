from job_tracker import create_app, db
import argparse

# Setup command line arguments
parser = argparse.ArgumentParser(description='Run the Job Tracker application')
parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
args = parser.parse_args()

app = create_app()

# Create database tables within application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print(f"Starting server on {args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port)
