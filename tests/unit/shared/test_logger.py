import logging
from src.shared.logger import logger

def test_logger_info(caplog):
    with caplog.at_level(logging.INFO):
        logger.info("Test message")
    assert "Test message" in caplog.text

def test_module_path_filter():
    from src.shared.logger import ModulePathFilter
    filter = ModulePathFilter()
    record = logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=10, msg="Test", args=(), exc_info=None)
    assert filter.filter(record)
    assert "test_logger" in record.module_path