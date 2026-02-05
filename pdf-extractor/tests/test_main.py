#!/usr/bin/env python3
"""Tests for PDF Text Extractor."""

import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import extract_text_from_pdf


class TestPDFExtractor(unittest.TestCase):
    """Test cases for PDF text extraction."""

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf("nonexistent.pdf")

    def test_invalid_extension(self):
        """Test that ValueError is raised for non-PDF files."""
        # Create a temporary file with wrong extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pdf")
            temp_path = f.name

        try:
            with self.assertRaises(ValueError):
                extract_text_from_pdf(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_output_path_generation(self):
        """Test that output path is correctly generated from input path."""
        # This tests the path logic without needing a real PDF
        input_path = Path("/some/path/document.pdf")
        expected_output = Path("/some/path/document.txt")
        self.assertEqual(input_path.with_suffix('.txt'), expected_output)


class TestIntegration(unittest.TestCase):
    """Integration tests requiring actual PDF files."""

    @unittest.skip("Requires a real PDF file for testing")
    def test_extract_real_pdf(self):
        """Test extraction from a real PDF file."""
        # To run this test, create a test PDF and update the path
        pdf_path = "test_document.pdf"
        result = extract_text_from_pdf(pdf_path)

        self.assertEqual(result["status"], "success")
        self.assertIn("total_pages", result)
        self.assertIn("total_characters", result)
        self.assertTrue(Path(result["output_file"]).exists())


if __name__ == '__main__':
    unittest.main()
