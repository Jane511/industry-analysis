from pathlib import Path
from textwrap import dedent
from uuid import uuid4

from src.load_public_data import parse_ptrs_ar_workbook
from src.ptrs_reconstruction import PTRS_MODEL_NOTE, parse_ptrs_cycle_table_from_text, write_ptrs_workbook


CYCLE8_TEXT = dedent(
    """
    Table 10: New payment times measures by industry, Reporting Cycle 8
    Industry Average common
    payment terms
    Average
    payment time
    80th percentile
    payment time
    95th percentile
    payment time
    Average percentage
    paid on time
    Ranked by alphabetical order (days) (days) (days) (days) (%)
    Accommodation & Food Services 28 24.6 30 45 60.4%
    Administrative & Support Services 27 28.6 35 53 63.4%
    Agriculture, Forestry & Fishing 24 20.3 31 45 63.2%
    Arts & Recreation Services 26 19.9 31 50 72.2%
    Construction 33 29.1 40 60 70.3%
    Education & Training 19 21.4 30 49 71.6%
    Electricity, Gas, Water & Waste Services 22 20.7 27 45 77.0%
    Financial & Insurance Services 27 23.8 34 52 69.0%
    Health Care & Social Assistance 25 26.2 34 52 61.0%
    Information Media & Telecommunications 23 20.6 39 61 74.3%
    Manufacturing 36 33.4 48 67 66.1%
    Mining 32 27.7 36 50 70.9%
    Other Services 17 17.6 28 53 71.3%
    Professional, Scientific & Technical Services 27 27.2 36 62 64.3%
    Public Administration & Safety 23 15.4 20 37 75.6%
    Rental, Hiring & Real Estate Services 26 22.8 33 52 74.2%
    Retail Trade 32 29.7 42 64 65.4%
    Transport, Postal & Warehousing 28 25.6 35 56 66.3%
    Wholesale Trade 31 28.6 40 58 66.5%
    All Industries 29 26.2 37 56 68.1%
    """
).strip()


CYCLE9_TEXT = dedent(
    """
    Table 9: Payment terms and times measures by industry, Reporting Cycle 9
    Industry
    Ranked by alphabetical order
    Average common
    payment term
    (days)
    Average
    payment time
    (days)
    80th percentile
    payment time
    (days)
    95th percentile
    payment time
    (days)
    Average percentage
    paid on time
    (%)
    Accommodation & Food Services 25 25.4 35 54 61.0%
    Administrative & Support Services 25 22.6 31 45 70.0%
    Agriculture, Forestry & Fishing 24 23.4 35 49 73.4%
    Arts & Recreation Services 25 21.1 30 50 69.4%
    Construction 34 33.5 47 68 64.8%
    Education & Training 20 24.4 33 62 71.6%
    Electricity, Gas, Water & Waste Services 26 23.5 31 48 68.6%
    Financial & Insurance Services 21 17.4 27 49 72.1%
    Health Care & Social Assistance 26 27.5 39 62 60.3%
    Information Media & Telecommunications 29 24.7 35 67 69.1%
    Manufacturing 35 33.7 47 67 62.1%
    Mining 32 30.0 39 70 68.7%
    Other Services 26 28.4 38 57 72.3%
    Professional, Scientific & Technical Services 28 27.9 38 94 64.8%
    Public Administration & Safety 23 23.3 31 51 68.0%
    Rental, Hiring & Real Estate Services 27 25.8 34 56 66.9%
    Retail Trade 31 28.7 40 77 67.5%
    Transport, Postal & Warehousing 30 27.7 41 62 61.9%
    Wholesale Trade 33 29.3 41 65 65.4%
    All Industries 29 27.4 39 64 66.5%
    """
).strip()


def test_parse_ptrs_cycle8_table_from_text():
    result = parse_ptrs_cycle_table_from_text(CYCLE8_TEXT, 8)

    assert list(result["Industry Code"])[:4] == ["A", "B", "C", "D"]
    retail = result[result["Industry Code"] == "G"].iloc[0]
    services = result[result["Industry Code"] == "M"].iloc[0]
    assert retail["Industry Name"] == "Retail Trade"
    assert retail["Avg Payment Time (Days)"] == 29.7
    assert retail["80th pct (Days)"] == 42
    assert retail["Avg % Paid On Time"] == 0.654
    assert services["Industry Name"] == "Professional, Scientific and Technical Services"


def test_parse_ptrs_cycle9_table_from_text():
    result = parse_ptrs_cycle_table_from_text(CYCLE9_TEXT, 9)

    construction = result[result["Industry Code"] == "E"].iloc[0]
    health = result[result["Industry Code"] == "Q"].iloc[0]
    assert construction["Avg Common Payment Term (Days)"] == 34
    assert construction["95th pct (Days)"] == 68
    assert health["Industry Name"] == "Health Care and Social Assistance"
    assert health["Avg Payment Time (Days)"] == 27.5
    assert health["Avg % Paid On Time"] == 0.603


def test_write_ptrs_workbook_remains_parseable_without_excel_calculation():
    cycle8_df = parse_ptrs_cycle_table_from_text(CYCLE8_TEXT, 8)
    cycle9_df = parse_ptrs_cycle_table_from_text(CYCLE9_TEXT, 9)
    temp_dir = Path("tests") / ".tmp" / f"ptrs-{uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = temp_dir / "PTRS_MultiCycle_AR_Days_Model_Official.xlsx"

    write_ptrs_workbook(cycle8_df, cycle9_df, workbook_path)
    parsed = parse_ptrs_ar_workbook(workbook_path)

    retail = parsed[parsed["anzsic_division_code"] == "G"].iloc[0]
    professional = parsed[parsed["anzsic_division_code"] == "M"].iloc[0]
    assert retail["ptrs_cycle8_avg_payment_days"] == 29.7
    assert retail["ptrs_cycle9_avg_payment_days"] == 28.7
    assert retail["ptrs_base_ar_days"] == 29.7
    assert retail["ptrs_stress_ar_days"] == 42.0
    assert retail["ptrs_severe_ar_days"] == 77.0
    assert retail["ptrs_adjusted_base_ar_days"] == 29.7
    assert retail["ptrs_conservative_multiplier"] == 1.0
    assert professional["ptrs_severe_ar_days"] == 94.0
    assert professional["ptrs_model_note"] == PTRS_MODEL_NOTE
