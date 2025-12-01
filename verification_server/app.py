"""
Verification Server Main Application
Flask application for handling verification flow and bypass detection.
"""

import logging
from flask import Flask
from flask_cors import CORS

# Import routes
from verification_server.routes import verify_routes, shortlink_routes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure Flask application.
    
    Args:
        config: Configuration dictionary (optional)
    
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        # Default configuration
        app.config.update({
            'SECRET_KEY': 'your-secret-key-change-in-production',
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
        })
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(verify_routes)
    app.register_blueprint(shortlink_routes)
    
    # Root route
    @app.route('/')
    def index():
        return {
            'status': 'online',
            'service': 'verification_server',
            'version': '1.0.0'
        }
    
    # Health check
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'verification_server'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    logger.info("Verification server application created")
    
    return app


def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Run the verification server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    try:
        # Connect to database
        from config.database import connect_database
        connect_database()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    # Create app
    app = create_app()
    
    # Run server
    logger.info(f"Starting verification server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


# Entry point for running standalone
if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    logger.info("="*50)
    logger.info("VERIFICATION SERVER")
    logger.info("="*50)
    
    run_server(port=port, debug=False)