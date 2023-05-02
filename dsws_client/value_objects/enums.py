import enum


class DSDateName(str, enum.Enum):
    """Specifies the date literals."""

    BASE_DATE = "BDATE"
    START_OF_WEEK = "SWDATE"
    START_OF_MONTH = "SMDATE"
    START_OF_QUARTER = "SQDATE"
    START_OF_YEAR = "SYDATE"
    LATEST_DATE = "LATESTDATE"
    INTRADAY = "TODAY"
    END_OF_YEAR = "YRE"
    END_OF_MONTH = "MTE"
    END_OF_QUARTER = "QTE"
    END_OF_WEEK = "WKE"
    START_OF_YEAR_2 = "YRS"
    START_OF_MONTH_2 = "MTS"
    START_OF_QUARTER_2 = "QTS"
    START_OF_WEEK_2 = "WKS"
    MIDDLE_OF_YEAR = "YRM"
    MIDDLE_OF_MONTH = "MTM"
    MIDDLE_OF_QUARTER = "QTM"
    MIDDLE_OF_WEEK = "WKM"


class DSDateFrequencyName(str, enum.Enum):
    """Specifies the frequency values."""

    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    YEARLY = "Y"
    SEVEN_DAYS = "7D"
    SEVEN_DAYS_PADDED = "7DPAD"
    SEVEN_DAYS_MIDDLE_EASTERN = "7DME"
    FIVSEVEN_DAYS_MIDDLE_EASTERN_PADDED = "7DMEPAD"


class DSDateKind(int, enum.Enum):
    """Specifies the date kind."""

    SNAPSHOT = 0
    TIMESERIES = 1


class DSInstrumentPropertyName(str, enum.Enum):
    """Specifies the instrument properties."""

    INSTRUMENT_LIST = "IsList"
    EXPRESSION = "IsExpression"
    SYMBOL_SET = "IsSymbolSet"
    RETURN_NAME = "ReturnName"


class DSSymbolResponseValueType(int, enum.Enum):
    """Specifies the value type of a symbol response."""

    ERROR = 0
    EMPTY = 1
    BOOL = 2
    INT = 3
    DATE_TIME = 4
    DOUBLE = 5
    STRING = 6
    BOOL_ARRAY = 7
    INT_ARRAY = 8
    DATE_TIME_ARRAY = 9
    DOUBLE_ARRAY = 10
    STRING_ARRAY = 11
    OBJECT_ARRAY = 12
