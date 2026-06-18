
METADATA = """
sample,file1,file2,strain,sample_name,ncbi-spuid,ncbi-spuid_namespace,ncbi-bioproject,author,serovar,source_type,isolate_name_alias,isolation_source,geo_loc_name,organism,collection_date,collected_by,illumina_sequencing_instrument,illumina_library_strategy,illumina_library_source,illumina_library_selection,illumina_library_layout,illumina_library_protocol,project_name,sequenced_by,intended_consumer,food_origin,food_processing_method,purpose_of_sampling,biosample
test_sample,r1.fq,r2.fq,strain_name,test_sample,spuid,some_namespace,PRJNA56789,author_name,serovar_name,Food,test_sample,source,USA:TX,Escherichia coli,1/30/2002,collector,Illumina MiSeq,WGS,GENOMIC,RANDOM,PAIRED,Illumina DNA Prep,project,sequencer,human as food consumer,origin,food_proc_method,purpose,SAMN1234
""".lstrip()

BIO_XML = """
<?xml version="1.0" ?>
<Submission>
  <Description>
    <Comment>Not Provided</Comment>
    <Organization role="owner" type="consortium">
      <Name>CDC</Name>
      <Contact email="email@email.gov">
        <Name>
          <First>Pulsenet</First>
          <Last>CDC</Last>
        </Name>
      </Contact>
    </Organization>
  </Description>
  <Action>
    <AddData target_db="BioSample">
      <Data content_type="XML">
        <XmlContent>
          <BioSample schema_version="2.0">
            <SampleId>
              <SPUID spuid_namespace="some_namespace">spuid</SPUID>
            </SampleId>
            <Descriptor/>
            <Organism>
              <OrganismName>Escherichia coli</OrganismName>
            </Organism>
            <BioProject>
              <PrimaryId>PRJNA56789</PrimaryId>
            </BioProject>
            <Package>OneHealthEnteric.1.0</Package>
            <Attributes>
              <Attribute attribute_name="strain">strain_name</Attribute>
              <Attribute attribute_name="sample_name">test_sample</Attribute>
              <Attribute attribute_name="author">author_name</Attribute>
              <Attribute attribute_name="serovar">serovar_name</Attribute>
              <Attribute attribute_name="source_type">Food</Attribute>
              <Attribute attribute_name="isolate_name_alias">test_sample</Attribute>
              <Attribute attribute_name="isolation_source">source</Attribute>
              <Attribute attribute_name="geo_loc_name">USA:TX</Attribute>
              <Attribute attribute_name="collection_date">1/30/2002</Attribute>
              <Attribute attribute_name="collected_by">collector</Attribute>
              <Attribute attribute_name="project_name">project</Attribute>
              <Attribute attribute_name="sequenced_by">sequencer</Attribute>
              <Attribute attribute_name="intended_consumer">human as food consumer</Attribute>
              <Attribute attribute_name="food_origin">origin</Attribute>
              <Attribute attribute_name="food_processing_method">food_proc_method</Attribute>
              <Attribute attribute_name="purpose_of_sampling">purpose</Attribute>
            </Attributes>
          </BioSample>
        </XmlContent>
      </Data>
      <Identifier>
        <SPUID spuid_namespace="some_namespace">spuid</SPUID>
      </Identifier>
    </AddData>
  </Action>
</Submission>
""".lstrip()


SRA_XML = """
<?xml version="1.0" ?>
<Submission>
  <Description>
    <Comment>Not Provided</Comment>
    <Organization role="owner" type="consortium">
      <Name>CDC</Name>
      <Contact email="email@email.gov">
        <Name>
          <First>Pulsenet</First>
          <Last>CDC</Last>
        </Name>
      </Contact>
    </Organization>
  </Description>
  <Action>
    <AddFiles target_db="SRA">
      <File file_path="r1.fq">
        <DataType>generic-data</DataType>
      </File>
      <File file_path="r2.fq">
        <DataType>generic-data</DataType>
      </File>
      <Attribute name="instrument_model">Illumina MiSeq</Attribute>
      <Attribute name="library_strategy">WGS</Attribute>
      <Attribute name="library_source">GENOMIC</Attribute>
      <Attribute name="library_selection">RANDOM</Attribute>
      <Attribute name="library_layout">PAIRED</Attribute>
      <Attribute name="library_construction_protocol">Illumina DNA Prep</Attribute>
      <Attribute name="library_name">Not Provided</Attribute>
      <AttributeRefId name="BioProject">
        <RefId>
          <PrimaryId>PRJNA56789</PrimaryId>
        </RefId>
      </AttributeRefId>
      <AttributeRefId name="BioSample">
        <RefId>
          <PrimaryId db="BioSample">SAMN1234</PrimaryId>
        </RefId>
      </AttributeRefId>
      <Identifier>
        <SPUID spuid_namespace="some_namespace_sra">spuid_sra</SPUID>
      </Identifier>
    </AddFiles>
  </Action>
</Submission>
""".lstrip()

