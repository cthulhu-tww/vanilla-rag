import io
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import pandas as pd
from haystack import logging
from haystack.components.converters import XLSXToDocument
from haystack.dataclasses import ByteStream

logger = logging.getLogger(__name__)


class XLSXToDocumentUpgrade(XLSXToDocument):
    def __init__(self, table_format: Literal["csv", "markdown"] = "csv",
                 sheet_name: Union[str, int, List[Union[str, int]], None] = None,
                 read_excel_kwargs: Optional[Dict[str, Any]] = None,
                 table_format_kwargs: Optional[Dict[str, Any]] = None):
        super().__init__(table_format, sheet_name, read_excel_kwargs, table_format_kwargs)

    def _extract_tables(self, bytestream: ByteStream) -> Tuple[List[str], List[Dict]]:
        """
        Extract tables from a Excel file.
        """
        resolved_read_excel_kwargs = {
            **self.read_excel_kwargs,
            "sheet_name": self.sheet_name,
            "header": None,  # Don't assign any pandas column labels
            "engine": "openpyxl",  # Use openpyxl as the engine to read the Excel file
        }

        try:
            sheet_to_dataframe = pd.read_excel(io=io.BytesIO(bytestream.data), **resolved_read_excel_kwargs)
        except Exception as e:
            resolved_read_excel_kwargs["engine"] = "xlrd"
            sheet_to_dataframe = pd.read_excel(io=io.BytesIO(bytestream.data), **resolved_read_excel_kwargs)

        if isinstance(sheet_to_dataframe, pd.DataFrame):
            sheet_to_dataframe = {self.sheet_name: sheet_to_dataframe}

        updated_sheet_to_dataframe = {}
        for key in sheet_to_dataframe:
            df = sheet_to_dataframe[key]
            # Row starts at 1 in Excel
            df.index = df.index + 1
            # Excel column names are Alphabet Characters
            header = self._generate_excel_column_names(df.shape[1])
            df.columns = header
            updated_sheet_to_dataframe[key] = df

        tables = []
        metadata = []
        for key, value in updated_sheet_to_dataframe.items():
            if self.table_format == "csv":
                resolved_kwargs = {"index": True, "header": True, "lineterminator": "\n", **self.table_format_kwargs}
                tables.append(value.to_csv(**resolved_kwargs))
            else:
                resolved_kwargs = {
                    "index": True,
                    "headers": value.columns,
                    "tablefmt": "pipe",
                    **self.table_format_kwargs,
                }
                # to_markdown uses tabulate
                tables.append(value.to_markdown(**resolved_kwargs))
            # add sheet_name to metadata
            metadata.append({"file_path": ""})
        return tables, metadata
