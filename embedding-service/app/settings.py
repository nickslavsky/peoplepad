from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    max_input_length: int
    peoplepad_client_key: str
    embedding_model_name: str
    embedding_model_path: str

    model_config = SettingsConfigDict(env_file='.env', env_ignore_empty=True)