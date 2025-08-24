from problib.log import log
from pydantic_settings import BaseSettings


class FacilityLocationConfig(BaseSettings):
    # model_config = SettingsConfigDict(env_file=".env")

    fix_cost: float = 0.001  # in Euros
    mip_time_limit: int = 3600
    mip_gap_limit: float = 0.01
    pharmacy_capacity: int = 5  # capacity each pharmacy can hold
    practitioner_demand: int = 1  # uniform demand of each practitioner
    city: str = "Berlin, Germany"  # "(optional distrct), City, Country. I.e: (Shibuya), Tokyo, Japan"


config = FacilityLocationConfig()


log.info("Loaded configuration:", conf=config)
