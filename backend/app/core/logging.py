import logging
import sys
from app.core.config import settings

def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence overly verbose botocore logs in normal mode
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('passlib').setLevel(logging.WARNING)

logger = logging.getLogger('SCCG')