COMBINED_XML = """
<?xml version="1.0" ?>
<Submission>
  <Description>
    <Comment>Not Provided</Comment>
    <Organization role="owner" type="consortium">
      <Name>CDC</Name>
      <Contact email="email@email.gov">
        <Name>
          <First>Pulsenet</First>
          <Last>CDC</Last>
        </Name>
      </Contact>
    </Organization>
  </Description>
  <Action>
    <AddFiles target_db="SRA">
      <File file_path="r1.fq">
        <DataType>generic-data</DataType>
      </File>
      <File file_path="r2.fq">
        <DataType>generic-data</DataType>
      </File>
      <Attribute name="instrument_model">Illumina MiSeq</Attribute>
      <Attribute name="library_strategy">WGS</Attribute>
      <Attribute name="library_source">GENOMIC</Attribute>
      <Attribute name="library_selection">RANDOM</Attribute>
      <Attribute name="library_layout">PAIRED</Attribute>
      <Attribute name="library_construction_protocol">Illumina DNA Prep</Attribute>
      <Attribute name="library_name">Not Provided</Attribute>
      <AttributeRefId name="BioProject">
        <RefId>
          <PrimaryId>PRJNA56789</PrimaryId>
        </RefId>
      </AttributeRefId>
      <AttributeRefId name="BioSample">
        <RefId>
          <SPUID spuid_namespace="some_namespace">spuid</SPUID>
        </RefId>
      </AttributeRefId>
      <Identifier>
        <SPUID spuid_namespace="some_namespace_sra">spuid_sra</SPUID>
      </Identifier>
    </AddFiles>
  </Action>
  <Action>
    <AddData target_db="BioSample">
      <Data content_type="XML">
        <XmlContent>
          <BioSample schema_version="2.0">
            <SampleId>
              <SPUID spuid_namespace="some_namespace">spuid</SPUID>
            </SampleId>
            <Descriptor/>
            <Organism>
              <OrganismName>Escherichia coli</OrganismName>
            </Organism>
            <BioProject>
              <PrimaryId>PRJNA56789</PrimaryId>
            </BioProject>
            <Package>OneHealthEnteric.1.0</Package>
            <Attributes>
              <Attribute attribute_name="strain">strain_name</Attribute>
              <Attribute attribute_name="sample_name">test_sample</Attribute>
              <Attribute attribute_name="author">author_name</Attribute>
              <Attribute attribute_name="serovar">serovar_name</Attribute>
              <Attribute attribute_name="source_type">Food</Attribute>
              <Attribute attribute_name="isolate_name_alias">test_sample</Attribute>
              <Attribute attribute_name="isolation_source">source</Attribute>
              <Attribute attribute_name="geo_loc_name">USA:TX</Attribute>
              <Attribute attribute_name="collection_date">1/30/2002</Attribute>
              <Attribute attribute_name="collected_by">collector</Attribute>
              <Attribute attribute_name="project_name">project</Attribute>
              <Attribute attribute_name="sequenced_by">sequencer</Attribute>
              <Attribute attribute_name="intended_consumer">human as food consumer</Attribute>
              <Attribute attribute_name="food_origin">origin</Attribute>
              <Attribute attribute_name="food_processing_method">food_proc_method</Attribute>
              <Attribute attribute_name="purpose_of_sampling">purpose</Attribute>
            </Attributes>
          </BioSample>
        </XmlContent>
      </Data>
      <Identifier>
        <SPUID spuid_namespace="some_namespace">spuid</SPUID>
      </Identifier>
    </AddData>
  </Action>
</Submission>
""".lstrip()


