"""XML output converter (HR Open Standards compliant).

Produces an XML document whose element structure mirrors the HR Open Standards
PersonProfileType. The required copyright + compliance notices are emitted as
XML comment nodes at the very top of every document.
"""

from __future__ import annotations

from lxml import etree

from app.converters.base_converter import BaseConverter
from app.schemas.hr_open_standards import (
    HR_OPEN_ATTRIBUTION,
    HR_OPEN_COMPLIANCE,
    HR_OPEN_VERSION,
    PersonProfile,
)

# The XML namespace used for HR Open Standards profile documents.
HR_OPEN_NAMESPACE = "http://www.hropenstandards.org/4.2.0"


class XmlConverter(BaseConverter):
    """Serializes a :class:`PersonProfile` to HR Open Standards XML."""

    format_name = "xml"
    media_type = "application/xml"
    file_extension = ".xml"

    def convert(self, profile: PersonProfile) -> str:
        """Return the profile as a pretty-printed XML string with notices."""
        # Start from the plain dict (without the JSON-only "_" notice keys).
        data = profile.model_dump(exclude_none=True)

        # Create the root <PersonProfile> element in the HR Open namespace.
        # ``nsmap`` declares the default namespace on the root element.
        root = etree.Element("PersonProfile", nsmap={None: HR_OPEN_NAMESPACE})
        root.set("specificationVersion", HR_OPEN_VERSION)

        # Recursively build child elements from the dict structure.
        self._build(root, data)

        # Assemble the full document so we can prepend comment nodes.
        doc = etree.ElementTree(root)

        # Build the two required attribution/compliance comments.
        attribution_comment = etree.Comment(f" {HR_OPEN_ATTRIBUTION} ")
        compliance_comment = etree.Comment(f" {HR_OPEN_COMPLIANCE} ")
        # ``addprevious`` inserts the comments immediately before the root, so
        # they appear at the top of the serialized document.
        root.addprevious(attribution_comment)
        root.addprevious(compliance_comment)

        # ``xml_declaration=True`` adds the <?xml ...?> header; pretty_print
        # indents the output for readability.
        xml_bytes = etree.tostring(
            doc,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        return xml_bytes.decode("utf-8")

    def _build(self, parent: etree._Element, value: object, item_name: str = "item") -> None:
        """Recursively turn Python data into XML child elements.

        Args:
            parent: The element to attach children to.
            value: A dict, list, or scalar to serialize.
            item_name: The tag name to use for anonymous list items.

        This handles the three shapes our data can take:
          * dict  -> one child element per key
          * list  -> repeated child elements
          * scalar-> element text
        """
        if isinstance(value, dict):
            # For each key/value, create a sub-element named after the key.
            for key, sub_value in value.items():
                if isinstance(sub_value, list):
                    # Lists become repeated elements named after the key.
                    for entry in sub_value:
                        child = etree.SubElement(parent, key)
                        self._build(child, entry, item_name=key)
                else:
                    child = etree.SubElement(parent, key)
                    self._build(child, sub_value, item_name=key)
        elif isinstance(value, list):
            # A bare list (rare here) -> repeated <item> elements.
            for entry in value:
                child = etree.SubElement(parent, item_name)
                self._build(child, entry, item_name=item_name)
        else:
            # Scalar value: booleans become "true"/"false", others use str().
            if isinstance(value, bool):
                parent.text = "true" if value else "false"
            else:
                parent.text = str(value)
