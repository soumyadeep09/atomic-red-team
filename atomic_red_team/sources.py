import glob
import os.path
from os.path import abspath, dirname
from typing import List

from attackcti import attack_client

from .models.atomic import Atomic, Platform
from .utils import flatten, get_technique_from_file


class AttackAPI:
    lift = attack_client()

    def __init__(self):
        self.techniques = self.lift.get_techniques()

    def get_mitre_technique(self, technique_id: str):
        return list(
            filter(
                lambda x: x["external_references"][0]["external_id"] == technique_id,
                self.techniques,
            )
        )[0]

    def get_technique_description(self, technique_id: str):
        return self.get_mitre_technique(technique_id)["description"]

    def get_tactics_for_technique(self, technique: str) -> List[str]:
        return sorted(
            [
                x["phase_name"]
                for x in self.get_mitre_technique(technique)["kill_chain_phases"]
            ]
        )

    def get_tactics(self):
        return [tactic["x_mitre_shortname"] for tactic in self.lift.get_tactics()]


class AtomicRedTeam:
    def __init__(self, test_path: str = None):
        self.atomics_path = test_path or os.path.join(
            dirname(dirname(abspath(__file__))), "atomics"
        )
        self.atomics_files = sorted(glob.glob(f"{self.atomics_path}/T*/*.yaml"))
        self.atomic_techniques = [
            get_technique_from_file(file) for file in self.atomics_files
        ]
        atomics = [technique.atomic_tests for technique in self.atomic_techniques]
        self.atomics = flatten(atomics)

    def get_atomics_by_platform(self, platform: Platform) -> List[Atomic]:
        return sorted(
            list(filter(lambda x: platform in x.supported_platforms, self.atomics)),
            key=lambda x: x.test_number,
        )
