# Vulture whitelist for legitimate code that appears unused
# This file contains code that vulture flags as unused but is actually needed

# Pydantic field_validator classmethod parameters
# These 'cls' parameters are required by Pydantic's @field_validator decorator
# even though they're not used in the method body
cls  # Used in @field_validator @classmethod methods in src/config/models.py

# Qwen-Agent tool interface parameters
# These 'kwargs' parameters are required by qwen-agent's BaseTool interface
# even though they're not used in the method body
kwargs  # Used in qwen-agent tool call methods 