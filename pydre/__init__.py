import logging

logger = logging.getLogger('PydreLogger')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s()] %(message)s"
logging.basicConfig(format=FORMAT)
