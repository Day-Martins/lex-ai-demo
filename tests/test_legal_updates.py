from __future__ import annotations

import unittest

from services.legislative_update_service import OfficialSource, parse_feed


SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fonte oficial</title>
    <item>
      <title>Nova regra tributaria para contribuintes</title>
      <link>https://example.jus.br/noticia/1</link>
      <description><![CDATA[Resumo <strong>oficial</strong>.]]></description>
      <pubDate>Wed, 22 Jul 2026 12:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>
"""


class LegalUpdatesTest(unittest.TestCase):
    def test_parse_and_classify_official_feed(self) -> None:
        source = OfficialSource(
            name="Tribunal de teste",
            feed_url="https://example.jus.br/feed",
            homepage_url="https://example.jus.br/",
            default_area="Jurisprudência",
        )
        updates = parse_feed(SAMPLE_RSS, source)

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].area, "Tributário")
        self.assertEqual(updates[0].summary, "Resumo oficial.")
        self.assertEqual(
            updates[0].source_url,
            "https://example.jus.br/noticia/1",
        )


if __name__ == "__main__":
    unittest.main()
