from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPDATE_CARD_PATH = PROJECT_ROOT / "app" / "utils" / "update_card.py"


class UpdateCardRenderingTest(unittest.TestCase):
    def test_card_is_rendered_as_html_and_escapes_content(self) -> None:
        fake_streamlit = ModuleType("streamlit")
        fake_streamlit.html = Mock()
        spec = spec_from_file_location("update_card_under_test", UPDATE_CARD_PATH)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = module_from_spec(spec)

        with patch.dict(sys.modules, {"streamlit": fake_streamlit}):
            spec.loader.exec_module(module)
            module.render_update_card(
                titulo='<script>alert("x")</script>',
                resumo="Resumo <b>seguro</b>",
                area="Penal",
                data_publicacao="24/07/2026",
                fonte="Câmara",
                url_fonte="https://example.com/?q=lei&tipo=1",
            )

        fake_streamlit.html.assert_called_once()
        markup = fake_streamlit.html.call_args.args[0]
        self.assertIn('<article class="lex-update-card">', markup)
        self.assertIn("&lt;script&gt;", markup)
        self.assertNotIn("<script>", markup)
        self.assertNotIn("unsafe_allow_html", markup)


if __name__ == "__main__":
    unittest.main()
