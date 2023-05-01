import logging

from FEWS_tools.lib.utils import add_loghandler


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
add_loghandler(logger, logging.StreamHandler, logging.INFO, fmt)
