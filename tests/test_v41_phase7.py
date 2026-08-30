from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
TESTS_ROOT = PROJECT_ROOT / "tests"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(TESTS_ROOT))

from build_shot_package import (
    AssetRequirementError,
    BUILDER_MODE,
    build_current_shot_package,
)
from director_state import read_json, write_json
from test_v41_phase6 import sample_execution_state


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _runtime(next_action: str = "GENERATE_CURRENT_SHOT_PACKAGE") -> dict:
    return {
        "schema_version": "4.1",
        "episode_id": "EP999",
        "current_scene_id": "Scene01",
        "current_shot_id": "Shot01-01",
        "director_session_mode": "PROMPT_ONLY",
        "scene_status": "PRODUCTION",
        "next_action": next_action,
        "pending_director_plan": None,
        "pending_director_qa": None,
        "last_event": "PHASE7_TEST_READY",
        "updated_at": "2026-08-29T00:00:00+00:00",
    }


def _scene_state(shot_ids: list[str]) -> dict:
    return {
        "schema_version": "4.1",
        "episode_id": "EP999",
        "scene_id": "Scene01",
        "scene_number": 1,
        "scene_title": "Phase7 Test",
        "plan_status": "LOCKED",
        "status": "PRODUCTION",
        "shot_count": len(shot_ids),
        "shots": shot_ids,
        "next_scene": "EPISODE_END",
        "updated_at": "2026-08-29T00:00:00+00:00",
    }


def _write_registry(project_root: Path, records: list[dict]) -> None:
    write_json(
        project_root / "assets" / "AssetRegistry.json",
        {
            "schema_version": "1.0",
            "generated_at": "2026-08-29T00:00:00+00:00",
            "project": "Phase7 Test",
            "asset_count": len(records),
            "assets": records,
        },
    )


def _create_asset(
    project_root: Path,
    asset_id: str,
    relative_path: str,
    content: bytes,
) -> dict:
    path = project_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return {
        "id": asset_id,
        "name": asset_id,
        "category": relative_path.split("/")[1],
        "path": relative_path,
        "aliases": [],
        "tags": [],
        "sha256": _sha256_bytes(content),
        "size_bytes": len(content),
    }


def _prepare_episode(
    project_root: Path,
    shot: dict,
    *,
    previous_shot: dict | None = None,
) -> tuple[Path, Path, Path]:
    episode_dir = project_root / "episodes" / "EP999"
    state_root = episode_dir / "director_state"
    scene_dir = state_root / "Scene01"
    shots_dir = scene_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    shot_ids = []
    if previous_shot is not None:
        shot_ids.append(previous_shot["shot_id"])
        write_json(
            shots_dir / f"{previous_shot['shot_id']}_State.json",
            previous_shot,
        )
    shot_ids.append(shot["shot_id"])
    write_json(shots_dir / f"{shot['shot_id']}_State.json", shot)
    write_json(scene_dir / "Scene_State.json", _scene_state(shot_ids))

    runtime = _runtime()
    runtime["current_shot_id"] = shot["shot_id"]
    write_json(state_root / "Runtime_State.json", runtime)
    return episode_dir, scene_dir, shots_dir / f"{shot['shot_id']}_State.json"


def _previous_and_current(policy: str) -> tuple[dict, dict]:
    previous = sample_execution_state()
    previous["shot_id"] = "Shot01-01"
    previous["order"] = 1
    previous["status"] = "COMPLETED"
    previous["scene_end"] = False
    previous["next_shot"] = "Shot01-02"

    current = sample_execution_state()
    current["shot_id"] = "Shot01-02"
    current["order"] = 2
    current["continuity"]["previous_frame_policy"] = policy
    current["continuity"]["mode"] = (
        "SAME_CAMERA_CONTINUATION"
        if policy == "HIGH_PRIORITY_VISUAL_CONTINUITY"
        else "CAMERA_CUT_CONTINUITY"
    )
    return previous, current


