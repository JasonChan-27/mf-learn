from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from asset_index import AssetRecord
from build_episode import refresh_project_asset_registry, write_manifest


class Phase8WorkflowTests(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (PROJECT_ROOT / relative).read_text(encoding="utf-8")

    def test_official_docs_use_only_v41_run_entry(self) -> None:
        for relative in ["README.md", "00_START_HERE.md", "00_WORKFLOW.md"]:
            content = self._read(relative)
            self.assertIn("python3.12 tools/run.py", content, relative)
            self.assertNotIn("python tools/run.py", content, relative)
            self.assertNotIn("python tools/build_episode.py", content, relative)
        workflow = self._read("00_WORKFLOW.md")
        self.assertIn("唯一日常入口", workflow)
        self.assertIn("旧 V2/V4", workflow)

    def test_production_standard_freezes_authority_boundaries(self) -> None:
        standard = self._read("director/Production_Standard.md")
        for phrase in [
            "GPT Director Brain",
            "Director Plan = Shot 设计唯一来源",
            "Shot State",
            "Runtime State",
            "NEED_NEW_CAMERA",
            "NEED_ASSET",
            "why_not_previous_shot",
            "Python 不",
        ]:
            self.assertIn(phrase, standard)

    def test_cli_guidance_is_python312_and_does_not_request_prompt_rewrite(self) -> None:
        source = self._read("tools/run.py")
        self.assertNotIn("python tools/run.py", source)
        self.assertIn("python3.12 tools/run.py", source)
        self.assertIn("不得让 GPT 重新导演或改写已编译 Prompt", source)

    def test_context_pack_requests_plan_or_qa_json_only(self) -> None:
        source = self._read("tools/build_context_pack.py")
        self.assertIn("Scene Director Plan JSON 或 Director QA JSON", source)
        self.assertIn("只输出符合模板和 Schema 的纯 JSON", source)
        self.assertIn("禁止在 Planning", source)
        self.assertNotIn("Image Prompt、Video Prompt 均由你自主完成", source)
        self.assertIn('"assets" / "AssetRegistry.json"', source)
        self.assertNotIn('"assets" / "Asset_Registry.md"', source)

    def test_build_manifest_and_sources_use_v41_standard(self) -> None:
        source = self._read("tools/build_episode.py")
        self.assertIn('PROJECT_ROOT / "director" / "Production_Standard.md"', source)
        self.assertIn('PROJECT_ROOT / "director" / "STATE" / "Director_QA_Result.schema.json"', source)
        self.assertIn('shutil.copy2(WORKFLOW, output_dir / "00_WORKFLOW.md")', source)
        for legacy in [
            'PROJECT_ROOT / "director" / "Production_Stage_Prompt.md"',
            'PROJECT_ROOT / "director" / "Output_Spec.md"',
            'PROJECT_ROOT / "director" / "Production_Prompt_Quality_Gate.md"',
            'PROJECT_ROOT / "director" / "Prompt_Language_Policy.md"',
        ]:
            self.assertNotIn(legacy, source)

        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            output = Path(temp_name)
            manifest = write_manifest("EP999", output, {}, "production")
            content = manifest.read_text(encoding="utf-8")
            self.assertIn("V4.1 Director Upload Manifest", content)
            self.assertIn("python3.12 tools/run.py EP999", content)
            self.assertIn("Planning / QA 只返回", content)
            self.assertNotIn("请直接开始 Production Stage", content)

    def test_build_refreshes_project_registry_from_the_same_asset_scan(self) -> None:
        record = AssetRecord(
            id="cameras.entrance-hall-camera02",
            name="Entrance Hall Camera02",
            category="cameras",
            path="assets/cameras/Entrance Hall Camera02.png",
            aliases=["Entrance Hall Camera02"],
            tags=["cameras"],
            sha256="a" * 64,
            size_bytes=1234,
        )

        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            output = Path(temp_name) / "assets" / "AssetRegistry.json"
            payload = refresh_project_asset_registry([record], output=output)
            saved = json.loads(output.read_text(encoding="utf-8"))

            self.assertEqual(saved, payload)
            self.assertEqual(saved["asset_count"], 1)
            self.assertEqual(saved["assets"][0]["id"], record.id)

    def test_empty_asset_scan_never_overwrites_existing_registry(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as temp_name:
            output = Path(temp_name) / "assets" / "AssetRegistry.json"
            output.parent.mkdir(parents=True)
            original = '{"keep": true}\n'
            output.write_text(original, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "不会用空 Registry 覆盖"):
                refresh_project_asset_registry([], output=output)

            self.assertEqual(output.read_text(encoding="utf-8"), original)

    def test_project_version_and_ep002_remain_at_empty_scene01_planning(self) -> None:
        config = json.loads(self._read("catdrama.json"))
        self.assertEqual(config["version"], "4.1.1")

        state_root = PROJECT_ROOT / "episodes" / "EP002" / "director_state"
        runtime = json.loads((state_root / "Runtime_State.json").read_text(encoding="utf-8"))
        scene = json.loads(
            (state_root / "Scene01" / "Scene_State.json").read_text(encoding="utf-8")
        )
        self.assertEqual(runtime["current_scene_id"], "Scene01")
        self.assertEqual(runtime["current_shot_id"], "")
        self.assertEqual(runtime["next_action"], "PLAN_CURRENT_SCENE")
        self.assertEqual(scene["plan_status"], "DRAFT")
        self.assertEqual(scene["status"], "PLANNING")
        self.assertEqual(scene["shot_count"], 0)
        self.assertEqual(scene["shots"], [])


if __name__ == "__main__":
    unittest.main()
