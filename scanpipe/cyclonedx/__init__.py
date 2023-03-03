# SPDX-License-Identifier: Apache-2.0
#
# http://nexb.com and https://github.com/nexB/scancode.io
# The ScanCode.io software is licensed under the Apache License version 2.0.
# Data generated with ScanCode.io is provided as-is without warranties.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Data Generated with ScanCode.io is provided on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. No content created from
# ScanCode.io should be considered or used as legal advice. Consult an Attorney
# for any legal advice.
#
# ScanCode.io is a free software code scanning tool from nexB Inc. and others.
# Visit https://github.com/nexB/scancode.io for support and download.

import json
import pathlib
from collections import defaultdict

import jsonschema
from hoppr_cyclonedx_models.cyclonedx_1_4 import (
    CyclonedxSoftwareBillOfMaterialsStandard as Bom_1_4,
)

CYCLONEDX_SPEC_VERSION = "1.4"
CYCLONEDX_JSON_SCHEMA_LOCATION = "bom-1.4.schema.json"
CYCLONEDX_JSON_SCHEMA_PATH = (
    pathlib.Path(__file__).parent / CYCLONEDX_JSON_SCHEMA_LOCATION
)
CYCLONEDX_JSON_SCHEMA_URL = (
    "https://raw.githubusercontent.com/"
    "CycloneDX/specification/master/schema/bom-1.4.schema.json"
)


def get_bom(cyclonedx_document):
    """
    Return CycloneDX BOM object.
    """
    return Bom_1_4(**cyclonedx_document)


def get_components(bom):
    """
    Return list of components from CycloneDX BOM.
    """
    return recursive_component_collector(bom.components, [])


def bom_attributes_to_dict(cyclonedx_attributes):
    """
    Return list of dict from a list of CycloneDX attributes.
    """
    if not cyclonedx_attributes:
        return []

    return [
        json.loads(attribute.json(exclude_unset=True, by_alias=True))
        for attribute in cyclonedx_attributes
    ]


def recursive_component_collector(root_component_list, collected):
    """
    Return list of components including the nested components.
    """
    if not root_component_list:
        return

    for component in root_component_list:
        extra_data = {}
        if component.components is not None:
            extra_data = bom_attributes_to_dict(component.components)

        collected.append({"cdx_package": component, "nested_components": extra_data})
        recursive_component_collector(component.components, collected)
    return collected


def resolve_license(license):
    """
    Return license expression/id/name from license item.
    """
    if "expression" in license:
        return license["expression"]
    elif "id" in license["license"]:
        return license["license"]["id"]
    else:
        return license["license"]["name"]


def get_declared_licenses(licenses):
    """
    Return resolved license from list of LicenseChoice.
    """
    if not licenses:
        return ""

    resolved_licenses = [
        resolve_license(license) for license in bom_attributes_to_dict(licenses)
    ]
    return "\n".join(resolved_licenses)


def get_checksums(component):
    """
    Return dict of all the checksums from a component.
    """
    if not component.hashes:
        return {}

    algorithm_map_cdx_scio = {
        "MD5": "md5",
        "SHA-1": "sha1",
        "SHA-256": "sha256",
        "SHA-512": "sha512",
    }
    return {
        algorithm_map_cdx_scio[algo_hash.alg.value]: algo_hash.content.__root__
        for algo_hash in component.hashes
        if algo_hash.alg.value in algorithm_map_cdx_scio
    }


def get_external_references(external_references):
    """
    Return dict of reference urls from list of `externalReferences`.
    """
    if not external_references:
        return {}

    references = defaultdict(lambda: [])

    for ref in external_references:
        references[ref.type.value].append(ref.url)

    return dict(references)


def validate_document(document, schema=CYCLONEDX_JSON_SCHEMA_PATH):
    """
    Check the validity of this CycloneDX document.
    """
    if isinstance(document, str):
        document = json.loads(document)

    if isinstance(schema, pathlib.Path):
        schema = schema.read_text()
    if isinstance(schema, str):
        schema = json.loads(schema)

    resolver = jsonschema.RefResolver(
        base_uri="file://" + str(pathlib.Path(__file__).parent), referrer=schema
    )

    validator = jsonschema.Draft7Validator(schema=schema, resolver=resolver)

    validator.validate(instance=document)
