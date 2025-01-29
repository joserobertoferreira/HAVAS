import json
import xml.etree.ElementTree as ET
from typing import Any

from config import settings
from utils.conversions import Conversions
from utils.handle_files import HandleFiles
from utils.xml.placeholder import Placeholder
from utils.xml.tag_factory import TagFactory

ATTACH_PDF = 2


class HandleXML(Placeholder, TagFactory):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.mapping = self.load_mapping(kwargs.get('mapping_file_path'))

    @staticmethod
    def load_mapping(file_path: str) -> Any:
        """Load a JSON mapping from a file.

        Args:
            file_path (str): The path to the file containing the mapping.

        Returns:
            JSON dict: The mapping loaded from the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def generate_xml(self, output_file: str):
        """Generate the XML file based on the provided mapping."""
        root = self.create_root_element()
        self.add_sender_receiver(root)

        invoice = self.add_invoice(root)
        self.add_binary_document_attachment(invoice)
        self.add_attachments(invoice)
        self.add_seller(invoice)
        self.add_buyer_billto(invoice)
        self.add_saphety_specific_info(invoice)
        self.add_qr_data(invoice)
        self.add_line_items(invoice)
        self.add_vat_summary(invoice)
        self.add_final_elements(invoice)

        self.save_xml(root, output_file)

    @staticmethod
    def remove_empty_tag(element: ET.Element, tag: str, tag_name: str) -> None:
        """Remove empty tags from the XML."""

        for parent in element.iterfind(tag):
            for sub_elem in parent.findall('contactInformation'):
                for elem in sub_elem.findall(tag_name):
                    if elem.text is None or len(elem.text.strip()) == 0:
                        parent.remove(sub_elem)

    def add_sender_receiver(self, root):
        elements = [(root, 'sender'), (root, 'receiver')]
        for element in elements:
            self.parent_tag = element[1]
            self.insert_element(*element)

    def add_invoice(self, root):
        return self.create_sub_element(
            root,
            'invoice',
            {
                'documentNumber': self.process_mapping_value(
                    self.mapping['invoice']['documentNumber']
                ),
                'documentDate': self.process_mapping_value(
                    self.mapping['invoice']['documentDate']
                ),
                'schemaVersion': self.mapping['invoice']['schemaVersion'],
                'xmlns': 'urn:netdocs:schemas:document',
            },
        )

    def add_binary_document_attachment(self, invoice):
        # attach_pdf = self.data_cache.get('SEND_METHOD_0')

        # if attach_pdf == ATTACH_PDF:
        self.parent_tag = 'binaryDocumentFormat'

        binary_document = self.create_sub_element(
            invoice,
            'binaryDocumentFormat',
            {
                'name': self.process_mapping_value(
                    self.mapping['binaryDocumentFormat']['name']
                ),
                'contentType': self.mapping['binaryDocumentFormat']['contentType'],
                'xmlns': '',
            },
        )

        self.parent_tag = 'base64Attachment'

        binary_document.text = self.process_mapping_value(
            self.mapping['binaryDocumentAttachment']['content']
        )

    def add_attachments(self, invoice):
        attachments = HandleFiles.list_folder(settings.FOLDER_XML_IN / 'attachments')

        if attachments:
            self.parent_tag = 'binaryDocumentAttachment'

            for attachment in attachments:
                binary_document = self.create_sub_element(
                    invoice,
                    'binaryDocumentAttachment',
                    {
                        'name': attachment.get('file_name'),
                        'contentType': attachment.get('content_type'),
                        'xmlns': '',
                    },
                )
                binary_document.text = Conversions.convert_file_to_base64(
                    settings.FOLDER_XML_IN / 'attachments',
                    f'{attachment.get("file_name")}{attachment.get("suffix")}',
                )

    def add_seller(self, invoice):
        element = (invoice, 'seller')
        self.parent_tag = element[1]
        self.insert_element(*element)

    def add_buyer_billto(self, invoice):
        elements = [(invoice, 'buyer'), (invoice, 'billTo')]
        for element in elements:
            self.parent_tag = element[1]
            self.insert_element(*element)

    def add_saphety_specific_info(self, invoice):
        self.parent_tag = 'saphety'

        additional_date = self.create_sub_element(
            invoice,
            'additionalDate',
            {'type': self.mapping['additionalDate']['type'], 'xmlns': ''},
        )
        additional_date.text = self.process_mapping_value(
            self.mapping['additionalDate']['value']
        )

        cost_center = self.data_cache.get('COST_CENTER_0', '')

        if len(cost_center) > 0:
            self.create_sub_element(
                invoice,
                'reference',
                {'type': 'COSTCENTER', 'referencedDocumentId': cost_center, 'xmlns': ''},
            )

        order = self.data_cache.get('REF_ORDER_0', '')

        if len(order) > 0:
            self.create_sub_element(
                invoice,
                'reference',
                {'type': 'ORDER', 'referencedDocumentId': order, 'xmlns': ''},
            )

        currency_code = self.create_sub_element(
            invoice,
            'currencyCode',
            {'xmlns': ''},
        )
        currency_code.text = self.process_mapping_value(
            self.mapping['currencyCode']['value']
        )

        elements = [(invoice, 'discount')]
        for element in elements:
            self.insert_element(*element)

        comment = self.create_sub_element(
            invoice,
            'comment',
            {'id': self.mapping['comment']['id'], 'xmlns': ''},
        )
        comment.text = self.process_mapping_value(self.mapping['comment']['value'])

    def add_qr_data(self, invoice):
        self.parent_tag = 'qrData'

        sender_software = self.create_sub_element(
            invoice,
            'senderSoftwareCertificationNumber',
            {'xmlns': ''},
        )
        sender_software.text = self.process_mapping_value(
            self.mapping['senderSoftwareCertificationNumber']['value']
        )

        sender_software = self.create_sub_element(
            invoice,
            'senderSoftwareDocumentSignatureHash',
            {'xmlns': ''},
        )
        sender_software.text = self.process_mapping_value(
            self.mapping['senderSoftwareDocumentSignatureHash']['value']
        )

        sender_software = self.create_sub_element(
            invoice,
            'atCud',
            {'xmlns': ''},
        )
        sender_software.text = self.process_mapping_value(self.mapping['atCud']['value'])

        elements = [(invoice, 'qrData')]
        for element in elements:
            self.insert_element(*element)

    def add_line_items(self, invoice):
        self.parent_tag = 'lineItem'

        for index_line, _ in enumerate(self.lines_cache):
            self.line_number = index_line
            self.current_tag = 'lineItem'

            line_item = self.create_sub_element(
                invoice,
                self.current_tag,
                {
                    'number': self.process_mapping_value(
                        self.mapping['lineItem']['number']
                    ),
                    'xmlns': '',
                },
            )

            elements = [
                (line_item, 'sellerItemCode'),
                (line_item, 'description'),
                (line_item, 'quantity'),
                (line_item, 'freeQuantity'),
                (line_item, 'netUnitPrice'),
            ]
            for element in elements:
                self.insert_element(*element)

            self.add_single_element(line_item, 'vatPercentage')

            elements = [
                (line_item, 'vatAmount'),
                (line_item, 'netAmount'),
            ]
            for element in elements:
                self.insert_element(*element)

    def add_vat_summary(self, invoice):
        self.parent_tag = 'lineItem'

        for index_line, _ in enumerate(self.vat_summary_cache):
            self.line_number = index_line
            self.current_tag = 'vatSummary'

            vat_summary = self.create_sub_element(
                invoice,
                'vatSummary',
                self.add_conditional_element(),
            )

            elements = [
                (vat_summary, 'vatPercentage', False, 'vatSummary'),
                (vat_summary, 'vatAmount', False, 'vatSummary'),
                (vat_summary, 'taxableAmount', False, 'vatSummary'),
            ]
            for element in elements:
                self.insert_element(*element)

    def add_final_elements(self, invoice):
        self.parent_tag = 'invoice'

        total = self.create_sub_element(
            invoice,
            'totalVatAmount',
            {'xmlns': ''},
        )
        total.text = self.process_mapping_value(self.mapping['totalVatAmount']['value'])

        total = self.create_sub_element(
            invoice,
            'totalTaxableAmount',
            {'xmlns': ''},
        )
        total.text = self.process_mapping_value(
            self.mapping['totalTaxableAmount']['value']
        )

        total = self.create_sub_element(
            invoice,
            'totalNetAmount',
            {'xmlns': ''},
        )
        total.text = self.process_mapping_value(self.mapping['totalNetAmount']['value'])

        total = self.create_sub_element(
            invoice,
            'totalPayableAmount',
            {'xmlns': ''},
        )
        total.text = self.process_mapping_value(
            self.mapping['totalPayableAmount']['value']
        )

    @staticmethod
    def save_xml(root, output_file):
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"Arquivo XML '{output_file}' gerado com sucesso.")
