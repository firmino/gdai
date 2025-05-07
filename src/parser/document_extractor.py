import os
from abc import ABC, abstractmethod
from collections import defaultdict
from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from src.parser.schema import Table, Image, Text, Document


class DocumentExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def extract_document_data(document_path: str) -> dict:
        """
        Extract text from a document.
        """
        pass

    @abstractmethod
    def _format_output(dict):
        pass


class DoclingPDFExtractor(DocumentExtractor):
    """
    Extract text from a document using Docling.
    """

    def __init__(self):
        super().__init__()

        # create a DocumentConverter instance   without ocr
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # pick what you need
        pipeline_options.generate_page_images = True
        pipeline_options.do_table_structure = True  # pick what you need
        self.docling_extractor_without_ocr = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)  # switch to beta PDF backend
            }
        )

        # create a DocumentConverter instance   with ocr
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # pick what you need
        pipeline_options.generate_page_images = True
        pipeline_options.do_table_structure = True  # pick what you need
        self.docling_extractor_with_ocr = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)  # switch to beta PDF backend
            }
        )

    def extract_document_data(self, document_path: str) -> dict:
        """
        Extract text from a document.
        """
        # check if the document exists  
        if not os.path.exists(document_path):
            raise ValueError

        # first try to extract text without OCR
        result = self.docling_extractor_without_ocr.convert(document_path)
        dict_result = result.document.export_to_dict()

        # if method without ocr fails, try with ocr
        if len(dict_result["texts"]) == 0:
            result = self.docling_extractor_with_ocr.convert(document_path)
            dict_result = result.document.export_to_dict()

        # format the output to a Document object    
        document = self._format_output(dict_result)

        return document 

    def _format_output(self, dict_result) -> Document:
        # extract tables, images and text
        tables = self._extract_tables(dict_result['tables'])
        images = self._extract_images(dict_result['pictures'])
        pages_text = self._extract_text(dict_result['texts'])

        # create a Document object
        doc = Document(
            doc_name="doc_name",
            texts=pages_text,
            tables=tables,
            images=images,
        )
        return doc

    def _extract_tables(self, raw_result) -> list[Table]:
        return None

    def _extract_images(self, raw_result) -> list[Image]:
        return None

    def _extract_text(self, text_result) -> list[Text]: 
        # extract text from docling result to a dictionary
        text_found = [ (text_item['prov'][0]['page_no'], text_item['text']  ) for text_item in text_result ] 

        # group text by page number
        page_data = defaultdict(str) 
        for page_number, page_text in text_found:
            page_data[page_number] += (" " + page_text) if page_data[page_number] else page_text
        # create a list of Page objects     
        pages = [Text(page=page, text=text) for page, text in page_data.items()] 
        return pages   


