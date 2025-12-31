"""Property-based tests for Gemini LLM integration"""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, date, timedelta
from app.services.gemini_integration import (
    GeminiClient,
    PromptBuilder,
    ResponseParser,
    WeatherContext
)
from app.models import WeatherData, Forecast, Location


# Custom strategies for generating test data
@st.composite
def location_strategy(draw):
    """Generate valid Location objects"""
    return Location(
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        city=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        country=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    )


@st.composite
def weather_data_strategy(draw, location=None):
    """Generate valid WeatherData objects"""
    if location is None:
        location = draw(location_strategy())
    
    return WeatherData(
        location=location,
        timestamp=datetime.now() + timedelta(days=draw(st.integers(min_value=0, max_value=30))),
        temperature=draw(st.floats(min_value=-50, max_value=50)),
        humidity=draw(st.floats(min_value=0, max_value=100)),
        pressure=draw(st.floats(min_value=900, max_value=1100)),
        wind_speed=draw(st.floats(min_value=0, max_value=50)),
        wind_direction=draw(st.floats(min_value=0, max_value=360)),
        precipitation=draw(st.floats(min_value=0, max_value=100)),
        cloud_cover=draw(st.floats(min_value=0, max_value=100)),
        weather_condition=draw(st.sampled_from(['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Partly Cloudy']))
    )


@st.composite
def forecast_strategy(draw, location=None):
    """Generate valid Forecast objects"""
    if location is None:
        location = draw(location_strategy())
    
    temp_low = draw(st.floats(min_value=-50, max_value=40))
    temp_high = temp_low + draw(st.floats(min_value=0, max_value=20))
    
    return Forecast(
        location=location,
        forecast_date=date.today() + timedelta(days=draw(st.integers(min_value=1, max_value=7))),
        predicted_temperature_high=temp_high,
        predicted_temperature_low=temp_low,
        precipitation_probability=draw(st.floats(min_value=0, max_value=1)),
        weather_condition=draw(st.sampled_from(['Clear', 'Cloudy', 'Rainy', 'Snowy', 'Sunny'])),
        confidence_score=draw(st.floats(min_value=0, max_value=1)),
        generated_at=datetime.now()
    )


# Feature: weather-prediction-system, Property 8: Gemini Summary Generation
@given(st.lists(forecast_strategy(), min_size=1, max_size=7))
def test_gemini_summary_generation_property(forecasts):
    """
    Property 8: Gemini Summary Generation
    For any valid forecast input, the Gemini_Integration should return 
    a non-empty natural language summary.
    
    Validates: Requirements 6.1
    """
    client = GeminiClient(api_key="test_key")
    
    summary = client.generate_forecast_summary(forecasts)
    
    # Verify summary is non-empty string
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(summary.strip()) > 0


# Feature: weather-prediction-system, Property 8: Gemini Summary Generation (Empty Input)
@given(st.just([]))
def test_gemini_summary_generation_empty_input_property(empty_forecasts):
    """
    Property 8: Gemini Summary Generation (Empty Input)
    For empty forecast input, should return fallback summary.
    
    Validates: Requirements 6.1
    """
    client = GeminiClient(api_key="test_key")
    
    summary = client.generate_forecast_summary(empty_forecasts)
    
    # Should still return non-empty fallback
    assert isinstance(summary, str)
    assert len(summary) > 0


# Feature: weather-prediction-system, Property 9: Gemini Question Answering
@given(
    st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))),
    st.builds(WeatherContext, location=location_strategy())
)
def test_gemini_question_answering_property(question, context):
    """
    Property 9: Gemini Question Answering
    For any valid weather-related question with context, the Gemini_Integration 
    should return a non-empty natural language response.
    
    Validates: Requirements 6.3
    """
    assume(len(question.strip()) > 0)  # Ensure non-empty question
    
    client = GeminiClient(api_key="test_key")
    
    answer = client.answer_question(question, context)
    
    # Verify answer is non-empty string
    assert isinstance(answer, str)
    assert len(answer) > 0
    assert len(answer.strip()) > 0


# Feature: weather-prediction-system, Property 9: Gemini Question Answering (Full Context)
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    weather_data_strategy(),
    st.lists(forecast_strategy(), min_size=1, max_size=7)
)
def test_gemini_question_answering_full_context_property(question, weather_data, forecasts):
    """
    Property 9: Gemini Question Answering (Full Context)
    With full weather context, should return comprehensive answer.
    
    Validates: Requirements 6.3
    """
    assume(len(question.strip()) > 0)
    
    client = GeminiClient(api_key="test_key")
    context = WeatherContext(
        location=weather_data.location,
        current_weather=weather_data,
        forecasts=forecasts
    )
    
    answer = client.answer_question(question, context)
    
    assert isinstance(answer, str)
    assert len(answer) > 0


