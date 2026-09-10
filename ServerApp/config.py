# Statement for enabling the development environment
import os

DEBUG = os.environ.get('SECURETEA_DEBUG', '0') == '1'
HOST = os.environ.get('SECURETEA_HOST', '0.0.0.0')

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. Generate one with:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
SESS_KEY = os.environ.get('SECURETEA_SESS_KEY', '')
SEC_KEY = os.environ.get('SECURETEA_SEC_KEY', '')

CSRF_SESSION_KEY = SESS_KEY

# Secret key for signing cookies
SECRET_KEY = SEC_KEY
