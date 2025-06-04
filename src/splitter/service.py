"""Module for splitting PDF files into individual pages."""

import os
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import List, Optional


logger = logging.getLogger("SPLITTER_SERVICE")


class PDFSplitterService:
    """Service for splitting PDF files into individual pages."""

    def __init__(self, output_base_path: str):
        """
        Initialize the PDFSplitterService with an output path.
        
        Args:
            output_base_path: Base directory where split PDFs will be saved
        """
        self.output_base_path = output_base_path
        
    def split_pdf(self, pdf_path: str, create_subfolder: bool = True) -> List[str]:
        """
        Split a PDF file into individual pages and save each as a separate PDF.
        
        Args:
            pdf_path: Path to the PDF file to split
            create_subfolder: If True, creates a subfolder with the PDF name
            
        Returns:
            List of paths to the created PDF files
        
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF file is invalid or empty
            IOError: If there are issues saving the split files
        """
        # Validate input file
        if not os.path.exists(pdf_path):
            error_msg = f"PDF file {pdf_path} does not exist"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Get PDF filename for folder creation
        pdf_filename = os.path.basename(pdf_path)
        pdf_name = os.path.splitext(pdf_filename)[0]
        
        try:
            # Open the PDF document
            logger.info(f"Opening PDF document: {pdf_path}")
            doc = fitz.open(pdf_path)
            
            # Check if PDF is empty
            if len(doc) == 0:
                error_msg = f"PDF file {pdf_path} has no pages"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Create output directory
            output_dir = self.output_base_path
            if create_subfolder:
                output_dir = os.path.join(self.output_base_path, pdf_name)
                
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Output directory: {output_dir}")
            
            created_files = []
            
            # Process each page
            for page_num in range(len(doc)):
                # Create a new PDF with just this page
                output_doc = fitz.open()
                output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # Create output filename
                output_filename = f"{pdf_name}_page_{page_num+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save the new PDF
                logger.info(f"Saving page {page_num+1} to {output_path}")
                output_doc.save(output_path)
                output_doc.close()
                
                created_files.append(output_path)
            
            # Close the original document
            doc.close()
            
            logger.info(f"Successfully split {pdf_path} into {len(created_files)} files")
            return created_files
            
        except fitz.FileDataError as e:
            error_msg = f"Invalid PDF file {pdf_path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except IOError as e:
            error_msg = f"Error saving split PDF files: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error when splitting PDF {pdf_path}: {str(e)}"
            logger.error(error_msg)
            raise
    
    def split_pdfs_in_directory(self, directory_path: str, recursive: bool = False) -> dict:
        """
        Split all PDF files in a directory into individual pages.
        
        Args:
            directory_path: Path to directory containing PDFs
            recursive: If True, process PDFs in subdirectories
            
        Returns:
            Dictionary mapping source PDF paths to lists of created file paths
        """
        if not os.path.exists(directory_path):
            error_msg = f"Directory {directory_path} does not exist"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        result = {}
        
        # Determine the pattern for PDF search
        pattern = "**/*.pdf" if recursive else "*.pdf"
        
        # Find all PDFs in the directory
        pdf_files = list(Path(directory_path).glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        # Process each PDF
        for pdf_path in pdf_files:
            try:
                pdf_str_path = str(pdf_path)
                result[pdf_str_path] = self.split_pdf(pdf_str_path)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")
                result[str(pdf_path)] = None
                
        return result