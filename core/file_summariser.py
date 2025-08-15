# Logic to parse & summarise files
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import PyPDF2
import docx
import pandas as pd

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import SUPPORTED_FILE_TYPES, DEFAULT_SUMMARY_LENGTH


class FileSummariser:
    def __init__(self):
        self.uploaded_files = []
        self.processed_files = {}

        # File size limits (in bytes)
        self.MIN_FILE_SIZE = 1024  # 1 KB minimum
        self.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB maximum

        # Content length limits (in characters)
        self.MIN_CONTENT_LENGTH = 100  # Minimum 100 characters
        self.MAX_CONTENT_LENGTH = 1000000  # Maximum ~1M characters

    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if the file meets our criteria
        Returns: (is_valid, error_message)
        """
        try:
            file_path_obj = Path(file_path)

            # Check if file exists
            if not file_path_obj.exists():
                return False, "File does not exist."

            # Check file extension
            if file_path_obj.suffix.lower() not in SUPPORTED_FILE_TYPES:
                return False, f"Unsupported file type. Supported types: {', '.join(SUPPORTED_FILE_TYPES)}"

            # Check file size
            file_size = file_path_obj.stat().st_size
            if file_size < self.MIN_FILE_SIZE:
                return False, f"File is too small. Minimum size: {self.MIN_FILE_SIZE / 1024:.1f} KB"

            if file_size > self.MAX_FILE_SIZE:
                return False, f"File is too large. Maximum size: {self.MAX_FILE_SIZE / (1024 * 1024):.1f} MB"

            # Try to read and validate content
            content = self.extract_text_content(file_path)
            if not content:
                return False, "Could not extract text content from file."

            content_length = len(content.strip())
            if content_length < self.MIN_CONTENT_LENGTH:
                return False, f"File content is too short. Minimum content: {self.MIN_CONTENT_LENGTH} characters"

            if content_length > self.MAX_CONTENT_LENGTH:
                return False, f"File content is too long. Maximum content: {self.MAX_CONTENT_LENGTH / 1000:.0f}K characters"

            return True, "File is valid."

        except Exception as e:
            return False, f"Error validating file: {str(e)}"

    def extract_text_content(self, file_path: str) -> Optional[str]:
        """
        Extract text content from supported file types
        Returns the extracted text or None if extraction fails
        """
        try:
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()

            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension == '.docx':
                return self._extract_docx_text(file_path)
            elif file_extension == '.csv':
                return self._extract_csv_text(file_path)
            elif file_extension == '.txt':
                return self._extract_txt_text(file_path)
            else:
                return None

        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text.strip()

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return "\n".join(text).strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text representation from CSV file"""
        try:
            # Read CSV and convert to string representation
            df = pd.read_csv(file_path)

            # Create a text representation
            text = f"CSV File with {len(df)} rows and {len(df.columns)} columns.\n\n"
            text += f"Columns: {', '.join(df.columns.tolist())}\n\n"

            # Add first few rows as sample
            sample_size = min(10, len(df))
            text += f"Sample data (first {sample_size} rows):\n"
            text += df.head(sample_size).to_string()

            # Add basic statistics if numeric columns exist
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                text += f"\n\nBasic statistics for numeric columns:\n"
                text += df[numeric_cols].describe().to_string()

            return text
        except Exception as e:
            raise Exception(f"Error reading CSV: {str(e)}")

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                raise Exception(f"Error reading TXT file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")

    def add_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Add a file to the processing list after validation
        Returns: (success, message)
        """
        # Validate file
        is_valid, message = self.validate_file(file_path)
        if not is_valid:
            return False, message

        # Check if already added
        if file_path in self.uploaded_files:
            return False, "File is already in the upload list."

        # Add to list
        self.uploaded_files.append(file_path)
        return True, f"File '{Path(file_path).name}' added successfully."

    def remove_file(self, file_path: str) -> bool:
        """Remove file from upload list"""
        if file_path in self.uploaded_files:
            self.uploaded_files.remove(file_path)
            # Also remove from processed files if it exists
            if file_path in self.processed_files:
                del self.processed_files[file_path]
            return True
        return False

    def get_uploaded_files(self) -> List[str]:
        """Get list of currently uploaded files"""
        return self.uploaded_files.copy()

    def clear_all_files(self):
        """Clear all uploaded and processed files"""
        self.uploaded_files.clear()
        self.processed_files.clear()

    def get_file_info(self, file_path: str) -> Dict:
        """Get information about a file"""
        try:
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size

            # Get content length
            content = self.extract_text_content(file_path)
            content_length = len(content) if content else 0

            return {
                'name': file_path_obj.name,
                'path': str(file_path_obj),
                'size_bytes': file_size,
                'size_readable': self._format_file_size(file_size),
                'extension': file_path_obj.suffix.lower(),
                'content_length': content_length,
                'is_valid': self.validate_file(file_path)[0]
            }
        except Exception as e:
            return {
                'name': Path(file_path).name,
                'path': file_path,
                'error': str(e),
                'is_valid': False
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"