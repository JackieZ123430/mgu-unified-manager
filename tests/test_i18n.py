"""Offline display-language regressions: no vehicle or subprocess operations."""
import os
import unittest
from unittest.mock import patch, Mock
from app.i18n import tr, language, ZH_CN

class LocalizationTests(unittest.TestCase):
    def test_english_is_exact_fallback(self):
        with patch.dict(os.environ, {"MGU_UI_LANGUAGE": "en"}):
            for source in ZH_CN:
                self.assertEqual(tr(source), source)

    def test_chinese_and_unknown_values(self):
        with patch.dict(os.environ, {"MGU_UI_LANGUAGE": "zh-CN"}):
            self.assertEqual(tr("Activity log"), "操作日志")
            for value in ("--yes", "id8-bcp", "stock", "WBA00000000000000", "id -u = 0"):
                self.assertEqual(tr(value), value)
            self.assertEqual(language(), "zh-CN")

    def test_unsupported_locale_falls_back(self):
        with patch.dict(os.environ, {"MGU_UI_LANGUAGE": "de-DE"}):
            self.assertEqual(tr("Activity log"), "Activity log")

    def test_simplified_system_locale(self):
        with patch.dict(os.environ, {}, clear=True), patch("app.i18n.locale.getlocale", return_value=("zh_CN", "UTF-8")):
            self.assertEqual(language(), "zh-CN")

    def test_vehicle_arguments_do_not_follow_display_language(self):
        import ast
        from pathlib import Path
        from types import SimpleNamespace
        source = ast.parse((Path(__file__).resolve().parents[1]/"app/main.py").read_text(encoding="utf-8"))
        cls = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == "UnifiedGUI")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_ssh_args")
        namespace = {}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "_ssh_args", "exec"), namespace)
        gui = SimpleNamespace()
        gui._ssh_args = lambda *args: namespace["_ssh_args"](gui, *args)
        for field, value in {"arch":"id8-bcp", "gateway":"auto", "vin":"WBA00000000000000", "mgu_ip":"", "persist":True, "unique":False}.items():
            setattr(gui, field, Mock(get=Mock(return_value=value)))
        with patch.dict(os.environ, {"MGU_UI_LANGUAGE":"en"}):
            english = gui._ssh_args("enable", True)
        with patch.dict(os.environ, {"MGU_UI_LANGUAGE":"zh-CN"}):
            self.assertEqual(gui._ssh_args("enable", True), english)
        self.assertEqual(english, ["enable", "--yes", "--arch", "id8-bcp", "--gateway", "auto", "--vin", "WBA00000000000000", "--persist", "--no-unique-key"])

if __name__ == "__main__":
    unittest.main()
