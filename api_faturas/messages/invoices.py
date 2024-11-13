from pathlib import Path
from typing import Any, Dict

from config import settings
from database.database import Condition, DatabaseConnection
from utils.xml.handle_xml import HandleXML


class HandleInvoices:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_invoices() -> None:
        result_query = {}

        # Connect to the database
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            # Execute query to get the invoices to be processed
            result_query = db.execute_query(
                table=f'{settings.DB_SCHEMA}.ZVWSAPHSIV',
                columns=[
                    'INVOICE_TYP_0',
                    'INVOICE_NUM_0',
                    'COMPANY_0',
                    'SELLER_NAME_0',
                    'SELL_SOCCAP_0',
                    'SELLER_COMM_0',
                    'TYPE_COD_SEL_0',
                    'SELLER_CODE_0',
                    'COMPANY_CRY_0',
                    'TYPE_COD_REC_0',
                    'RECEIVER_COD_0',
                    'INVOICE_CRY_0',
                    'INVOICE_DATE_0',
                    'SEND_METHOD_0',
                    'ATT_PATH_0',
                    'PDF_FILE_0',
                    'SALES_SITE_0',
                    'SITE_ADDRESS_0',
                    'BUYER_CODE_0',
                    'BUYER_ADDR_0',
                    'BUYER_NAME_0',
                    'BUYER_VAT_0',
                    'ADDITIONALDT_0',
                    'COST_CENTER_0',
                    'REF_ORDER_0',
                    'CURRENCY_COD_0',
                    'COMMENT_0',
                    'TOT_VAT_AMT_0',
                    'TOT_TAX_AMT_0',
                    'TOTAL_AMOUNT_0',
                ],
                where_clauses={
                    'INVOICE_NUM_0': Condition('=', 'FT-01324/00008').as_tuple()
                },
            )

        # Check if the query was successful
        if result_query['status'] == 'success':
            # Get the path of the json mapping file
            mapping_file_path = Path(settings.BASE_DIR / 'mapping_xml.json')

            # Process the invoices
            result_data = result_query['data']
            # result_data: DataFrame = result_query['data'] - Pandas

            # Extract the columns headers from the dataframe - Pandas
            # result_headers = result_data.columns.tolist()

            # for row in result_data.itertuples(index=False): - Pandas
            #     file_name = (
            #         Path(settings.FOLDER_XML_IN) / str(row.INVOICE_NUM_0).replace('/', '')  # noqa: E501
            #         + '.xml'
            #     )

            #     # Read QR Code table from Portugal
            #     qr_code = HandleInvoices.get_qr_code(
            #         str(row.INVOICE_TYP_0), str(row.INVOICE_NUM_0)
            #     )

            #     # Read invoice lines
            #     invoice_lines = HandleInvoices.get_invoice_lines(str(row.INVOICE_NUM_0))

            #     xmlHandler = HandleXML(
            #         mapping_file_path,
            #         result_headers,
            #         row._asdict(),
            #         qr_code,
            #         invoice_lines,
            #     )

            # Loop through the invoices
            for record in result_data:
                invoice_number = str(record.get('INVOICE_NUM_0', ''))
                invoice_type = str(record.get('INVOICE_TYP_0', 'FT'))
                seller = str(record.get('SALES_SITE_0', ''))
                seller_address = str(record.get('SITE_ADDRESS_0', ''))
                buyer = str(record.get('BUYER_CODE_0', ''))
                buyer_address = str(record.get('BUYER_ADDR_0', ''))

                file_name = (
                    f'{Path(settings.FOLDER_XML_IN) / invoice_number.replace("/", "")}'
                    '.xml'
                )

                # Read QR Code table from Portugal
                qr_code = HandleInvoices.get_qr_code(invoice_type, invoice_number)

                # Read invoice lines
                invoice_lines = HandleInvoices.get_invoice_lines(invoice_number)

                # Read VAT summary table
                vat_summary = HandleInvoices.get_vat_summary(invoice_number)

                # Read the addresses referenced in the invoice
                seller_address = HandleInvoices.get_addresses(
                    parameters=[
                        {
                            'address_type': 3,
                            'entity': seller,
                            'address': seller_address,
                        },
                        {
                            'address_type': 1,
                            'entity': buyer,
                            'address': buyer_address,
                        },
                    ]
                )

                # Generate the XML file for the invoice
                xml_parameters = {
                    'mapping_file_path': mapping_file_path,
                    'field_headers': result_query['columns'],
                    'db_record': record,
                    'db_qrcode': qr_code,
                    'db_lines': invoice_lines,
                    'db_vat_summary': vat_summary,
                    'db_addresses': seller_address,
                }

                xmlHandler = HandleXML(**xml_parameters)

                xmlHandler.generate_xml(file_name)

                break

    def get_addresses(**kwargs) -> Dict[str, Any]:
        """This method receives a list of dictionaries with the data to be searched in the
        address table and returns the fields to be used in the XML"""

        parameters = kwargs.get('parameters', [])

        if not all(isinstance(parameter, dict) for parameter in parameters):
            raise TypeError('All values must be dictionaries')

        return_list = []
        result_query = {}

        for parameter in parameters:
            address_type = parameter.get('address_type', 1)
            entity = parameter.get('entity', '')
            address = parameter.get('address', '')

            # Connect to the database
            with DatabaseConnection(
                settings.DB_SERVER,
                settings.DB_DATABASE,
                settings.DB_USERNAME,
                settings.DB_PASSWORD,
            ) as db:
                # Execute query to get the addresses
                result_query = db.execute_query(
                    table=f'{settings.DB_SCHEMA}.BPADDRESS',
                    columns=[
                        'BPATYP_0',
                        'BPAADDLIG_0',
                        'BPAADDLIG_1',
                        'BPAADDLIG_2',
                        'POSCOD_0',
                        'CTY_0',
                        'CRY_0',
                        'TEL_0',
                        'FAX_0',
                        'WEB_0',
                    ],
                    where_clauses={
                        'BPATYP_0': Condition('=', address_type).as_tuple(),
                        'BPANUM_0': Condition('=', entity).as_tuple(),
                        'BPAADD_0': Condition('=', address).as_tuple(),
                    },
                )

            # Check if the query was successful
            if result_query['status'] == 'success':
                result_list = result_query['data']

                if result_list:
                    return_list.append(result_list.pop())

        return return_list

    @staticmethod
    def get_qr_code(invoice_type: str, invoice_number: str) -> Dict[str, Any]:
        result_query = {}

        # Connect to the database
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            # Execute query to get the invoices to be processed
            result_query = db.execute_query(
                table=f'{settings.DB_SCHEMA}.PORQRC',
                columns=[
                    'DOCNUM_0',
                    'QRC_R_0',
                    'QRC_Q_0',
                    'QRC_H_0',
                    'STRQRC_0',
                    'IMGQRC_0',
                ],
                where_clauses={
                    'DOCTYP_0': Condition('=', invoice_type).as_tuple(),
                    'DOCNUM_0': Condition('=', invoice_number).as_tuple(),
                },
            )

        # Check if the query was successful
        if result_query['status'] == 'success':
            return result_query['data']

        return {}

    @staticmethod
    def get_invoice_lines(invoice_number: str) -> Dict[str, Any]:
        result_query = {}

        # Connect to the database
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            # Execute query to get the invoices to be processed
            result_query = db.execute_query(
                table=f'{settings.DB_SCHEMA}.ZVWSAPHSID',
                columns=[
                    'INVOICE_NUM_0',
                    'LINE_NUMBER_0',
                    'LINE_PRODUCT_0',
                    'LINE_DESCR_0',
                    'LINE_QUANT_0',
                    'LINE_UNIT_0',
                    'LINE_UNIT_PR_0',
                    'LINE_VAT_AMT_0',
                    'LINE_NET_AMT_0',
                    'VAT_PERCENT_0',
                    'VAT_REA_CODE_0',
                    'VAT_REASON_0',
                ],
                where_clauses={
                    'INVOICE_NUM_0': Condition('=', invoice_number).as_tuple(),
                },
            )

        # Check if the query was successful
        if result_query['status'] == 'success':
            return result_query['data']

        return {}

    @staticmethod
    def get_vat_summary(invoice_number: str) -> Dict[str, Any]:
        result_query = {}

        # Connect to the database
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            # Execute query to get the invoices to be processed
            result_query = db.execute_query(
                table=f'{settings.DB_SCHEMA}.ZVWSAPHSVV',
                columns=[
                    'INVOICE_NUM_0',
                    'VAT_CODE_0',
                    'VAT_PERCENT_0',
                    'VAT_AMOUNT_0',
                    'TAXABLE_AMT_0',
                    'VAT_REA_CODE_0',
                    'VAT_REASON_0',
                ],
                where_clauses={
                    'INVOICE_NUM_0': Condition('=', invoice_number).as_tuple(),
                },
            )

        # Check if the query was successful
        if result_query['status'] == 'success':
            return result_query['data']

        return {}
