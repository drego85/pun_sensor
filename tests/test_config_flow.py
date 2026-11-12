"""Keep zone labels explicit without changing persisted market codes."""

import json
from pathlib import Path

import pytest

from custom_components.pun_sensor.config_flow import selector_config
from custom_components.pun_sensor.interfaces import Zona
from homeassistant.helpers.translation import async_get_translations


@pytest.mark.parametrize(
    "filename", ["strings.json", "translations/it.json", "translations/en.json"]
)
def test_zone_labels_preserve_codes_and_distinguish_foreign_zones(filename):
    """Every existing code gets a translated label, not a new stored value."""
    root = Path(__file__).parents[1] / "custom_components/pun_sensor"
    strings = json.loads((root / filename).read_text())
    labels = strings["selector"]["zona"]["options"]
    assert set(labels) == {zone.name for zone in Zona}
    assert set(selector_config["options"]) == set(labels)
    assert selector_config["translation_key"] == "zona"
    italy = "Italy" if filename.endswith("en.json") else "Italia"
    for code in ("NORD", "CNOR", "CSUD", "SUD", "CALA", "SARD", "SICI", "NAT"):
        assert labels[code].startswith(f"{italy} (")
    for code in ("CORS", "COAC", "FRAN", "AUST", "MALT"):
        assert not labels[code].startswith(italy)
    assert len(set(labels.values())) == len(labels)


@pytest.mark.parametrize(
    ("language", "expected"), [("it", "Italia (Nord)"), ("en", "Italy (North)")]
)
async def test_home_assistant_loads_zone_translations(hass, language, expected):
    """Exercise HA's actual translation loader, not only the JSON structure."""
    translations = await async_get_translations(
        hass, language, "selector", {"pun_sensor"}
    )
    assert translations["component.pun_sensor.selector.zona.options.NORD"] == expected
