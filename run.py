from app import create_app
from app.routes.google import start_scheduler
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
