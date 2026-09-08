import logging
logger=logging.getLogger("app")
logger.setLevel("INFO")
handler=logging.StreamHandler()
formatter=logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)