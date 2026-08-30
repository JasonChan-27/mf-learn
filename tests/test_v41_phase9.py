from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
TESTS_ROOT = PROJECT_ROOT / "tests"
FIXTURE_ROOT = TESTS_ROOT / "fixtures" / "phase9"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(TESTS_ROOT))

from asset_index import scan_assets
from asset_selector import parse_selection, resolve_requests
from director_plan_validator import classify_issues, validate_director_plan
from director_qa import validate_qa_result
from director_state import write_json
from production_runtime import advance_after_shot
from test_v41_phase6 import sample_execution_state


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Phase9EP002RegressionTests(unittest.TestCase):
    def test_markdown_escaped_asset_id_is_unescaped_deterministically(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            path = Path(temp_name) / "Asset_Selection.md"
            path.write_text(
                "# Selection\n\n## Outfits\n\n"
                "- asset:outfits.小南\\_周末休闲外出款\n",
                encoding="utf-8",
            )
            requests = parse_selection(path)
            self.assertEqual(len(requests), 1)
            self.assertEqual(
                requests[0].asset_id,
                "outfits.小南_周末休闲外出款",
            )

    def test_gpt_scene01_plan_passes_v41_contract_and_acceptance(self) -> None:
        plan = _json(FIXTURE_ROOT / "EP002_Scene01_Director_Plan.json")
        issues = validate_director_plan(plan)
        self.assertEqual(classify_issues(issues), "PASS", issues)
        self.assertEqual(len(plan["shots"]), 4)
        self.assertEqual(plan["shots"][-1]["next_shot"], "Scene02")
        self.assertTrue(plan["shots"][-1]["scene_end"])

        signatures = []
        for shot in plan["shots"]:
            self.assertTrue(shot["why_this_shot"].strip())
            self.assertTrue(shot["why_not_previous_shot"].strip())
            self.assertTrue(shot["coverage_reason"].strip())
            self.assertTrue(shot["composition_intent"].strip())
            self.assertTrue(shot["camera_reason"].strip())
            self.assertTrue(shot["frozen_moment"]["physical_boundaries"])
            self.assertTrue(
                shot["frozen_moment"]["forbidden_advanced_states"]
            )
            signatures.append((
                shot["primary_function"],
                shot["primary_focus"],
                shot["coverage"],
                shot["selected_camera"],
                shot["information_density"],
            ))
        for previous, current in zip(signatures, signatures[1:]):
            self.assertNotEqual(previous, current)

    def test_confirmed_dialogue_is_preserved_in_gpt_shot_delta(self) -> None:
        plan = _json(FIXTURE_ROOT / "EP002_Scene01_Director_Plan.json")
        motion = "\n".join(
            shot["shot_delta"]["primary_action"]
            for shot in plan["shots"]
        )
        for dialogue in [
            "主人……外面的世界竞争太激烈了。你一定要注意安全。",
            "主人……如果你回不来了……我们该怎么办呀？",
            "主人放心。我会照顾好他们两个。",
            "你们三个……我只是出去取个快递。很快回来。",
            "在家乖一点。",
        ]:
            self.assertIn(dialogue, motion)

    def test_phase9_qa_fixture_is_a_valid_pass(self) -> None:
        qa = _json(FIXTURE_ROOT / "EP002_Scene01_Director_QA.json")
        self.assertEqual(validate_qa_result(qa, "EP002", "Scene01"), [])
        self.assertEqual(qa["result"], "PASS")
        self.assertGreaterEqual(qa["scene_score"], 80)

    def test_registry_matches_all_master_files_and_phase9_plan_assets(self) -> None:
        registry = _json(PROJECT_ROOT / "assets" / "AssetRegistry.json")
        registered = {item["id"]: item for item in registry["assets"]}
        scanned = {item.id: asdict(item) for item in scan_assets()}
        # Phase9 established an 83-asset baseline. New permanent Masters may
        # extend the library without invalidating the original acceptance set.
        self.assertGreaterEqual(len(registered), 83)
        self.assertEqual(set(registered), set(scanned))

        for asset_id, expected in registered.items():
            actual = scanned[asset_id]
            self.assertEqual(actual["path"], expected["path"])
            self.assertEqual(actual["size_bytes"], expected["size_bytes"])
            self.assertEqual(actual["sha256"], expected["sha256"])

        requests = parse_selection(
            PROJECT_ROOT / "episodes" / "EP002" / "Asset_Selection.md"
        )
        selected, missing, ambiguous = resolve_requests(
            requests,
            list(registered.values()),
        )
        self.assertEqual(len(selected), len(requests))
        self.assertEqual(missing, [])
        self.assertEqual(ambiguous, [])

        plan = _json(FIXTURE_ROOT / "EP002_Scene01_Director_Plan.json")
        assets = plan["scene_assets"]
        required = {
            assets["environment_asset"],
            *assets["character_assets"].values(),
            *assets["outfit_assets"].values(),
            *assets["prop_assets"],
            *(
                shot["selected_camera"]
                for shot in plan["shots"]
                if shot["selected_camera"]
            ),
        }
        self.assertEqual(len(required), 7)
        self.assertFalse(required - set(registered))
        for asset_id in required:
            path = PROJECT_ROOT / registered[asset_id]["path"]
            self.assertTrue(path.is_file(), asset_id)
            self.assertEqual(path.stat().st_size, registered[asset_id]["size_bytes"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, registered[asset_id]["sha256"])

    def test_scene_transition_clears_pending_paths_and_refreshes_next_scene(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            episode_dir = Path(temp_name) / "episodes" / "EP999"
            state_root = episode_dir / "director_state"
            scene1 = state_root / "Scene01"
            scene2 = state_root / "Scene02"

            shot = sample_execution_state()
            shot["episode_id"] = "EP999"
            shot["scene_end"] = True
            shot["next_shot"] = "Scene02"
            write_json(scene1 / "shots" / "Shot01-01_State.json", shot)
            write_json(scene1 / "Scene_State.json", {
                "schema_version": "4.1",
                "episode_id": "EP999",
                "scene_id": "Scene01",
                "scene_number": 1,
                "scene_title": "Transition Source",
                "plan_status": "LOCKED",
                "status": "PRODUCTION",
                "shot_count": 1,
                "shots": ["Shot01-01"],
                "next_scene": "Scene02",
                "updated_at": "2026-01-01T00:00:00+00:00",
            })
            write_json(scene2 / "Scene_State.json", {
                "schema_version": "4.1",
                "episode_id": "EP999",
                "scene_id": "Scene02",
                "scene_number": 2,
                "scene_title": "Transition Target",
                "plan_status": "DRAFT",
                "status": "PLANNING",
                "shot_count": 0,
                "shots": [],
                "next_scene": "EPISODE_END",
                "updated_at": "2026-01-01T00:00:00+00:00",
            })
            write_json(state_root / "Runtime_State.json", {
                "schema_version": "4.1",
                "episode_id": "EP999",
                "current_scene_id": "Scene01",
                "current_shot_id": "Shot01-01",
                "director_session_mode": "PROMPT_ONLY",
                "scene_status": "PRODUCTION",
                "next_action": "WAIT_FOR_VIDEO_APPROVAL",
                "pending_director_plan": "director_state/Scene01/plan.json",
                "pending_director_qa": "director_state/Scene01/qa.json",
                "last_event": "TEST_READY",
                "updated_at": "2026-01-01T00:00:00+00:00",
            })

            self.assertEqual(
                advance_after_shot("EP999", episode_dir),
                "SCENE_END:Scene02",
            )
            runtime = _json(state_root / "Runtime_State.json")
            target = _json(scene2 / "Scene_State.json")
            self.assertEqual(runtime["current_scene_id"], "Scene02")
            self.assertEqual(runtime["current_shot_id"], "")
            self.assertEqual(runtime["next_action"], "PLAN_CURRENT_SCENE")
            self.assertIsNone(runtime["pending_director_plan"])
            self.assertIsNone(runtime["pending_director_qa"])
            self.assertNotEqual(
                target["updated_at"],
                "2026-01-01T00:00:00+00:00",
            )


if __name__ == "__main__":
    unittest.main()
