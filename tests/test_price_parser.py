"""Tests for the public standard-price HTML parser."""

from custom_components.geld_fuereauto.coordinator import parse_prices


def test_parse_complete_public_price_table():
    rows = "".join(
        f"<tr><td>PKW ({cls})</td><td>1.230 €</td>"
        f"<td>90 %</td><td>180 €</td></tr>"
        for cls in ("M1", "N1", "N2", "N3", "M3")
    )
    html = f"<h2>Quotenjahr 2027</h2><table>{rows}</table>"
    data = parse_prices(html)
    assert data[(2027, "M1", "garantie")] == 1230.0
    assert data[(2027, "N3", "risiko")] == 90.0
    assert data[(2027, "M3", "express")] == 180.0
    assert len(data) == 15


def test_incomplete_year_is_rejected():
    html = (
        "<h2>Quotenjahr 2027</h2><table><tr>"
        "<td>PKW (M1)</td><td>230 €</td>"
        "<td>90 %</td><td>180 €</td>"
        "</tr></table>"
    )
    try:
        parse_prices(html)
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete price table must be rejected")
