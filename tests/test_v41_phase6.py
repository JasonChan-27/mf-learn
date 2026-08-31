from __future__ import annotations

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

from director_plan_compiler import compile_director_decision, compile_shot_state
from director_plan_importer import apply_director_plan
from director_plan_validator import validate_director_plan
from director_state import validate_state_payload, write_json
from production_runtime import (
    AssetRequirementError,
    approve_image,
    approve_video,
    build_current_shot_package,
)
from prompt_contract_qa import validate_compiled_prompt_contract
from state_prompt_compiler import (
    build_compilation_manifest,
    compile_prompt_pair,
    source_state_sha256,
)
from image_fixture import png_bytes


def sample_plan_shot() -> tuple[dict, dict]:
    plan = {
        "schema_version": "4.1",
        "episode_id": "EP999",
        "scene_id": "Scene01",
        "revision": 1,
        "plan_status": "LOCKED",
        "scene_assets": {
            "environment_asset": "environments.test",
            "character_assets": {
                "DaPiaoLiang": "characters.dapiaoliang-master",
                "XiaoNan": "characters.xiaonan-master",
            },
            "outfit_assets": {},
            "prop_assets": [],
        },
        "next_scene": "EPISODE_END",
    }
    shot = {
        "shot_id": "Shot01-01",
        "order": 1,
        "primary_function": "CHARACTER_REVEAL",
        "secondary_effect": "REACTION",
        "narrative_purpose": "让观众看清角色反应。",
        "audience_feeling": "轻微共情。",
        "information_gain": "角色最先发现变化。",
        "why_this_shot": "当前必须读取单猫反应。",
        "why_not_previous_shot": "这是 Scene 首镜，需要独立建立注意力。",
        "primary_focus": "DaPiaoLiang",
        "secondary_focus": None,
        "coverage": "MEDIUM_CLOSE",
        "coverage_reason": "中近景足以读取表情并保留少量空间身份。",
        "composition_intent": "主体占画面主要面积，门与鞋柜柔焦保留。",
        "information_density": "LOW",
        "visible_characters": ["DaPiaoLiang"],
        "partial_characters": [],
        "off_screen_characters": ["XiaoNan"],
        "camera_requirement": {
            "purpose": "Cat Reaction",
            "scale": "MEDIUM_CLOSE",
            "subject_zone": "entrance cat zone",
            "axis_requirement": "Preserve entrance axis",
            "lens_intent": "Compress background",
        },
        "selected_camera": "cameras.test-camera",
        "camera_status": "MATCH",
        "camera_reason": "固定机位符合反应镜头需求。",
        "camera_motion": "LOCKED_OFF",
        "camera_motion_reason": "静止更利于读取反应。",
        "axis_status": "PRESERVED",
        "continuity_mode": "CAMERA_CUT_CONTINUITY",
        "previous_frame_policy": "NONE",
        "start_state": {"description": "猫安静坐在玄关地面。"},
        "frozen_moment": {
            "description": "猫抬头前的稳定瞬间。",
            "physical_boundaries": ["四只脚接触地面", "头部保持水平"],
            "forbidden_advanced_states": ["头部已经抬起", "身体已经起跳"],
        },
        "shot_delta": {
            "primary_action": "猫缓慢抬头看向门口。",
            "secondary_actions": ["耳朵轻微转向声音来源"],
            "performance_notes": "动作自然克制。",
            "timing": ["0.0-1.0s 保持", "1.0-2.5s 抬头"],
        },
        "end_state": {"description": "猫抬头看向门口并保持。"},
        "estimated_duration": 2.5,
        "scene_end": True,
        "next_shot": "EPISODE_END",
    }
    return plan, shot


def sample_execution_state() -> dict:
    plan, plan_shot = sample_plan_shot()
    state = compile_shot_state(plan, plan_shot)
    state["required_assets"]["asset_ids"] = []
    state["status"] = "READY"
    return state


def sample_director_plan() -> dict:
    plan, shot = sample_plan_shot()
    plan["scene_director_decision"] = {
        "scene_goal": "读取玄关内的角色反应。",
        "narrative_change": "角色由平静转为注意门口。",
        "primary_character": "DaPiaoLiang",
        "secondary_characters": ["XiaoNan"],
        "audience_start_state": "观察日常状态。",
        "audience_end_state": "意识到门外有变化。",
        "emotion_curve": ["平静", "警觉"],
        "information_curve": ["玄关日常", "门外出现声响"],
        "rhythm_strategy": "单镜克制推进。",
        "primary_style": "观察式喜剧",
        "secondary_style": None,
        "scene_visual_strategy": "保持空间稳定，突出猫的反应。",
        "scene_camera_strategy": "固定中近景。",
        "scene_end_intent": "以视线指向门口结束。",
    }
    plan["scene_end_state"] = {"description": "猫抬头看向门口。"}
    plan["shots"] = [shot]
    return plan