# Feature: weather-prediction-system, Property 10: Gemini Rate Limit Handling
@given(st.just(None))
def test_gemini_rate_limit_handling_property(dummy):
    """
    Property 10: Gemini Rate Limit Handling
    For any request made when rate limits are exceeded, the Gemini_Integration 
    should queue the request and return a notification to the user.
    
    Validates: Requirements 6.4
    """
    client = GeminiClient(api_key="test_key")
    
    # Get rate limit status
    status = client.handle_rate_limit()
    
    # Verify status structure
    assert isinstance(status, dict)
    assert 'rate_limited' in status
    assert 'queue_size' in status
    assert 'message' in status
    
    # Verify types
    assert isinstance(status['rate_limited'], bool)
    assert isinstance(status['queue_size'], int)
    assert isinstance(status['message'], str)
    
    # Message should be non-empty
    assert len(status['message']) > 0


# Feature: weather-prediction-system, Property 18: Gemini API Fallback
@given(st.lists(forecast_strategy(), min_size=1, max_size=7))
def test_gemini_api_fallback_property(forecasts):
    """
    Property 18: Gemini API Fallback
    For any Gemini API request that fails due to API unavailability, 
    the Gemini_Integration should return a predefined fallback response.
    
    Validates: Requirements 10.2
    """
    # Client without API key should use fallback
    client = GeminiClient(api_key=None)
    
    summary = client.generate_forecast_summary(forecasts)
    
    # Should return fallback response
    assert isinstance(summary, str)
    assert len(summary) > 0
    
    # Verify it's a valid fallback (not an error)
    assert "error" not in summary.lower() or "forecast" in summary.lower()


# Feature: weather-prediction-system, Property 18: Gemini API Fallback (Explanation)
@given(weather_data_strategy(), forecast_strategy())
def test_gemini_api_fallback_explanation_property(weather_data, forecast):
    """
    Property 18: Gemini API Fallback (Explanation)
    Weather explanations should have fallback responses.
    
    Validates: Requirements 10.2
    """
    client = GeminiClient(api_key=None)
    
    explanation = client.explain_weather_pattern(weather_data, forecast)
    
    assert isinstance(explanation, str)
    assert len(explanation) > 0


# Feature: weather-prediction-system, Property 18: Gemini API Fallback (Q&A)
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    st.builds(WeatherContext)
)
def test_gemini_api_fallback_qa_property(question, context):
    """
    Property 18: Gemini API Fallback (Q&A)
    Question answering should have fallback responses.
    
    Validates: Requirements 10.2
    """
    assume(len(question.strip()) > 0)
    
    client = GeminiClient(api_key=None)
    
    answer = client.answer_question(question, context)
    
    assert isinstance(answer, str)
    assert len(answer) > 0


# Feature: weather-prediction-system, Property 8: Prompt Builder Consistency
@given(st.lists(forecast_strategy(), min_size=1, max_size=7))
def test_prompt_builder_consistency_property(forecasts):
    """
    Property 8: Prompt Builder Consistency
    For any forecasts, prompt builder should generate consistent, valid prompts.
    
    Validates: Requirements 6.1
    """
    builder = PromptBuilder()
    
    prompt = builder.build_forecast_summary_prompt(forecasts)
    
    # Verify prompt structure
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    
    # Should contain location information
    if forecasts:
        location = forecasts[0].location
        assert location.city in prompt or location.country in prompt


# Feature: weather-prediction-system, Property 9: Response Parser Consistency
@given(st.text(min_size=1, max_size=1000))
def test_response_parser_consistency_property(response_text):
    """
    Property 9: Response Parser Consistency
    For any response text, parser should return valid cleaned text.
    
    Validates: Requirements 6.3
    """
    parser = ResponseParser()
    
    # Test all parser methods
    summary = parser.parse_summary_response(response_text)
    explanation = parser.parse_explanation_response(response_text)
    answer = parser.parse_answer_response(response_text)
    
    # All should return strings
    assert isinstance(summary, str)
    assert isinstance(explanation, str)
    assert isinstance(answer, str)
    
    # Should not contain markdown formatting
    assert '**' not in summary
    assert '**' not in explanation
    assert '**' not in answer


# Feature: weather-prediction-system, Property 10: Request Queue Behavior
@given(st.integers(min_value=0, max_value=100))
def test_request_queue_behavior_property(num_requests):
    """
    Property 10: Request Queue Behavior
    Request queue should maintain correct size.
    
    Validates: Requirements 6.4
    """
    client = GeminiClient(api_key="test_key")
    
    # Simulate queueing requests
    for i in range(num_requests):
        client._queue_request(f"test_prompt_{i}")
    
    # Verify queue size
    assert len(client.request_queue) == num_requests
    
    # Get status
    status = client.handle_rate_limit()
    assert status['queue_size'] == num_requests


# Feature: weather-prediction-system, Property 8: Client Info Consistency
@given(st.one_of(st.none(), st.text(min_size=1, max_size=100)))
def test_client_info_consistency_property(api_key):
    """
    Property 8: Client Info Consistency
    Client info should accurately reflect configuration.
    
    Validates: Requirements 6.1
    """
    client = GeminiClient(api_key=api_key)
    
    info = client.get_client_info()
    
    # Verify structure
    assert isinstance(info, dict)
    assert 'api_key_configured' in info
    assert 'rate_limit' in info
    assert 'queue_size' in info
    
    # Verify api_key_configured matches actual state
    assert info['api_key_configured'] == bool(api_key)
    
    # Verify rate limit is positive
    assert info['rate_limit'] > 0
    
    # Verify queue size is non-negative
    assert info['queue_size'] >= 0
