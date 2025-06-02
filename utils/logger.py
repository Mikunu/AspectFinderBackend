import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    _instance = None  # Singleton instance

    def __new__(cls,
                log_file: str = 'app.log',
                max_bytes: int = 1048576,
                backup_count: int = 5):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._configure_logger(log_file, max_bytes, backup_count)
        return cls._instance

    def _configure_logger(self, log_file: str, max_bytes: int, backup_count: int):
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / log_file

        if log_path.exists():
            log_path.unlink()

        self.logger = logging.getLogger('AppLogger')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            file_handler = RotatingFileHandler(
                log_path,
                mode='w',
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
