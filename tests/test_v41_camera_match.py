from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

import camera_match
from director_plan_importer import apply_director_plan
from director_state import write_json
from tests.test_v41_phase6 import sample_director_plan


def _runtime() -> dict:
    return {
        "schema_version": "4.1",
        "episode_id": "EP999",
        "current_scene_id": "Scene01",
        "current_shot_id": "",
        "director_session_mode": "PROMPT_ONLY",
        "scene_status": "PLANNING",
        "next_action": "PLAN_CURRENT_SCENE",
        "pending_director_plan": None,
        "pending_director_qa": None,
        "pending_camera_match": None,
        "last_event": "TEST_PLANNING",
        "updated_at": "2026-08-29T00:00:00+00:00",
    }


def _scene() -> dict:
    return {
        "schema_version": "4.1",
        "episode_id": "EP999",
        "scene_id": "Scene01",
        "scene_number": 1,
        "scene_title": "Camera Resume Test",
        "plan_status": "DRAFT",
        "status": "PLANNING",
        "shot_count": 0,
        "shots": [],
        "next_scene": "EPISODE_END",
        "updated_at": "2026-08-29T00:00:00+00:00",
    }


def _strip_camera_patch_fields(plan: dict) -> dict:
    normalized = deepcopy(plan)
    normalized.pop("revision", None)
    for shot in normalized["shots"]:
        shot.pop("selected_camera", None)
        shot.pop("camera_status", None)
        shot.pop("camera_reason", None)
    return normalized


class CameraMatchResumeTests(unittest.TestCase):
    def test_legacy_camera_gap_resumes_and_only_patches_camera_fields(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            root = Path(temp_name)
            episode_dir = root / "episodes" / "EP999"
            scene_dir = episode_dir / "director_state" / "Scene01"
            scene_dir.mkdir(parents=True)
            write_json(episode_dir / "director_state" / "Runtime_State.json", _runtime())
            write_json(scene_dir / "Scene_State.json", _scene())

            plan = sample_director_plan()
            plan["shots"][0]["selected_camera"] = None
            plan["shots"][0]["camera_status"] = "NEED_NEW_CAMERA"
            plan["shots"][0]["camera_reason"] = "需要新的玄关反应机位。"
            input_path = root / "camera_gap_plan.json"
            write_json(input_path, plan)
            result, _ = apply_director_plan("EP999", episode_dir, input_path)
            self.assertEqual(result, "NEED_NEW_CAMERA")
            stored_plan = scene_dir / "Scene_Director_Plan_RESULT.json"
            self.assertTrue(stored_plan.is_file())

            # Simulate the V4.1.0 behavior already seen in an existing project.
            runtime_path = episode_dir / "director_state" / "Runtime_State.json"
            legacy = json.loads(runtime_path.read_text(encoding="utf-8"))
            legacy["scene_status"] = "PLANNING"
            legacy["next_action"] = "PLAN_CURRENT_SCENE"
            legacy["last_event"] = "CAMERA_LIBRARY_REBUILT_REPLAN_REQUIRED"
            write_json(runtime_path, legacy)

            camera_record = {
                "id": "cameras.entrance-reaction-camera02",
                "name": "Entrance Reaction Camera02",
                "category": "cameras",
                "path": "assets/cameras/Entrance Reaction Camera02.png",
                "aliases": ["Entrance Reaction Camera02"],
                "tags": ["cameras", "entrance"],
                "sha256": "a" * 64,
                "size_bytes": 1234,
            }
            write_json(root / "assets" / "AssetRegistry.json", {
                "schema_version": "4.0",
                "asset_count": 1,
                "assets": [camera_record],
            })
            write_json(root / "build" / "EP999" / "EP999_Asset_Selection.json", {
                "schema_version": "4.0",
                "episode": "EP999",
                "stage": "production",
                "selected": [{**camera_record, "package_path": "assets/cameras/test.png"}],
                "missing": [],
                "ambiguous": [],
            })

            with patch.object(camera_match, "PROJECT_ROOT", root), patch.object(
                camera_match, "BUILD_ROOT", root / "build"
            ):
                self.assertTrue(
                    camera_match.resume_camera_gap_after_build("EP999", episode_dir)
                )
                resumed = json.loads(runtime_path.read_text(encoding="utf-8"))
                self.assertEqual(resumed["next_action"], "CAMERA_MATCH_REQUIRED")
                self.assertTrue((scene_dir / "CAMERA_MATCH_REQUEST.md").is_file())

                invalid_path = root / "invalid_camera_match.json"
                write_json(invalid_path, {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "scene_id": "Scene01",
                    "source_plan_revision": 1,
                    "resolutions": [{
                        "shot_id": "Shot01-01",
                        "selected_camera": "cameras.not-selected",
                        "camera_status": "MATCH",
                        "camera_reason": "错误候选。",
                    }],
                })
                invalid_result, invalid_issues = camera_match.apply_camera_match(
                    "EP999", episode_dir, invalid_path
                )
                self.assertEqual(invalid_result, "INVALID_CAMERA_MATCH_RESULT")
                self.assertTrue(any("不是当前 Episode" in item for item in invalid_issues))
                self.assertEqual(
                    json.loads(stored_plan.read_text(encoding="utf-8"))["revision"],
                    1,
                )

                valid_path = root / "Camera_Match_Result.json"
                write_json(valid_path, {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "scene_id": "Scene01",
                    "source_plan_revision": 1,
                    "resolutions": [{
                        "shot_id": "Shot01-01",
                        "selected_camera": camera_record["id"],
                        "camera_status": "MATCH",
                        "camera_reason": "新登记机位满足中近景、玄关轴线与静态反应读取。",
                    }],
                })
                applied, issues = camera_match.apply_camera_match(
                    "EP999", episode_dir, valid_path
                )

            self.assertEqual(applied, "PASS")
            self.assertEqual(issues, [])
            patched_plan = json.loads(stored_plan.read_text(encoding="utf-8"))
            self.assertEqual(patched_plan["revision"], 2)
            self.assertEqual(
                patched_plan["shots"][0]["selected_camera"],
                camera_record["id"],
            )
            self.assertEqual(
                _strip_camera_patch_fields(patched_plan),
                _strip_camera_patch_fields(plan),
            )
            final_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(final_runtime["next_action"], "DIRECTOR_QA_REQUIRED")
            self.assertEqual(
                final_runtime["last_event"],
                "CAMERA_MATCH_APPLIED_WAIT_DIRECTOR_QA",
            )
            self.assertTrue(
                (scene_dir / "Scene_Director_Plan_PRE_CAMERA_MATCH_R001.json").is_file()
            )


if __name__ == "__main__":
    unittest.main()
