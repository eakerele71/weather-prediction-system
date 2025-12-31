"""Unit tests for Gemini LLM integration"""
import pytest
from datetime import datetime, date, timedelta
from app.services.gemini_integration import (
    GeminiClient,
    PromptBuilder,
    ResponseParser,
    WeatherContext
)
from app.models import WeatherData, Forecast, Location


@pytest.fixture
def sample_location():
    """Sample location for testing"""
    return Location(
        latitude=47.6062,
        longitude=-122.3321,
        city="Seattle",
        country="United States"
    )


@pytest.fixture
def sample_weather_data(sample_location):
    """Sample weather data for testing"""
    return WeatherData(
        location=sample_location,
        timestamp=datetime.now(),
        temperature=15.5,
        humidity=65.0,
        pressure=1013.25,
        wind_speed=5.2,
        wind_direction=180.0,
        precipitation=0.0,
        cloud_cover=40.0,
        weather_condition="Partly Cloudy"
    )


@pytest.fixture
def sample_forecasts(sample_location):
    """Sample forecast list for testing"""
    forecasts = []
    base_date = date.today()
    
    for i in range(7):
        forecast = Forecast(
            location=sample_location,
            forecast_date=base_date + timedelta(days=i+1),
            predicted_temperature_high=20.0 + i,
            predicted_temperature_low=10.0 + i * 0.5,
            precipitation_probability=0.3 + i * 0.05,
            weather_condition="Sunny" if i < 3 else "Cloudy",
            confidence_score=0.85 - i * 0.02,
            generated_at=datetime.now()
        )
        forecasts.append(forecast)
    
    return forecasts


