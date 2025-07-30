from app import create_app

# Export the create_app function so gunicorn can find it
__all__ = ['create_app']

app = create_app()

if __name__ == '__main__':
    app.run()