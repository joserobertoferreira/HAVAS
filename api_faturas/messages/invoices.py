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
                    'DOC_PATH_0',
                    'SALES_SITE_0',
                    'SITE_ADDRESS_0',
                    'BUYER_CODE_0',
                    'INVOICE_ADDR_0',
                    'BUYER_NAME_0',
                    'ADDITIONALDT_0',
                    'COST_CENTER_0',
                    'REF_ORDER_0',
                    'CURRENCY_COD_0',
                    'COMMENT_0',
                ],
                where_clauses={
                    'INVOICE_NUM_0': Condition('=', 'FT-01323/00056').as_tuple()
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

                file_name = (
                    f'{Path(settings.FOLDER_XML_IN) / invoice_number.replace("/", "")}'
                    '.xml'
                )

                # Read QR Code table from Portugal
                qr_code = HandleInvoices.get_qr_code(invoice_type, invoice_number)

                # Read invoice lines
                invoice_lines = HandleInvoices.get_invoice_lines(invoice_number)

                xmlHandler = HandleXML(
                    mapping_file_path,
                    result_query['columns'],
                    record,
                    qr_code,
                    invoice_lines,
                )

                xmlHandler.generate_xml(file_name)

                break

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