class TestPromptBuilder:
    """Test cases for PromptBuilder"""
    
    def test_initialization(self):
        """Test PromptBuilder initialization"""
        builder = PromptBuilder()
        assert builder is not None

    def test_build_forecast_summary_prompt(self, sample_forecasts):
        """Test building forecast summary prompt"""
        builder = PromptBuilder()
        prompt = builder.build_forecast_summary_prompt(sample_forecasts)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Seattle" in prompt
        assert "forecast" in prompt.lower()
        
        # Check that forecast details are included
        for forecast in sample_forecasts[:3]:
            assert str(forecast.forecast_date) in prompt

    def test_build_forecast_summary_prompt_empty_list(self):
        """Test building prompt with empty forecast list"""
        builder = PromptBuilder()
        prompt = builder.build_forecast_summary_prompt([])
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_weather_explanation_prompt(self, sample_weather_data, sample_forecasts):
        """Test building weather explanation prompt"""
        builder = PromptBuilder()
        prompt = builder.build_weather_explanation_prompt(
            sample_weather_data,
            sample_forecasts[0]
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Seattle" in prompt
        assert str(sample_weather_data.temperature) in prompt
        assert "explain" in prompt.lower()

    def test_build_question_answer_prompt_with_full_context(
        self, 
        sample_location,
        sample_weather_data,
        sample_forecasts
    ):
        """Test building Q&A prompt with full context"""
        builder = PromptBuilder()
        context = WeatherContext(
            location=sample_location,
            current_weather=sample_weather_data,
            forecasts=sample_forecasts
        )
        
        question = "Will it rain tomorrow?"
        prompt = builder.build_question_answer_prompt(question, context)
        
        assert isinstance(prompt, str)
        assert question in prompt
        assert "Seattle" in prompt
        assert "Context:" in prompt

    def test_build_question_answer_prompt_minimal_context(self):
        """Test building Q&A prompt with minimal context"""
        builder = PromptBuilder()
        context = WeatherContext()
        
        question = "What's the weather like?"
        prompt = builder.build_question_answer_prompt(question, context)
        
        assert isinstance(prompt, str)
        assert question in prompt


class TestResponseParser:
    """Test cases for ResponseParser"""
    
    def test_initialization(self):
        """Test ResponseParser initialization"""
        parser = ResponseParser()
        assert parser is not None

    def test_parse_summary_response(self):
        """Test parsing summary response"""
        parser = ResponseParser()
        raw_response = "**Weather Summary:** The week ahead looks sunny with mild temperatures."
        
        parsed = parser.parse_summary_response(raw_response)
        
        assert isinstance(parsed, str)
        assert "**" not in parsed  # Markdown removed
        assert "sunny" in parsed.lower()

    def test_parse_summary_response_clean_text(self):
        """Test parsing already clean summary"""
        parser = ResponseParser()
        raw_response = "Clear skies expected throughout the week."
        
        parsed = parser.parse_summary_response(raw_response)
        
        assert parsed == raw_response

    def test_parse_explanation_response(self):
        """Test parsing explanation response"""
        parser = ResponseParser()
        raw_response = "The weather is influenced by *high pressure* systems."
        
        parsed = parser.parse_explanation_response(raw_response)
        
        assert isinstance(parsed, str)
        assert "*" not in parsed

    def test_parse_answer_response(self):
        """Test parsing answer response"""
        parser = ResponseParser()
        raw_response = "Yes, rain is expected tomorrow afternoon."
        
        parsed = parser.parse_answer_response(raw_response)
        
        assert isinstance(parsed, str)
        assert "rain" in parsed.lower()


class TestGeminiClient:
    """Test cases for GeminiClient"""
    
    def test_initialization_with_api_key(self):
        """Test GeminiClient initialization with API key"""
        client = GeminiClient(api_key="test_key_123")
        
        assert client is not None
        assert client.api_key == "test_key_123"
        assert client.prompt_builder is not None
        assert client.response_parser is not None

    def test_initialization_without_api_key(self):
        """Test GeminiClient initialization without API key"""
        client = GeminiClient()
        
        assert client is not None
        # API key may be None if not in environment

    def test_generate_forecast_summary(self, sample_forecasts):
        """Test generating forecast summary"""
        client = GeminiClient(api_key="test_key")
        
        summary = client.generate_forecast_summary(sample_forecasts)
        
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_generate_forecast_summary_empty_list(self):
        """Test generating summary with empty forecast list"""
        client = GeminiClient(api_key="test_key")
        
        summary = client.generate_forecast_summary([])
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should return fallback response

    def test_explain_weather_pattern(self, sample_weather_data, sample_forecasts):
        """Test explaining weather pattern"""
        client = GeminiClient(api_key="test_key")
        
        explanation = client.explain_weather_pattern(
            sample_weather_data,
            sample_forecasts[0]
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    def test_answer_question(self, sample_location):
        """Test answering user question"""
        client = GeminiClient(api_key="test_key")
        context = WeatherContext(location=sample_location)
        
        answer = client.answer_question("Will it be sunny tomorrow?", context)
        
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_answer_question_empty_context(self):
        """Test answering question with empty context"""
        client = GeminiClient(api_key="test_key")
        context = WeatherContext()
        
        answer = client.answer_question("What's the weather?", context)
        
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_handle_rate_limit(self):
        """Test rate limit handling"""
        client = GeminiClient(api_key="test_key")
        
        status = client.handle_rate_limit()
        
        assert isinstance(status, dict)
        assert 'rate_limited' in status
        assert 'queue_size' in status
        assert 'message' in status

    def test_get_client_info(self):
        """Test getting client information"""
        client = GeminiClient(api_key="test_key")
        
        info = client.get_client_info()
        
        assert isinstance(info, dict)
        assert 'api_key_configured' in info
        assert 'rate_limit' in info
        assert 'queue_size' in info
        assert info['api_key_configured'] is True

    def test_get_client_info_no_api_key(self):
        """Test client info when no API key configured"""
        client = GeminiClient(api_key=None)
        
        info = client.get_client_info()
        
        assert info['api_key_configured'] is False

    def test_fallback_responses_exist(self):
        """Test that fallback responses are configured"""
        client = GeminiClient()
        
        assert 'summary' in client.fallback_responses
        assert 'explanation' in client.fallback_responses
        assert 'answer' in client.fallback_responses
        
        # Verify fallback responses are non-empty
        for key, value in client.fallback_responses.items():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_request_queue_initialization(self):
        """Test request queue is initialized"""
        client = GeminiClient()
        
        assert isinstance(client.request_queue, list)
        assert len(client.request_queue) == 0

    def test_simulated_api_calls(self, sample_forecasts):
        """Test that simulated API calls work without real API key"""
        client = GeminiClient(api_key=None)
        
        # Should use fallback/simulated responses
        summary = client.generate_forecast_summary(sample_forecasts)
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestWeatherContext:
    """Test cases for WeatherContext"""
    
    def test_weather_context_creation(self, sample_location, sample_weather_data):
        """Test creating WeatherContext"""
        context = WeatherContext(
            location=sample_location,
            current_weather=sample_weather_data
        )
        
        assert context.location == sample_location
        assert context.current_weather == sample_weather_data
        assert context.forecasts is None
        assert context.historical_data is None

    def test_weather_context_empty(self):
        """Test creating empty WeatherContext"""
        context = WeatherContext()
        
        assert context.location is None
        assert context.current_weather is None
        assert context.forecasts is None
        assert context.historical_data is None
