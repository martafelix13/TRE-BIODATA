from typing import List, Union, Dict, Any
from pydantic import ConfigDict, Field
from rdflib import DCAT, DCTERMS, XSD, Literal, Namespace, URIRef
from rdflib.namespace import DefinedNamespace
from sempyro.dcat import DCATDataset
from sempyro.rdf_model import LiteralField
from sempyro.dcat.dcat_distribution import DCATDistribution
from sempyro.foaf.agent import Agent
from sempyro.vcard.vcard import VCard
from sempyro.utils.validator_functions import force_literal_field
import datetime
import fairclient.fdpclient
from pydantic import field_validator

BASE_URL = "http://localhost:8667"

# Define HealthDCAT-AP namespace with some properties
class HEALTHDCAT(DefinedNamespace):
    minTypicalAge: int
    maxTypicalAge: int
    numberOfUniqueIndividuals: int
    numberOfRecords: int
    populationCoverage: List[LiteralField]

    _NS = Namespace("http://example.com/ns/healthdcat#")

class TREDataset(DCATDataset):
    model_config = ConfigDict(
        json_schema_extra={
            "$ontology": "https://healthdcat-ap.github.io/",
            "$namespace": str(HEALTHDCAT),
            "$IRI": DCAT.Dataset,
            "$prefix": "healthdcatap"
        }
    )
    min_typical_age: int = Field(
        description="Minimum typical age of the population within the dataset",
        rdf_term=HEALTHDCAT.minTypicalAge,
        rdf_type="xsd:nonNegativeInteger",
    )
    max_typical_age: int = Field(
        description="Maximum typical age of the population within the dataset",
        rdf_term=HEALTHDCAT.maxTypicalAge,
        rdf_type="xsd:nonNegativeInteger",
    )
    no_unique_individuals: int = Field(
        description="Number of participants in study",
        rdf_term=HEALTHDCAT.numberOfUniqueIndividuals,
        rdf_type="xsd:nonNegativeInteger",
    )
    no_records: int = Field(
        description="Size of the dataset in terms of the number of records.",
        rdf_term=HEALTHDCAT.numberOfRecords,
        rdf_type="xsd:nonNegativeInteger",
    )
    population_coverage: List[Union[str, LiteralField]] = Field(
        default=None,
        description="A definition of the population within the dataset",
        rdf_term=HEALTHDCAT.populationCoverage,
        rdf_type="rdfs_literal",
    )

    has_version: LiteralField = Field(
        description="This resource has a more specific, versioned resource",
        rdf_term=DCTERMS.hasVersion,
        rdf_type="rdfs_literal",
    )

    identifier: List[Union[str, LiteralField]] = Field(
        description="A unique identifier of the resource being described or catalogued.",
        rdf_term=DCTERMS.identifier,
        rdf_type="rdfs_literal",
    )

    @field_validator("has_version", mode="before")
    @classmethod
    def convert_to_literal(cls, value: Union[str, LiteralField]) -> List[LiteralField]:
        return force_literal_field(value)

def create_and_publish_metadata(dataset_data: Dict[str, Any], distribution_data: List[Dict[str, Any]]):
    # Parse dataset information
    dataset_definition = dataset_data
    dataset_subject = URIRef(BASE_URL + "/tre/dataset")
    example_dataset = TREDataset(**dataset_definition)
    example_dataset_graph = example_dataset.to_graph(dataset_subject)

    # Parse distribution information
    distribution_graphs = []
    for dist_data in distribution_data:
        distribution_subject = URIRef(BASE_URL + f"/tre/distribution/{dist_data.get('id', '1')}")
        example_distribution = DCATDistribution(**dist_data)
        example_distribution_graph = example_distribution.to_graph(distribution_subject)
        distribution_graphs.append((distribution_subject, example_distribution_graph))

    # Add contact point to the dataset graph
    contact_uri = URIRef(BASE_URL + "/tre/contact/martafelix")
    contact = VCard(
        hasEmail=["mailto:marta.felix@tecnico.ulisboa.pt"],
        full_name=["Marta Félix"],
        hasUID="https://ror.org/000000"
    )
    example_contact_graph = contact.to_graph(contact_uri)
    example_dataset_graph += example_contact_graph

    # Add parent catalog reference
    fdp_parent_catalog = BASE_URL + "/catalog/bc43e54f-56d8-4c26-bd49-df3b9218ef0a"
    example_dataset_graph.add((dataset_subject, DCTERMS.isPartOf, URIRef(fdp_parent_catalog)))

    example_dataset_graph.set((dataset_subject, DCTERMS.issued,Literal("2024-01-01T00:00:00Z", datatype=XSD.dateTime)))
    example_dataset_graph.set((dataset_subject, DCTERMS.modified, Literal("2025-01-01T00:00:00Z", datatype=XSD.dateTime)))


    print("Dataset graph:")
    print(example_dataset_graph.serialize(format="turtle"))

    # Serialize and publish dataset
    fdp_baseurl = BASE_URL
    fdp_user = "albert.einstein@example.com"
    fdp_pass = "password"

    fdpclient = fairclient.fdpclient.FDPClient(base_url=fdp_baseurl, username=fdp_user, password=fdp_pass)
    new_dataset = fdpclient.create_and_publish("dataset", example_dataset_graph)

    # Publish distributions
    for distribution_subject, distribution_graph in distribution_graphs:
        distribution_graph.add((distribution_subject, DCTERMS.isPartOf, URIRef(f"{new_dataset}")))
        fdpclient.create_and_publish(resource_type="distribution", metadata=distribution_graph)

    return new_dataset

""" # Example usage
if __name__ == "__main__":
    # Example dataset and distribution data from frontend
    dataset_data = {
        "contact_point": [URIRef(BASE_URL + "/tre/contact/martafelix")],
        "creator": [Agent(name=["BioData.pt"], identifier="https://ror.org/02q7abn51")],
        "description": [LiteralField(value="Synthetic dataset for testing.")],
        "distribution": [BASE_URL + "/tre/distribution"],
        "release_date": datetime.datetime(2024, 7, 7, 11, 11, 11, tzinfo=datetime.timezone.utc),
        "keyword": [LiteralField(value="COVID")],
        "identifier": ["GDID-becadf5a-a1b2"],
        "update_date": datetime.datetime(2024, 11, 4, 10, 20, 5, tzinfo=datetime.timezone.utc),
        "publisher": [Agent(name=["BioData.pt"], identifier="https://ror.org/02q7abn51")],
        "theme": [URIRef("http://publications.europa.eu/resource/authority/data-theme/HEAL")],
        "title": [LiteralField(value="COVID-19 Dataset")],
        "license": URIRef("https://creativecommons.org/licenses/by-sa/4.0/"),
        "no_unique_individuals": 41514,
        "no_records": 18382376,
        "population_coverage": ["Synthetic population coverage."],
        "min_typical_age": 18,
        "max_typical_age": 64,
        "has_version": "0.1",
    }

    distribution_data = [
        {
            "publisher": [Agent(name=["BioData.pt"], identifier="https://ror.org/02q7abn51")],
            "title": ["GWAS Data Distribution"],
            "description": ["Synthetic GWAS data distribution."],
            "access_url": ["https://example.com/dataset/GDI-MS8-COVID19.vcf"],
            "media_type": "vcf",
            "has_version": "0.1",
        }
    ]

    new_dataset = create_and_publish_dataset(dataset_data, distribution_data)
    print(f"Dataset published at: {new_dataset}") """