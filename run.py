# run.py - Entry point for the EV Charging System application

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)