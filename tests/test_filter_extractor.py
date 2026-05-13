from app.qa.filter_extractor import extract_query_filters, merge_filters


def test_extract_query_filters_detects_trouble_code():
    assert extract_query_filters("P0301 是什么意思")["code"] == "P0301"


def test_extract_query_filters_detects_vehicle_model():
    assert extract_query_filters("L9 的 AUTOHOLD 怎么开")["vehicle_model"] == "L9"


def test_merge_filters_keeps_explicit_values():
    merged = merge_filters({"vehicle_model": "L8"}, {"vehicle_model": "L9", "code": "P0301"})
    assert merged == {"vehicle_model": "L8", "code": "P0301"}
