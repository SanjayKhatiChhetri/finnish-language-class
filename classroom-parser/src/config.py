class Config:
    WEEK_START_DAY = 0  # Monday
    WEEK_KEY_FORMAT = "%Y-%m-%d"
    PRESERVE_HTML = False
    VALIDATE_URLS = False
    DATE_FORMATS = [
        "%d %b %Y",     # 21 Sept 2023
        "%b %d, %Y",    # Sept 21, 2023
        "%d.%m.%Y",     # 21.09.2023
        "%d/%m/%Y",     # 21/09/2023
        "%Y-%m-%d",     # 2023-09-21
        "%d %B %Y",     # 21 September 2023
        "%B %d, %Y",    # September 21, 2023
    ]