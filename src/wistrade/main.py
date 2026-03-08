"""
Main entry point for WisTrade application
"""

import sys
from pathlib import Path

from wistrade.core.config import get_config
from wistrade.core.logger import setup_logging, get_logger


def main() -> int:
    """
    Main entry point for WisTrade application
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Load configuration
        config = get_config()
        app_config = config.config
        
        # Setup logging
        log_level = app_config.log_level
        log_file = config.get("logging.file.path", "logs/wistrade.log")
        setup_logging(
            log_level=log_level,
            log_file=log_file,
            enable_json=True,
            enable_checksum=True,
        )
        
        logger = get_logger(__name__)
        logger.info(
            "application_starting",
            app_name=app_config.name,
            version=app_config.version,
            environment=app_config.environment,
        )
        
        # TODO: Initialize application components
        # - Database manager
        # - Broker adapters
        # - AI core
        # - Trading engine
        # - UI application
        
        logger.info("application_initialized")
        
        # Start PyQt6 application
        from PyQt6.QtWidgets import QApplication
        from wistrade.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName(app_config.name)
        app.setApplicationVersion(app_config.version)
        
        window = MainWindow()
        window.show()
        
        logger.info("UI_application_started")
        
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
