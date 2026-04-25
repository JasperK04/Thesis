# Copyright (c) 2024 Md. Ashraful Islam — Licensed under the MIT License. See LICENSE.
from promptings import (
    AnalogicalStrategy,
    CoTStrategy,
    DirectStrategy,
    MapCoder,
    PACEcoding,
    SelfPlanningStrategy,
)


class PromptingFactory:
    @staticmethod
    def get_prompting_class(prompting_name):
        if prompting_name == "PACEcoding":
            return PACEcoding
        elif prompting_name == "CoT":
            return CoTStrategy
        elif prompting_name == "MapCoder":
            return MapCoder
        elif prompting_name == "Direct":
            return DirectStrategy
        elif prompting_name == "Analogical":
            return AnalogicalStrategy
        elif prompting_name == "SelfPlanning":
            return SelfPlanningStrategy
        else:
            raise Exception(f"Unknown prompting name {prompting_name}")
