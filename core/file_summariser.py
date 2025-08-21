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
# GPT integration (optional)
try:
    from gpt import GPTHandler
except Exception:
    GPTHandler = None


class FileSummariser:
    def __init__(self):
        self.uploaded_files = []
        self.processed_files = {}

        # File size limits (configured in GB, computed to bytes)
        self.MIN_FILE_SIZE_GB = 0.000001  # ~1 KB
        self.MAX_FILE_SIZE_GB = 0.05      # ~50 MB
        self.MIN_FILE_SIZE = int(self.MIN_FILE_SIZE_GB * (1024 ** 3))
        self.MAX_FILE_SIZE = int(self.MAX_FILE_SIZE_GB * (1024 ** 3))

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
                return False, (
                    f"File is too small. Minimum size: {self.MIN_FILE_SIZE_GB:.9f} GB "
                    f"(~{self.MIN_FILE_SIZE/1024:.1f} KB)"
                )

            if file_size > self.MAX_FILE_SIZE:
                return False, (
                    f"File is too large. Maximum size: {self.MAX_FILE_SIZE_GB:.3f} GB "
                    f"(~{self.MAX_FILE_SIZE/(1024*1024):.1f} MB)"
                )

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

    # ---------------- Summarization helpers (GPT-backed with fallbacks) ----------------
    def summarise(self, file_path: str, instruction: str = "Provide a general summary") -> Dict:
        """
        Summarise a single file according to instruction.
        Returns dict: { success, message, summary, kind }
        """
        try:
            # Validate the file first
            ok, emsg = self.validate_file(file_path)
            if not ok:
                return { 'success': False, 'message': emsg, 'summary': '', 'kind': 'error' }

            text = self.extract_text_content(file_path) or ''
            if not text.strip():
                return { 'success': False, 'message': 'No textual content could be extracted from the file.', 'summary': '', 'kind': 'error' }

            kind = self._detect_request_kind(instruction)
            prompt = self._build_prompt(kind, instruction, Path(file_path).name)

            # Use GPT if available with a dedicated summariser; else fallback to heuristic short summary
            summary = None
            if GPTHandler:
                try:
                    gpt = GPTHandler()
                    # Larger context slice to help GPT, but keep a cap for tokens
                    content_slice = text[:20000]
                    summary = gpt.summarize(content_slice, instruction, kind, Path(file_path).name, max_tokens=900, temperature=0.5)
                    # Robust failure filtering: treat apologies/errors as failure
                    if summary and isinstance(summary, str):
                        s_low = summary.lower()
                        blocked = [
                            "don't have access to gpt",
                            "openai integration is not available",
                            "i'm having trouble processing",
                            "couldn't process",
                            "error",
                            "api configuration"
                        ]
                        if any(b in s_low for b in blocked):
                            summary = None
                except Exception as e:
                    print(f"GPT summarisation failed: {e}")
                    summary = None

            if not summary or not str(summary).strip():
                summary = self._fallback_summary(text, kind)

            return { 'success': True, 'message': 'Summary completed successfully.', 'summary': str(summary).strip(), 'kind': kind }
        except Exception as e:
            return { 'success': False, 'message': f'Error during summarisation: {e}', 'summary': '', 'kind': 'error' }

    def _detect_request_kind(self, instruction: str) -> str:
        s = (instruction or '').lower()
        if any(k in s for k in ["timeline", "chronology", "chronological", "sequence of events"]):
            return 'timeline'
        if any(k in s for k in ["highlight", "key points", "keypoints", "keywords", "names", "dates", "figures", "topics"]):
            return 'highlights'
        if any(k in s for k in ["code", "function", "class", "method", "variable", "algorithm"]):
            return 'code'
        return 'general'

    def _build_prompt(self, kind: str, instruction: str, filename: str) -> str:
        base = (
            "You are DeskPilot, an assistant that summarises files for the user (address them as 'sir').\n"
            f"File: {filename}. Keep it concise and structured."
        )
        if kind == 'timeline':
            extra = "Create a clear chronological timeline of events as bullet points with timestamps/dates if present."
        elif kind == 'highlights':
            extra = (
                "Extract highlights: top keywords, named people/organizations, dates, figures, and most discussed topics. "
                "Return as concise sections with short bullet points."
            )
        elif kind == 'code':
            extra = (
                "Summarise code: describe the overall purpose, list key functions/classes and explain what important lines/blocks do. "
                "Point out any potential issues or noteworthy patterns."
            )
        else:
            extra = "Provide a short, helpful summary."
        if instruction and instruction.strip():
            extra += f"\nThe user additionally requested: {instruction.strip()}"
        return base + "\n\n" + extra

    def _fallback_summary(self, text: str, kind: str) -> str:
        # Very basic, offline fallback
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        head = lines[:10]
        if kind == 'timeline':
            return "Timeline (approximate):\n- " + "\n- ".join(head[:8])
        if kind == 'highlights':
            # Simulate highlights by common words
            import re, collections
            words = re.findall(r"[A-Za-z]{4,}", text.lower())
            common = [w for w, _ in collections.Counter(words).most_common(8)]
            return (
                "Highlights:\n- Keywords: " + ", ".join(common) +
                "\n- Top lines:\n- " + "\n- ".join(head[:5])
            )
        if kind == 'code':
            return (
                "Code Summary (basic):\n- Purpose: Derived from top comments/first lines.\n- Notable parts:\n- " + "\n- ".join(head[:8])
            )
        # general
        return "Summary:\n- " + "\n- ".join(head[:8])