class Phase7BuilderTests(unittest.TestCase):
    def test_builder_copies_only_locked_assets_and_emits_contract(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            required = _create_asset(
                project_root,
                "cameras.required",
                "assets/cameras/Camera.png",
                b"required camera",
            )
            unused = _create_asset(
                project_root,
                "props.unused",
                "assets/props/Unused.png",
                b"unused prop",
            )
            _write_registry(project_root, [required, unused])

            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["cameras.required"]
            episode_dir, _, shot_path = _prepare_episode(project_root, shot)

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(package_dir.name, "v001")
            for name in [
                "prompt.md",
                "IMAGE_PROMPT.md",
                "VIDEO_PROMPT.md",
                "CHATGPT_HANDOFF.md",
                "PROMPT_COMPILATION_MANIFEST.json",
                "required_assets.json",
                "UPLOAD_MANIFEST.json",
                "PACKAGE_MANIFEST.json",
            ]:
                self.assertTrue((package_dir / name).is_file(), name)

            upload_files = [path.name for path in (package_dir / "upload").iterdir()]
            self.assertEqual(upload_files, ["cameras__required.png"])
            self.assertNotIn("Unused.png", upload_files)

            package_manifest = read_json(package_dir / "PACKAGE_MANIFEST.json")
            self.assertEqual(package_manifest["builder_mode"], BUILDER_MODE)
            self.assertFalse(package_manifest["creative_decision_allowed"])
            self.assertFalse(package_manifest["reads_director_decision"])
            self.assertEqual(package_manifest["state_authority"], "Shot_State.json")

            required_assets = read_json(package_dir / "required_assets.json")
            self.assertEqual(
                [item["asset_id"] for item in required_assets["assets"]],
                ["cameras.required"],
            )
            self.assertFalse(required_assets["blocking"])
            state = read_json(shot_path)
            self.assertEqual(state["status"], "PROMPTED")
            runtime = read_json(
                episode_dir / "director_state" / "Runtime_State.json"
            )
            self.assertEqual(runtime["next_action"], "WAIT_FOR_IMAGE_APPROVAL")

    def test_registered_but_missing_source_blocks_without_build_fallback(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [{
                "id": "props.missing",
                "name": "Missing",
                "category": "props",
                "path": "assets/props/Missing.png",
                "aliases": [],
                "tags": [],
                "sha256": "0" * 64,
                "size_bytes": 1,
            }])
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["props.missing"]
            episode_dir, scene_dir, _ = _prepare_episode(project_root, shot)

            with self.assertRaises(AssetRequirementError) as raised:
                build_current_shot_package(
                    "EP999",
                    episode_dir,
                    project_root=project_root,
                )
            self.assertEqual(raised.exception.issues[0]["reason"], "SOURCE_FILE_MISSING")
            runtime = read_json(
                episode_dir / "director_state" / "Runtime_State.json"
            )
            self.assertEqual(runtime["next_action"], "NEED_ASSET")
            requirement = (scene_dir / "ASSET_REQUIREMENT.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("SOURCE_FILE_MISSING", requirement)
            self.assertFalse((episode_dir / "production").exists())

    def test_registry_hash_mismatch_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            record = _create_asset(
                project_root,
                "props.changed",
                "assets/props/Changed.png",
                b"current bytes",
            )
            record["sha256"] = "f" * 64
            _write_registry(project_root, [record])
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["props.changed"]
            episode_dir, _, _ = _prepare_episode(project_root, shot)

            with self.assertRaises(AssetRequirementError) as raised:
                build_current_shot_package(
                    "EP999",
                    episode_dir,
                    project_root=project_root,
                )
            self.assertEqual(raised.exception.issues[0]["reason"], "SHA256_MISMATCH")

    def test_state_reference_only_does_not_copy_previous_final(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [])
            previous, current = _previous_and_current("STATE_REFERENCE_ONLY")
            episode_dir, _, _ = _prepare_episode(
                project_root,
                current,
                previous_shot=previous,
            )
            final_path = (
                episode_dir
                / "production"
                / "Scene01"
                / "Shot01-01"
                / "Shot01-01_Final.png"
            )
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_bytes(b"previous final")

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(list((package_dir / "upload").iterdir()), [])
            required = read_json(package_dir / "required_assets.json")
            self.assertFalse(required["previous_frame"]["copied_to_upload"])
            self.assertEqual(
                required["previous_frame"]["policy"],
                "STATE_REFERENCE_ONLY",
            )

    def test_high_priority_continuity_copies_previous_final(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [])
            previous, current = _previous_and_current(
                "HIGH_PRIORITY_VISUAL_CONTINUITY"
            )
            episode_dir, _, _ = _prepare_episode(
                project_root,
                current,
                previous_shot=previous,
            )
            final_path = (
                episode_dir
                / "production"
                / "Scene01"
                / "Shot01-01"
                / "Shot01-01_Final.png"
            )
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_bytes(b"previous final")

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            copied = package_dir / "upload" / "Shot01-01_Final.png"
            self.assertEqual(copied.read_bytes(), b"previous final")
            upload_manifest = read_json(package_dir / "UPLOAD_MANIFEST.json")
            self.assertEqual(upload_manifest["upload_items"][0]["type"], "PREVIOUS_FINAL")
            required = read_json(package_dir / "required_assets.json")
            self.assertTrue(required["previous_frame"]["copied_to_upload"])

    def test_identical_input_reuses_package_and_locked_change_versions(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [])
            shot = sample_execution_state()
            episode_dir, _, shot_path = _prepare_episode(project_root, shot)
            runtime_path = episode_dir / "director_state" / "Runtime_State.json"

            first = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            first_prompt = (first / "IMAGE_PROMPT.md").read_text(encoding="utf-8")

            runtime = read_json(runtime_path)
            runtime["next_action"] = "GENERATE_CURRENT_SHOT_PACKAGE"
            write_json(runtime_path, runtime)
            reused = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(reused, first)
            self.assertEqual(
                read_json(runtime_path)["last_event"],
                "CURRENT_SHOT_PACKAGE_REUSED",
            )
            self.assertEqual(
                sorted(path.name for path in first.parent.iterdir()),
                ["v001"],
            )

            (first / "IMAGE_PROMPT.md").write_text(
                "corrupted",
                encoding="utf-8",
            )
            runtime = read_json(runtime_path)
            runtime["next_action"] = "GENERATE_CURRENT_SHOT_PACKAGE"
            write_json(runtime_path, runtime)
            recovered = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(recovered.name, "v002")
            self.assertEqual(
                (recovered / "IMAGE_PROMPT.md").read_text(encoding="utf-8"),
                first_prompt,
            )

            runtime = read_json(runtime_path)
            runtime["next_action"] = "GENERATE_CURRENT_SHOT_PACKAGE"
            write_json(runtime_path, runtime)
            changed = read_json(shot_path)
            changed["status"] = "READY"
            changed["composition_intent"] = "锁定后的新构图版本。"
            write_json(shot_path, changed)
            second = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(second.name, "v003")
            self.assertEqual(
                (recovered / "IMAGE_PROMPT.md").read_text(encoding="utf-8"),
                first_prompt,
            )
            self.assertNotEqual(
                (second / "IMAGE_PROMPT.md").read_text(encoding="utf-8"),
                first_prompt,
            )

    def test_same_basename_assets_receive_collision_safe_upload_names(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            camera = _create_asset(
                project_root,
                "cameras.same",
                "assets/cameras/Master.png",
                b"camera",
            )
            prop = _create_asset(
                project_root,
                "props.same",
                "assets/props/Master.png",
                b"prop",
            )
            _write_registry(project_root, [camera, prop])
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["cameras.same", "props.same"]
            episode_dir, _, _ = _prepare_episode(project_root, shot)

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            filenames = sorted(path.name for path in (package_dir / "upload").iterdir())
            self.assertEqual(filenames, ["cameras__same.png", "props__same.png"])


if __name__ == "__main__":
    unittest.main()
