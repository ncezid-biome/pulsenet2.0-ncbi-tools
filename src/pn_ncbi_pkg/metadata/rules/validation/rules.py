from ..metadata_rules.validation_fields import (
    ControlledLanguageField,
    ControlledLanguageSubField,
    ImmutableField,
    MandatoryField,
    MandatoryGroup,
    RegexField,
)
from . import acceptable_values

###################### MANDATORY ######################
### Mandatory all BS/SRA/both
ALL_MANDATORY = (
    MandatoryField(field="spuid"),
    MandatoryField(field="spuid_namespace"),
    MandatoryField(field="bioproject"),
)

### Mandatory all bs packages
BS_ALL_MANDATORY = (
    MandatoryField(field="sample_name"),
    MandatoryField(field="organism"),
    MandatoryField(field="collected_by"),
    MandatoryField(field="collection_date"),
    MandatoryField(field="geo_loc_name"),
    MandatoryField(field="isolation_source"),
)

### Mandatory Pathogen.cl.1.0
BS_PATH_MANDATORY = (
    MandatoryGroup(fields=["strain", "isolate"]),
    MandatoryField(field="host"),
    MandatoryField(field="host_disease"),
    MandatoryField(field="lat_lon"),
)

### Mandatory OneHealthEnteric.1.0
BS_OHE_MANDATORY = (
    MandatoryField(field="isolation_source"),
    MandatoryField(field="source_type"),
    MandatoryField(field="strain"),
)

### Mandatory SRA
SRA_MANDATORY = (
    MandatoryField(field="file1"),
    MandatoryField(field="file2"),
    MandatoryField(field="instrument_model"),
    MandatoryField(field="library_source"),
    MandatoryField(field="library_selection"),
    MandatoryField(field="library_layout"),
    MandatoryField(field="library_strategy"),
)

### Mandatory if not original BS sub
MANDATORY_BIOSAMPLE = (MandatoryField(field="biosample"),)

#######################################################


################# CONTROLLED LANGUAGE #################
### Controlled language sra
SRA_CONTROLLED = (
    ControlledLanguageField(
        field="instrument_model",
        case_sensitive=True,
        acceptable_values=acceptable_values.ILLUMINA_INSTRUMENT_MODEL
    ),
    ControlledLanguageField(
        field="library_source",
        case_sensitive=True,
        acceptable_values=acceptable_values.ILLUMINA_LIBRARY_SOURCE
    ),
    ControlledLanguageField(
        field="library_selection",
        case_sensitive=True,
        acceptable_values=acceptable_values.ILLUMINA_LIBRARY_SELECTION
    ),
    ControlledLanguageField(
        field="library_layout",
        case_sensitive=False,
        acceptable_values=acceptable_values.ILLUMNINA_LIBARY_LAYOUT
    ),
    ControlledLanguageField(
        field="library_strategy",
        case_sensitive=True,
        acceptable_values=acceptable_values.ILLUMINA_LIBRARY_STRATEGY
    ),
)

CONTROLLED_BIOSAMPLE = (
    RegexField(
        field="biosample",
        case_sensitive=False,
        pattern=r"(?:SAMN|samn).+"
    ),
)

### Controlled language all BS
BS_ALL_CONTROLLED = (
    ControlledLanguageSubField(
        field="geo_loc_name",
        case_sensitive=True,
        acceptable_values=acceptable_values.COUNTRY,
        get_subvalue_method=lambda x: x.split(":")[0]
    ),
    ControlledLanguageField(
        field="host_sex",
        case_sensitive=False,
        acceptable_values=acceptable_values.BS_HOST_SEX
    ),
    RegexField(
        field="lat_lon",
        case_sensitive=False,
        # pattern from NCBI docs "d[d.dddd] N|S d[dd.dddd] W|E", eg, 38.98 N 77.11 W
        pattern=r"\d{1,2}\.?\d* [NS] \d{1,3}\.?\d* [WE]"
    ),
)

### Controlled language OneHealthEnteric.1.0
BS_OHE_CONTROLLED = (
    ControlledLanguageField(
        field="source_type",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_SOURCE_TYPE
    ),
    ControlledLanguageField(
        field="building_setting",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_BUILDING_SETTING
    ),
    ControlledLanguageField(
        field="env_monitoring_zone",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_ENV_MONITORING_ZONE
    ),
    ControlledLanguageField(
        field="indoor_surf",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_INDOOR_SURFACE
    ),
    ControlledLanguageField(
        field="intended_consumer",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_INTENDED_CONSUMER
    ),
    ControlledLanguageField(
        field="spec_intended_cons",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_SPEC_INTENDED_CONS
    ),
    ControlledLanguageField(
        field="surf_material",
        case_sensitive=False,
        acceptable_values=acceptable_values.OHE_SURF_MATERIAL
    ),
)

#######################################################


################# EDIT METADATA #######################
BS_IMMUTABLE_EDIT_FIELDS = (
    ImmutableField(field="spuid"),
    ImmutableField(field="spuid_namespace"),
    ImmutableField(field="bioproject"),
    ImmutableField(field="organism"),
    ImmutableField(field="strain"),
    ImmutableField(field="isolate"),
    ImmutableField(field="serovar"),
    ImmutableField(field="serotype"),
)
