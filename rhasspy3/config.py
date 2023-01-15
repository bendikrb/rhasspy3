import argparse

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from dataclasses_json import DataClassJsonMixin
from yaml import safe_load


@dataclass
class ProgramConfig(DataClassJsonMixin):
    command: str
    wrapper: Optional[str] = None
    shell: bool = False
    template_args: Optional[Dict[str, Any]] = None


@dataclass
class FlowProgramConfig(DataClassJsonMixin):
    name: str
    template_args: Optional[Dict[str, Any]] = None


@dataclass
class FlowConfig(DataClassJsonMixin):
    mic: FlowProgramConfig
    wake: FlowProgramConfig
    vad: FlowProgramConfig
    asr: FlowProgramConfig
    intent: FlowProgramConfig
    handle: FlowProgramConfig
    tts: FlowProgramConfig
    snd: FlowProgramConfig


@dataclass
class Config(DataClassJsonMixin):
    programs: Dict[str, Dict[str, ProgramConfig]]
    """domain -> name -> program"""

    flows: Dict[str, FlowConfig] = field(default_factory=dict)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to YAML configuration file")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as config_file:
        config_dict = safe_load(config_file)

    config = Config.from_dict(config_dict)
    print(config)
