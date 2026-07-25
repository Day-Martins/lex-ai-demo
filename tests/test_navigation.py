from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NavigationTest(unittest.TestCase):
    def test_access_page_uses_integrated_gateway_session(self) -> None:
        home_source = (PROJECT_ROOT / "app" / "Página_Inicial.py").read_text()
        access_source = (
            PROJECT_ROOT / "app" / "pages" / "0_🔑_Acesso.py"
        ).read_text()

        self.assertNotIn("render_access_portal", home_source)
        self.assertNotIn("render_access_portal", access_source)
        self.assertIn("require_user()", access_source)
        self.assertIn("logout_url()", access_source)
        self.assertNotIn("Entrar ou solicitar cadastro", home_source)
        self.assertNotIn("Acesse a plataforma", home_source)

    def test_access_page_buttons_have_readable_variants(self) -> None:
        access_source = (
            PROJECT_ROOT / "app" / "pages" / "0_🔑_Acesso.py"
        ).read_text()
        style_source = (
            PROJECT_ROOT / "app" / "utils" / "page_style.py"
        ).read_text()

        self.assertIn('type="primary"', access_source)
        self.assertIn('type="secondary"', access_source)
        self.assertIn('.stLinkButton > a[kind="primary"]', style_source)
        self.assertIn(".stLinkButton > a *", style_source)

    def test_fiscus_feature_uses_custom_tax_reform_icon(self) -> None:
        fiscus_source = (
            PROJECT_ROOT
            / "app"
            / "pages"
            / "2_↳_Direito_Tributário_·_Fiscus_AI.py"
        ).read_text()
        icon_source = (
            PROJECT_ROOT / "app" / "utils" / "tax_reform_icon.py"
        ).read_text()

        self.assertIn("tax_reform_calculator_icon", fiscus_source)
        self.assertIn('data-icon="tax-reform-calculator"', icon_source)
        self.assertNotIn('"🧮"', fiscus_source)


if __name__ == "__main__":
    unittest.main()
