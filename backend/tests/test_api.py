""" Tests for API endpoints """

class TestAPI:
    def test_api_import(self):
        from backend.app.api.memory import router
        assert router is not None
        return True