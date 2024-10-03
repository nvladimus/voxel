from dataclasses import dataclass
from typing import List, Dict, Any

from ruamel.yaml import YAML

from voxel.acquisition.model.frame_stack import FrameStack
from voxel.utils.geometry.vec import Vec2D


def update_yaml_content(file_path: str, new_content: Dict[str, Any]) -> None:
    try:
        yaml = YAML(typ='safe')
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)

        # Read existing content
        try:
            with open(file_path) as file:
                data = yaml.load(file) or {}
        except FileNotFoundError:
            data = {}

        # Update content
        data.update(new_content)

        # Write updated content
        with open(file_path, "w") as file:
            for key, value in data.items():
                yaml.dump({key: value}, file)
                file.write("\n")
    except Exception as e:
        raise ValueError(f"Error updating YAML content: {e}")


@dataclass(frozen=True)
class VoxelAcquisitionPlan:
    frame_stacks: Dict[Vec2D, FrameStack]
    scan_path: List[Vec2D]

    def __post_init__(self):
        if not self.scan_path:
            raise ValueError("Scan path cannot be empty")
        if not all(idx in self.frame_stacks for idx in self.scan_path):
            raise ValueError("Scan path contains indices not present in frame stacks")

    def __len__(self):
        return len(self.scan_path)

    def __eq__(self, other: 'VoxelAcquisitionPlan') -> bool:
        if not isinstance(other, VoxelAcquisitionPlan):
            return NotImplemented

        return self.frame_stacks == other.frame_stacks and self.scan_path == other.scan_path

    def __ne__(self, other: 'VoxelAcquisitionPlan') -> bool:
        return not self.__eq__(other)

    def to_dict(self):
        return {
            "frame_stacks": {str(idx): frame_stack.to_dict() for idx, frame_stack in self.frame_stacks.items()},
            "scan_path": [str(idx) for idx in self.scan_path]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Dict[str, any]]]) -> 'VoxelAcquisitionPlan':
        frame_stacks = {}
        for idx_str, frame_stack_data in data["frame_stacks"].items():
            idx = Vec2D.from_str(idx_str)
            frame_stacks[idx] = FrameStack.from_dict(frame_stack_data)
        scan_path = [Vec2D.from_str(idx_str) for idx_str in data["scan_path"]]
        return cls(frame_stacks, scan_path)

    def save_to_yaml(self, file_path: str):
        update_yaml_content(file_path, {"plan": self.to_dict()})

    @classmethod
    def load_from_yaml(cls, file_path: str) -> 'VoxelAcquisitionPlan':
        with open(file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
            return cls.from_dict(data["plan"])
