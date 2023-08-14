import datetime
import inspect
from dataclasses import dataclass
from functools import wraps
from typing import Dict, Optional


@dataclass(frozen=True)
class Plumber:
    name: str
    function: str
    color: str
    code: str
    doc: str
    specificity: float
    version: str = "0.0"


# Global dictionary to store registered functions and their source code
plumbers_registry: Dict[str, Plumber] = {}


def plumber(name="", color="pink", specificity=10.0):
    def decorator(func):
        plumber_name = name
        if name == "":
            plumber_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Get the source code of the function
        source_code = inspect.getsource(func)

        # Register the function and its source code in the global dictionary
        plumb = Plumber(
            name=plumber_name,
            function=func.__name__,
            color=color,  # Use the provided color argument
            code=source_code,
            doc=func.__doc__,
            specificity=specificity,
        )
        plumbers_registry[func.__name__] = plumb

        return wrapper

    return decorator


@plumber(
    name="String",
    color='rgb(255, 153, 153)',
    specificity=0,
)
def string_parser(input_string) -> str:
    """Accepts any string"""
    return input_string


@plumber(
    name="Integer",
    color='rgb(255, 183, 153)',
    specificity=7,
)
def integer_parser(input_string) -> int:
    """Accepts integers"""
    return int(input_string)


@plumber(
    name="Integer or NA",
    color='rgb(225, 153, 113)',
    specificity=6,
)
def integer_or_na_parser(input_string) -> Optional[int]:
    """Accepts integers"""
    if input_string in ["NA", "N/A", ""]:
        return None
    return int(input_string)


@plumber(
    name="Numerical value (float)",
    color='rgb(255, 214, 153)',
    specificity=5,
)
def float_parser(input_string) -> float:
    """Accepts floating point numbers"""
    return float(input_string)


@plumber(
    name="Date (MM-DD-YYYY)",
    color='rgb(255, 244, 153)',
    specificity=15,
)
def date_parser(input_string) -> datetime.datetime:
    """Accepts date in the format MM-DD-YYYY"""
    from datetime import datetime
    return datetime.strptime(input_string, "%m-%d-%Y")


@plumber(
    name="Boolean (True/False)",
    color='rgb(234, 255, 153)',
    specificity=41,
)
def boolean_parser(input_string) -> bool:
    """Boolean values (True or False)"""
    lowercase = input_string.lower()
    if lowercase in ['true', '1', 'yes']:
        return True
    elif lowercase in ['false', '0', 'no']:
        return False
    else:
        raise Exception("Invalid boolean")


@plumber(
    name="Email",
    color='rgb(204, 255, 153)',
    specificity=20,
)
def email_parser(input_string) -> str:
    """Accepts email addresses"""
    import re
    if re.match(r"[^@]+@[^@]+\.[^@]+", input_string):
        return input_string
    else:
        raise ValueError("Invalid email address")


@plumber(
    name="URL",
    color='rgb(173, 255, 153)',
    specificity=25,
)
def url_parser(input_string) -> str:
    """Accepts URLs"""
    from urllib.parse import urlparse
    result = urlparse(input_string)
    if result.scheme and result.netloc:
        return input_string
    else:
        raise ValueError("Invalid URL")
