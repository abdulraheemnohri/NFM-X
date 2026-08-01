""" Tests for OCR module """

class TestOCR:
    def test_language_detection(self):
        from backend.app.ocr.language_detection import detect_language
        result = detect_language("Hello")
        assert "language" in result
        return True