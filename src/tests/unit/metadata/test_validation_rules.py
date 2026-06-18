import pytest

from pn_ncbi_pkg.metadata import Metadata
from pn_ncbi_pkg.metadata.rules.validation.rules import (
    ControlledLanguageField,
    ControlledLanguageSubField,
    MandatoryField,
    RegexField,
)
from pn_ncbi_pkg.result import Err, Ok


class TestMandatoryFields:
    def test_is_err_if_missing(self):
        rule = MandatoryField(field="mandatory")
        data_missing = Metadata({"other": ""})

        assert isinstance(rule(data_missing), Err)

    def test_is_err_if_blank_value(self):
        rule = MandatoryField(field="mandatory")
        data_missing = Metadata({"mandatory": ""})

        assert isinstance(rule(data_missing), Err)

    def test_is_ok_if_present(self):
        rule = MandatoryField(field="mandatory")
        data_present = Metadata({"mandatory": "something"})

        assert isinstance(rule(data_present), Ok)


class TestControlledLanguageFields:
    def test_field_err_if_unacceptable(self):
        rule = ControlledLanguageField(field="field",acceptable_values={"acceptable"})
        data_unacceptable = Metadata({"field": "unacceptable"})

        assert isinstance(rule(data_unacceptable), Err)

    def test_field_ok_if_acceptable(self):
        rule = ControlledLanguageField(field="field",acceptable_values={"acceptable"})
        data_acceptable = Metadata({"field": "acceptable"})

        assert isinstance(rule(data_acceptable), Ok)

    def test_field_ok_if_missing(self):
        rule = ControlledLanguageField(field="field",acceptable_values={"acceptable"})
        data_missing = Metadata({"other": ""})

        assert isinstance(rule(data_missing), Ok)


class TestControlledLanguageSubFields:
    @pytest.mark.parametrize(
        ("metadata", "case_sensitive", "expected_result"),
        [
            (Metadata({"other": ""}), True, Ok), # Ok if absent
            (Metadata({"geo_loc_name": ""}), True, Err),
            (Metadata({"geo_loc_name": "xyz"}), True, Err),
            (Metadata({"geo_loc_name": "Afghanistan"}), True, Ok),
            (Metadata({"geo_loc_name": "AFGHANISTAN"}), True, Err),
            (Metadata({"geo_loc_name": "AFGHANISTAN"}), False, Ok),
            (Metadata({"geo_loc_name": "Albania:region"}), True, Ok),
            (Metadata({"geo_loc_name": "ALBANIA:region"}), True, Err),
            (Metadata({"geo_loc_name": "ALBANIA:region"}), False, Ok),
            (Metadata({"geo_loc_name": "Albania:region:more"}), True, Ok),
        ]
    )
    def test_bs_controlled_lang_subfield(self, metadata, case_sensitive, expected_result):
        rule = ControlledLanguageSubField(
            field="geo_loc_name",
            case_sensitive=case_sensitive,
            acceptable_values={"Afghanistan", "Albania"},
            get_subvalue_method=lambda x: x.split(":")[0]
        )

        assert isinstance(rule(metadata), expected_result)


class TestRegexFields:
    @pytest.mark.parametrize(
        ("metadata", "case_sensitive", "expected_result"),
        [
            (Metadata({"other": ""}), True, Ok), # Ok if absent
            (Metadata({"biosample": ""}), True, Err),
            (Metadata({"biosample": "xyz"}), True, Err),
            (Metadata({"biosample": "SAMN123"}), True, Ok),
            (Metadata({"biosample": "samn123"}), False, Ok),
            (Metadata({"biosample": "samn123"}), True, Err)
        ]
    )
    def test_bs_controlled_lang_regex(self, metadata, case_sensitive, expected_result):
        rule = RegexField(
            field="biosample",
            pattern=r"SAMN\d+",
            case_sensitive=case_sensitive
        )

        assert isinstance(rule(metadata), expected_result)
