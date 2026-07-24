from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NavigationTest(unittest.TestCase):
    def test_access_form_exists_only_on_access_page(self) -> None:
        home_source = (PROJECT_ROOT / "app" / "Página_Inicial.py").read_text()
        access_source = (
            PROJECT_ROOT / "app" / "pages" / "0_🔑_Acesso.py"
        ).read_text()

        self.assertNotIn("render_access_portal", home_source)
        self.assertIn("render_access_portal()", access_source)


if __name__ == "__main__":
    unittest.main()
