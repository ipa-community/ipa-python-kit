import logging
import logging.config

from ipa.logging import get_default_dict_config_builder


def test_logger():
    builder = get_default_dict_config_builder()
    logging.config.dictConfig(builder.build())
    log = logging.getLogger("app")
    log.info("test")
