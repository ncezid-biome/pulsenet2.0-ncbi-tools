from ..metadata_rules.default_fields import DefaultField

### Default all packages

BS_DEFAULT_ALL = (
    DefaultField(field="author", value="CDC"),
    DefaultField(field="spuid_namespace", value="EDLB-CDC"),
    DefaultField(field="isolation_source", value="missing"),
    DefaultField(field="purpose_of_sampling", value="missing"),
    DefaultField(field="strain", value="missing"),
    DefaultField(field="collected_by", value="missing"),
)

### Default Pathogen.cl.1.0
BS_DEFAULT_PATH = (
    DefaultField(field="host", value="missing"),
    DefaultField(field="host_disease", value="missing"),
    DefaultField(field="host_sex", value="missing"),
    DefaultField(field="state", value="missing"),
    DefaultField(field="lat_lon", value="missing"),
    DefaultField(field="sex", value="missing"),
    DefaultField(field="age", value="missing"),
    DefaultField(field="race", value="missing"),
    DefaultField(field="ethnicity", value="missing"),
    DefaultField(field="isolate", value="missing"),
    DefaultField(field="source_type", value="missing"),
)
