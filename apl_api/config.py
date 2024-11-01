from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "A Pattern Language API"
    version: str = "1.0"
    description: str = """A RESTful API implementation of Christopher Alexander's *A Pattern Language*: use it to search and retrieve pattern data by name, id, confidence, etc. and explore links and backlinks.
    """
    database: str = "apl.db"
    update_interval: int = 1 # In days, how often to check for Markdown file updates
    swagger_ui: dict = {
            "syntaxHilight.activated" : True,
            "syntaxHighlight.theme": "obsidian",
            "tryItOutEnabled" : True,
    }
    contact: dict = {
        "name" : "See original website for more info",
        "url" : "https://patternlanguage.cc",
    }
    license_info: dict = {
        "name" : "MIT License",
        "identifier" : "MIT License"
    }


settings = Settings()