from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
TESTS_ROOT = PROJECT_ROOT / "tests"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(TESTS_ROOT))

import asset_index
from build_shot_package import build_current_shot_package, refresh_stale_current_package_state
from director_state import read_json, validate_state_payload
from image_fixture import png_bytes
from image_metadata import image_metadata
from production_format import DEFAULT_OUTPUT_FORMAT, ensure_shot_output_format
from production_runtime import approve_image
from prompt_contract_qa import validate_compiled_prompt_contract
from state_prompt_compiler import compile_prompt_pair
from test_v41_phase6 import previous_frame, sample_execution_state
from test_v41_phase7 import _create_asset, _prepare_episode, _write_registry


class V41AspectFormatHotfixTests(unittest.TestCase):
    def test_first_shot_prompt_is_locked_to_native_vertical_9x16(self) -> None:
        shot = sample_execution_state()
        prompts = compile_prompt_pair(shot, previous_frame())
        for name in ("image_prompt", "video_prompt"):
            prompt = prompts[name]
            self.assertIn("Aspect Ratio: 9:16", prompt)
            self.assertIn("Orientation: PORTRAIT", prompt)
            self.assertIn("Target Canvas: 1080x1920", prompt)
            self.assertIn("Do not output landscape", prompt)
            self.assertEqual(prompt.count("Aspect Ratio: 9:16"), 1)

    def test_prompt_qa_rejects_missing_output_format_lock(self) -> None:
        shot = sample_execution_state()
        prev = previous_frame()
        prompts = compile_prompt_pair(shot, prev)
        broken = prompts["image_prompt"].replace("Aspect Ratio: 9:16", "")
        issues = validate_compiled_prompt_contract(
            shot,
            prev,
            broken,
            prompts["video_prompt"],
        )
        self.assertTrue(any("Aspect Ratio: 9:16" in item for item in issues))

    def test_old_shot_state_is_migrated_without_redirection(self) -> None:
        shot = sample_execution_state()
        del shot["output_format"]
        self.assertTrue(ensure_shot_output_format(shot))
        self.assertEqual(shot["output_format"], DEFAULT_OUTPUT_FORMAT)
        validate_state_payload(shot, "Shot_State.schema.json")

    def test_landscape_camera_master_is_nonblocking_and_recommends_variant(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            camera = _create_asset(
                project_root,
                "cameras.landscape",
                "assets/cameras/Landscape.png",
                png_bytes(160, 90),
            )
            _write_registry(project_root, [camera])
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["cameras.landscape"]
            episode_dir, scene_dir, _ = _prepare_episode(project_root, shot)

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertFalse((scene_dir / "ASSET_REQUIREMENT.md").exists())
            manifest = read_json(package_dir / "PACKAGE_MANIFEST.json")
            self.assertFalse(manifest["reference_warnings"][0]["blocking"])
            self.assertEqual(
                manifest["reference_warnings"][0]["reason"],
                "PORTRAIT_VARIANT_RECOMMENDED",
            )
            self.assertIn("160x90", manifest["reference_warnings"][0]["details"])

    def test_portrait_variant_is_preferred_without_changing_camera_asset_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            base = _create_asset(
                project_root,
                "cameras.same-camera",
                "assets/cameras/Camera.png",
                png_bytes(160, 90),
            )
            variant = _create_asset(
                project_root,
                "unused.variant-record",
                "assets/cameras/Camera_Portrait_9x16.png",
                png_bytes(90, 160),
            )
            base["variants"] = {
                "portrait_9x16": {
                    "path": variant["path"],
                    "sha256": variant["sha256"],
                    "size_bytes": variant["size_bytes"],
                    "width_pixels": 90,
                    "height_pixels": 160,
                    "orientation": "PORTRAIT",
                }
            }
            _write_registry(project_root, [base])
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["cameras.same-camera"]
            episode_dir, _, _ = _prepare_episode(project_root, shot)

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            required = read_json(package_dir / "required_assets.json")
            asset = required["assets"][0]
            self.assertEqual(asset["asset_id"], "cameras.same-camera")
            self.assertEqual(asset["source_variant"], "portrait_9x16")
            self.assertEqual(asset["orientation"], "PORTRAIT")
            self.assertEqual(required["reference_warnings"], [])
            uploaded = package_dir / asset["upload_path"]
            self.assertEqual(uploaded.read_bytes(), png_bytes(90, 160))

    def test_package_records_output_format_and_portrait_reference_metadata(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            camera = _create_asset(
                project_root,
                "cameras.portrait",
                "assets/cameras/Portrait.png",
                png_bytes(),
            )
            _write_registry(project_root, [camera])
            shot = sample_execution_state()
            del shot["output_format"]
            shot["required_assets"]["asset_ids"] = ["cameras.portrait"]
            episode_dir, _, shot_path = _prepare_episode(project_root, shot)

            package_dir = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            state = read_json(shot_path)
            manifest = read_json(package_dir / "PACKAGE_MANIFEST.json")
            required = read_json(package_dir / "required_assets.json")
            self.assertEqual(state["output_format"], DEFAULT_OUTPUT_FORMAT)
            self.assertEqual(manifest["output_format"], DEFAULT_OUTPUT_FORMAT)
            self.assertEqual(required["output_format"], DEFAULT_OUTPUT_FORMAT)
            self.assertEqual(required["assets"][0]["orientation"], "PORTRAIT")

    def test_image_approval_rejects_landscape_final(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [])
            shot = sample_execution_state()
            episode_dir, _, _ = _prepare_episode(project_root, shot)
            build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            landscape = project_root / "generated-landscape.png"
            landscape.write_bytes(png_bytes(160, 90))
            with self.assertRaisesRegex(ValueError, "必须是竖屏图片"):
                approve_image("EP999", episode_dir, landscape)

    def test_unapproved_pre_hotfix_package_is_requeued_without_deletion(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            project_root = Path(temp_name)
            _write_registry(project_root, [])
            shot = sample_execution_state()
            episode_dir, _, shot_path = _prepare_episode(project_root, shot)
            first = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            manifest_path = first / "PACKAGE_MANIFEST.json"
            manifest = read_json(manifest_path)
            del manifest["output_format"]
            from director_state import write_json
            write_json(manifest_path, manifest)
            old_state = read_json(shot_path)
            del old_state["output_format"]
            write_json(shot_path, old_state)

            self.assertTrue(
                refresh_stale_current_package_state(
                    "EP999",
                    episode_dir,
                    project_root=project_root,
                )
            )
            self.assertTrue(first.is_dir())
            runtime = read_json(
                episode_dir / "director_state" / "Runtime_State.json"
            )
            self.assertEqual(
                runtime["next_action"],
                "GENERATE_CURRENT_SHOT_PACKAGE",
            )
            second = build_current_shot_package(
                "EP999",
                episode_dir,
                project_root=project_root,
            )
            self.assertEqual(second.name, "v002")
            self.assertTrue(first.is_dir())

    def test_png_metadata_reports_orientation_without_third_party_package(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            path = Path(temp_name) / "portrait.png"
            path.write_bytes(png_bytes(90, 160))
            self.assertEqual(
                image_metadata(path),
                {
                    "width_pixels": 90,
                    "height_pixels": 160,
                    "orientation": "PORTRAIT",
                },
            )

    def test_asset_scan_embeds_declared_variant_without_second_asset_id(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            assets_root = Path(temp_name) / "assets"
            camera_dir = assets_root / "cameras"
            camera_dir.mkdir(parents=True)
            base = camera_dir / "Camera.png"
            variant = camera_dir / "Camera_Portrait_9x16.png"
            base.write_bytes(png_bytes(160, 90))
            variant.write_bytes(png_bytes(90, 160))
            base.with_suffix(".asset.json").write_text(
                json.dumps({
                    "id": "cameras.test",
                    "variants": {
                        "portrait_9x16": "Camera_Portrait_9x16.png"
                    },
                }),
                encoding="utf-8",
            )
            original_root = asset_index.ASSETS_ROOT
            try:
                asset_index.ASSETS_ROOT = assets_root
                records = asset_index.scan_assets()
            finally:
                asset_index.ASSETS_ROOT = original_root
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].id, "cameras.test")
            self.assertEqual(
                records[0].variants["portrait_9x16"]["orientation"],
                "PORTRAIT",
            )


if __name__ == "__main__":
    unittest.main()
