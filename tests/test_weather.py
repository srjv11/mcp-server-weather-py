import sys

sys.path.append("/home/raghu/mcp-server-weather-py")

# Import the weather module to test it can be imported
import src.weather


class TestWeatherModule:
    """Test weather module functionality"""

    def test_weather_module_import(self):
        """Test that weather module can be imported"""
        assert src.weather is not None

    def test_weather_module_has_main_block(self):
        """Test that weather module has main execution block"""
        # Check if the module file contains the main block
        import inspect

        source = inspect.getsource(src.weather)
        assert 'if __name__ == "__main__"' in source
