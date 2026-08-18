from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = load_module("check_availability", ROOT / "check_availability.py")
notifier = load_module("notify_github", ROOT / "notify_github.py")


class AvailabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product = {
            "name": "MikroTik hAP be³ Media",
            "mpn": "MA53UG+HbeH",
            "ean": "4752224010230",
            "name_terms": ["hAP", "be3", "Media"],
        }
        self.store = checker.Store(
            name="Test",
            country="PL",
            region="Polska",
            url="https://example.invalid/product",
            positive_patterns=(r"Dostępność:\s*Dostępny",),
            negative_patterns=(r"Brak w magazynie",),
            preorder_patterns=(r"Przewidywana dostawa",),
        )

    def test_superscript_identifier_normalization(self) -> None:
        self.assertEqual(checker.normalize_identifier("hAP be³ Media"), "hapbe3media")

    def test_json_ld_in_stock_is_available(self) -> None:
        html = """
        <html><head><script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "MikroTik hAP be³ Media",
          "mpn": "MA53UG+HbeH",
          "offers": {
            "@type": "Offer",
            "price": "649.00",
            "priceCurrency": "PLN",
            "availability": "https://schema.org/InStock"
          }
        }
        </script></head><body>Router Wi-Fi 7</body></html>
        """
        status, _, price, currency = checker.classify_html(html, self.store, self.product)
        self.assertEqual(status, checker.AVAILABLE)
        self.assertEqual(price, "649.00")
        self.assertEqual(currency, "PLN")

    def test_visible_out_of_stock_blocks_stale_json_ld_alert(self) -> None:
        html = """
        <script type="application/ld+json">
        {"@type":"Product","mpn":"MA53UG+HbeH","name":"hAP be3 Media",
         "offers":{"@type":"Offer","availability":"https://schema.org/InStock"}}
        </script>
        <main>Brak w magazynie</main>
        """
        status, reason, _, _ = checker.classify_html(html, self.store, self.product)
        self.assertEqual(status, checker.UNKNOWN)
        self.assertIn("conflicting signals", reason)

    def test_store_specific_negative_text(self) -> None:
        html = "<html><body><div>Brak w magazynie. Przewidywana dostawa: jutro.</div></body></html>"
        status, _, _, _ = checker.classify_html(html, self.store, self.product)
        self.assertEqual(status, checker.UNAVAILABLE)

    def test_store_specific_positive_text(self) -> None:
        html = "<html><body><div>Dostępność: Dostępny</div></body></html>"
        status, _, _, _ = checker.classify_html(html, self.store, self.product)
        self.assertEqual(status, checker.AVAILABLE)

    def test_ambiguous_page_never_alerts(self) -> None:
        html = "<html><body><h1>MikroTik hAP be3 Media</h1><button>Dodaj do koszyka</button></body></html>"
        status, _, _, _ = checker.classify_html(html, self.store, self.product)
        self.assertEqual(status, checker.UNKNOWN)

    def test_payload_observation_prioritizes_available(self) -> None:
        results = [
            checker.Result("A", "PL", "Polska", "https://a", checker.UNKNOWN, "error", "now"),
            checker.Result("B", "DE", "Europa", "https://b", checker.AVAILABLE, "stock", "now"),
        ]
        payload = checker.build_payload(self.product, results, "start")
        self.assertEqual(payload["observation"], checker.AVAILABLE)
        self.assertTrue(payload["fingerprint"])

    def test_payload_is_unknown_when_no_stock_and_one_store_is_unknown(self) -> None:
        results = [
            checker.Result("A", "PL", "Polska", "https://a", checker.UNKNOWN, "error", "now"),
            checker.Result("B", "DE", "Europa", "https://b", checker.UNAVAILABLE, "no stock", "now"),
        ]
        payload = checker.build_payload(self.product, results, "start")
        self.assertEqual(payload["observation"], checker.UNKNOWN)

    def test_notify_only_on_transition_or_changed_offer_set(self) -> None:
        payload = {"observation": checker.AVAILABLE, "fingerprint": "abc"}
        self.assertTrue(notifier.should_notify(checker.UNAVAILABLE, "", payload))
        self.assertFalse(notifier.should_notify(checker.AVAILABLE, "abc", payload))
        self.assertTrue(notifier.should_notify(checker.AVAILABLE, "xyz", payload))
        self.assertFalse(
            notifier.should_notify(checker.AVAILABLE, "abc", {"observation": checker.UNKNOWN, "fingerprint": ""})
        )


if __name__ == "__main__":
    unittest.main()
