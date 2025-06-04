import logging
import inspect
import os
import sys
from pathlib import Path

# Disable existing handlers from the root logger
logging.getLogger().handlers = []

class ModulePathFilter(logging.Filter):
    """Filter that adds module path information to log records"""
    
    def filter(self, record):
        # Override if this record already has pathname info that's not from logging
        if hasattr(record, 'pathname') and not ('logger.py' in record.pathname or 'logging' in record.pathname):
            try:
                path_obj = Path(record.pathname)
                parts = []
                current = path_obj.parent
                
                # Get the filename without extension
                filename = path_obj.stem
                
                # Go back through parents until we find 'src' or reach the root
                found_src = False
                while current.name:
                    if current.name == 'src':
                        found_src = True
                        parts.append(current.name)
                        break
                    parts.append(current.name)
                    current = current.parent
                
                # Reverse to get correct order and join
                parts.reverse()
                
                if found_src:
                    # Create a path like 'src.module.file'
                    record.module_path = '.'.join(parts + [filename])
                else:
                    # Fallback if 'src' not found
                    record.module_path = '.'.join([p for p in parts[-2:] if p] + [filename])
                
                return True
            except:
                pass
        
        # Use stack inspection only if needed
        frame = inspect.currentframe()
        try:
            # Go back multiple frames to find the actual caller
            frames_to_skip = 0
            caller_frame = None
            
            while frame:
                filename = os.path.basename(frame.f_code.co_filename)
                if filename == 'logger.py' or 'logging' in frame.f_code.co_filename:
                    frames_to_skip += 1
                    frame = frame.f_back
                else:
                    caller_frame = frame
                    break
            
            if caller_frame:
                filepath = caller_frame.f_code.co_filename
                
                try:
                    path_obj = Path(filepath)
                    parts = []
                    current = path_obj.parent
                    
                    # Get the filename without extension
                    filename = path_obj.stem
                   
                    # Go back through parents until we find 'src' or reach the root
                    found_src = False
                    while current.name:
                        if current.name == 'src':
                            found_src = True
                            parts.append(current.name)
                            break
                        parts.append(current.name)
                        current = current.parent
                    
                    # Reverse to get correct order and join
                    parts.reverse()
                    
                    if found_src:
                        # Create a path like 'src.module.file'
                        module_path = '.'.join(parts + [filename])
                    else:
                        # Fallback if 'src' not found
                        module_path = '.'.join([p for p in parts[-2:] if p] + [filename])
                    
                    record.module_path = module_path
                except:
                    record.module_path = filepath
            else:
                record.module_path = "unknown"
        finally:
            # Clean up frame reference
            del frame
        
        return True


# Create the GDAI logger
gdai_logger = logging.getLogger("GDAI")
gdai_logger.setLevel(logging.INFO)

# Remove any existing handlers
for handler in gdai_logger.handlers[:]:
    gdai_logger.removeHandler(handler)

# Add a custom filter
gdai_logger.addFilter(ModulePathFilter())


# Add a console handler with the desired format
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] [GDAI] [%(module_path)s] [%(levelname)s]: %(message)s', 
                             '%Y-%m-%d %H:%M:%S,%f')
# Truncate microseconds to 3 digits for milliseconds
old_format = formatter.formatTime
def format_time(self, record, datefmt=None):
    result = old_format(record, datefmt)  # Fixed: don't pass self here
    return result[:-3]  # Remove last 3 digits of microseconds
formatter.formatTime = format_time.__get__(formatter)


console_handler.setFormatter(formatter)
gdai_logger.handlers = [console_handler]
gdai_logger.propagate = False

class Logger:
    """Simple logger class that delegates to the configured GDAI logger"""
    
    def __init__(self):
        """Initialize the logger instance"""
        pass
    
    def info(self, message):
        """Log info message"""
        gdai_logger.info(message)
        
    def warning(self, message):
        """Log warning message"""
        gdai_logger.warning(message)
        
    def error(self, message):
        """Log error message"""
        gdai_logger.error(message)
        
    def debug(self, message):
        """Log debug message"""
        gdai_logger.debug(message)
        
    def critical(self, message):
        """Log critical message"""
        gdai_logger.critical(message)

# Create a singleton logger instance
logger = Logger()