def previous_frame() -> dict:
    return {
        "policy": "NONE",
        "previous_shot_id": None,
        "include_previous_final_in_upload": False,
        "previous_final_path": None,
        "instruction": "不上传上一 Shot Final；当前镜头独立建立。",
    }


class Phase6PureCompilerTests(unittest.TestCase):
    def test_visible_character_requires_explicit_asset_mapping(self) -> None:
        plan = sample_director_plan()
        del plan["scene_assets"]["character_assets"]["DaPiaoLiang"]
        issues = validate_director_plan(plan)
        self.assertTrue(any("DaPiaoLiang" in item for item in issues))

    def test_required_assets_are_compiled_from_explicit_scene_mapping(self) -> None:
        plan = sample_director_plan()
        plan["scene_assets"]["outfit_assets"] = {
            "DaPiaoLiang": "outfits.dapiaoliang-test"
        }
        state = compile_shot_state(plan, plan["shots"][0])
        self.assertEqual(
            state["required_assets"]["asset_ids"],
            [
                "environments.test",
                "characters.dapiaoliang-master",
                "outfits.dapiaoliang-test",
                "cameras.test-camera",
            ],
        )

    def test_director_fields_are_copied_not_inferred(self) -> None:
        plan, shot = sample_plan_shot()
        decision = compile_director_decision(plan, shot)
        state = compile_shot_state(plan, shot)
        self.assertEqual(decision["coverage_reason"], shot["coverage_reason"])
        self.assertEqual(state["camera_state"]["axis_status"], shot["axis_status"])
        validate_state_payload(decision, "Director_Decision.schema.json")
        validate_state_payload(state, "Shot_State.schema.json")

    def test_image_and_video_contract_are_separated(self) -> None:
        shot = sample_execution_state()
        prev = previous_frame()
        prompts = compile_prompt_pair(shot, prev)
        issues = validate_compiled_prompt_contract(
            shot,
            prev,
            prompts["image_prompt"],
            prompts["video_prompt"],
        )
        self.assertEqual(issues, [])
        self.assertNotIn(shot["shot_delta"]["primary_action"], prompts["image_prompt"])
        self.assertIn(shot["shot_delta"]["primary_action"], prompts["video_prompt"])

    def test_contract_qa_rejects_video_state_leak(self) -> None:
        shot = sample_execution_state()
        prev = previous_frame()
        prompts = compile_prompt_pair(shot, prev)
        leaked = prompts["image_prompt"] + shot["shot_delta"]["primary_action"]
        issues = validate_compiled_prompt_contract(
            shot,
            prev,
            leaked,
            prompts["video_prompt"],
        )
        self.assertTrue(any("VIDEO-only" in item for item in issues))

    def test_source_hash_ignores_runtime_bookkeeping(self) -> None:
        shot = sample_execution_state()
        prev = previous_frame()
        before = source_state_sha256(shot, prev)
        mutated = deepcopy(shot)
        mutated["status"] = "PROMPTED"
        mutated["continuity"]["previous_frame_filename"] = "previous.png"
        mutated["required_assets"]["package_filenames"] = ["camera.png"]
        self.assertEqual(before, source_state_sha256(mutated, prev))

        prompts = compile_prompt_pair(shot, prev)
        manifest = build_compilation_manifest(shot, prev, prompts)
        self.assertEqual(manifest["compiler_mode"], "PURE_STATE_TRANSLATION")
        self.assertFalse(manifest["creative_decision_allowed"])
        for key in [
            "source_state_sha256",
            "image_prompt_sha256",
            "video_prompt_sha256",
            "handoff_sha256",
        ]:
            self.assertEqual(len(manifest[key]), 64)