META_YAML = """
---
NCBI_username: UNAME
NCBI_password: PASS
NCBI_ftp_host: 'ftp-private.ncbi.nlm.nih.gov'
NCBI_sftp_host: 'sftp-private.ncbi.nlm.nih.gov'
NCBI_API_URL: 'https://submit.ncbi.nlm.nih.gov/api/2.0/files/FILE_ID/?format=attachment'
table2asn_email: 'gb-admin@ncbi.nlm.nih.gov'
BioSample_package: "OneHealthEnteric.1.0"
Role: owner
Type: consortium
Org_ID: ""
Submitting_Org: CDC
Submitting_Org_Dept:
Street: 1600 Clifton Rd
City: Atlanta
State: GA
Postal_code: 30329
Country: USA
Email: email@email.gov
Phone: ""
Specified_Release_Date: ""
Submitter:
  '@email': email@email.gov
  '@alt_email': email@email.gov
  Name:
    First: Pulsenet
    Last: CDC
GISAID_client-id: TEST-EA76875B00C3
GISAID_username: username
GISAID_password: password
""".lstrip()

PUBLIC_BS_XML = """
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE BioSampleSet>
<BioSampleSet>
  <BioSample access="public" publication_date="2026-05-27T00:00:00.000" last_update="2026-05-27T15:44:24.533" submission_date="2026-05-27T15:41:05.900" id="12345" accession="SAMN12345">
    <Ids>
      <Id db="BioSample" is_primary="1">SAMN12345</Id>
      <Id db="SRA">SRS12345</Id>
      <Id db="EDLB-CDC">PNUSAS12345</Id>
    </Ids>
    <Description>
      <Title>One Health Enteric sample from Salmonella enterica</Title>
      <Organism taxonomy_id="28901" taxonomy_name="Salmonella enterica">
        <OrganismName>Salmonella enterica</OrganismName>
      </Organism>
    </Description>
    <Owner>
      <Name abbreviation="Pulsenet">PulseNet Next Generation Subtyping Methods Unit</Name>
    </Owner>
    <Models>
      <Model>One Health Enteric</Model>
    </Models>
    <Package display_name="One Health Enteric; version 1.0">OneHealthEnteric.1.0</Package>
    <Attributes>
      <Attribute attribute_name="strain" harmonized_name="strain" display_name="strain">PNUSAS12345</Attribute>
      <Attribute attribute_name="sample_name" harmonized_name="sample_name" display_name="sample name">PNUSAS12345</Attribute>
      <Attribute attribute_name="author">CDC</Attribute>
      <Attribute attribute_name="serovar" harmonized_name="serovar" display_name="serovar">Typhimurium</Attribute>
      <Attribute attribute_name="source_type" harmonized_name="source_type" display_name="source type">human</Attribute>
      <Attribute attribute_name="isolate_name_alias" harmonized_name="isolate_name_alias" display_name="isolate name alias">PNUSAS12345</Attribute>
      <Attribute attribute_name="isolation_source" harmonized_name="isolation_source" display_name="isolation source">missing</Attribute>
      <Attribute attribute_name="geo_loc_name" harmonized_name="geo_loc_name" display_name="geographic location">USA</Attribute>
      <Attribute attribute_name="collection_date" harmonized_name="collection_date" display_name="collection date">2026</Attribute>
      <Attribute attribute_name="collected_by" harmonized_name="collected_by" display_name="collected by">CDC</Attribute>
      <Attribute attribute_name="project_name" harmonized_name="project_name" display_name="project name">missing</Attribute>
      <Attribute attribute_name="sequenced_by" harmonized_name="sequenced_by" display_name="sequenced by">CDC</Attribute>
      <Attribute attribute_name="purpose_of_sampling" harmonized_name="purpose_of_sampling" display_name="purpose of sampling">missing</Attribute>
    </Attributes>
    <Links>
      <Link type="entrez" target="bioproject" label="PRJNA56789">56789</Link>
    </Links>
    <Status status="live" when="2026-05-27T15:41:05.899"/>
  </BioSample>
</BioSampleSet>
""".lstrip()