class Phase5To6RuntimeIntegrationTests(unittest.TestCase):
    def test_camera_gap_blocks_without_python_fallback(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            episode_dir = Path(temp_name) / "episodes" / "EP999"
            scene_dir = episode_dir / "director_state" / "Scene01"
            scene_dir.mkdir(parents=True)
            write_json(
                episode_dir / "director_state" / "Runtime_State.json",
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "current_scene_id": "Scene01",
                    "current_shot_id": "",
                    "director_session_mode": "PROMPT_ONLY",
                    "scene_status": "PLANNING",
                    "next_action": "PLAN_CURRENT_SCENE",
                    "pending_director_plan": None,
                    "pending_director_qa": None,
                    "last_event": "TEST_PLANNING",
                    "updated_at": "2026-08-24T00:00:00+00:00",
                },
            )
            write_json(
                scene_dir / "Scene_State.json",
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "scene_id": "Scene01",
                    "scene_number": 1,
                    "scene_title": "Test",
                    "plan_status": "DRAFT",
                    "status": "PLANNING",
                    "shot_count": 0,
                    "shots": [],
                    "next_scene": "EPISODE_END",
                    "updated_at": "2026-08-24T00:00:00+00:00",
                },
            )
            plan = sample_director_plan()
            plan["shots"][0]["camera_status"] = "NEED_NEW_CAMERA"
            plan["shots"][0]["selected_camera"] = None
            plan_path = Path(temp_name) / "camera_gap.json"
            write_json(plan_path, plan)

            result, issues = apply_director_plan("EP999", episode_dir, plan_path)
            self.assertEqual(result, "NEED_NEW_CAMERA")
            self.assertTrue(any("NEED_NEW_CAMERA" in item for item in issues))
            runtime = json.loads(
                (episode_dir / "director_state" / "Runtime_State.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(runtime["next_action"], "NEED_NEW_CAMERA")
            self.assertTrue((scene_dir / "CAMERA_REQUIREMENT.md").is_file())

    def test_asset_gap_blocks_and_writes_requirement(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            episode_dir = Path(temp_name) / "episodes" / "EP999"
            scene_dir = episode_dir / "director_state" / "Scene01"
            shot_dir = scene_dir / "shots"
            shot_dir.mkdir(parents=True)
            shot = sample_execution_state()
            shot["required_assets"]["asset_ids"] = ["props.not-registered"]
            write_json(shot_dir / "Shot01-01_State.json", shot)
            write_json(
                scene_dir / "Scene_State.json",
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "scene_id": "Scene01",
                    "scene_number": 1,
                    "scene_title": "Test",
                    "plan_status": "LOCKED",
                    "status": "PRODUCTION",
                    "shot_count": 1,
                    "shots": ["Shot01-01"],
                    "next_scene": "EPISODE_END",
                    "updated_at": "2026-08-24T00:00:00+00:00",
                },
            )
            runtime_path = episode_dir / "director_state" / "Runtime_State.json"
            write_json(
                runtime_path,
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "current_scene_id": "Scene01",
                    "current_shot_id": "Shot01-01",
                    "director_session_mode": "PROMPT_ONLY",
                    "scene_status": "PRODUCTION",
                    "next_action": "GENERATE_CURRENT_SHOT_PACKAGE",
                    "pending_director_plan": None,
                    "pending_director_qa": None,
                    "last_event": "TEST_READY",
                    "updated_at": "2026-08-24T00:00:00+00:00",
                },
            )

            with self.assertRaises(AssetRequirementError):
                build_current_shot_package("EP999", episode_dir)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(runtime["next_action"], "NEED_ASSET")
            requirement = scene_dir / "ASSET_REQUIREMENT.md"
            self.assertTrue(requirement.is_file())
            self.assertIn("props.not-registered", requirement.read_text(encoding="utf-8"))

    def test_package_approval_and_episode_completion(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            episode_dir = Path(temp_name) / "episodes" / "EP999"
            scene_dir = episode_dir / "director_state" / "Scene01"
            shot_dir = scene_dir / "shots"
            shot_dir.mkdir(parents=True)

            shot = sample_execution_state()
            write_json(shot_dir / "Shot01-01_State.json", shot)
            write_json(
                scene_dir / "Scene_State.json",
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "scene_id": "Scene01",
                    "scene_number": 1,
                    "scene_title": "Test",
                    "plan_status": "LOCKED",
                    "status": "PRODUCTION",
                    "shot_count": 1,
                    "shots": ["Shot01-01"],
                    "next_scene": "EPISODE_END",
                    "updated_at": "2026-08-23T00:00:00+00:00",
                },
            )
            runtime_path = episode_dir / "director_state" / "Runtime_State.json"
            write_json(
                runtime_path,
                {
                    "schema_version": "4.1",
                    "episode_id": "EP999",
                    "current_scene_id": "Scene01",
                    "current_shot_id": "Shot01-01",
                    "director_session_mode": "PROMPT_ONLY",
                    "scene_status": "PRODUCTION",
                    "next_action": "GENERATE_CURRENT_SHOT_PACKAGE",
                    "pending_director_plan": None,
                    "pending_director_qa": None,
                    "last_event": "TEST_READY",
                    "updated_at": "2026-08-23T00:00:00+00:00",
                },
            )

            package_dir = build_current_shot_package("EP999", episode_dir)
            for name in [
                "IMAGE_PROMPT.md",
                "VIDEO_PROMPT.md",
                "UPLOAD_MANIFEST.json",
                "CHATGPT_HANDOFF.md",
                "PROMPT_COMPILATION_MANIFEST.json",
            ]:
                self.assertTrue((package_dir / name).is_file(), name)

            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(runtime["next_action"], "WAIT_FOR_IMAGE_APPROVAL")
            validate_state_payload(runtime, "Runtime_State.schema.json")

            generated = Path(temp_name) / "approved.png"
            generated.write_bytes(png_bytes())
            approve_image("EP999", episode_dir, generated)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(runtime["next_action"], "WAIT_FOR_VIDEO_APPROVAL")
            validate_state_payload(runtime, "Runtime_State.schema.json")

            approve_video("EP999", episode_dir, None)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(runtime["next_action"], "EPISODE_COMPLETE")
            validate_state_payload(runtime, "Runtime_State.schema.json")


if __name__ == "__main__":
    unittest.main()
