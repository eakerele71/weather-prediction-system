"""Gemini LLM integration for natural language weather insights"""
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import json
from app.models import Forecast, WeatherData, Location

logger = logging.getLogger(__name__)


@dataclass
class WeatherContext:
    """Context information for Gemini prompts"""
    current_weather: Optional[WeatherData] = None
    forecasts: Optional[List[Forecast]] = None
    location: Optional[Location] = None
    historical_data: Optional[List[WeatherData]] = None


class PromptBuilder:
    """Builds prompts with weather context for Gemini API"""
    
    def __init__(self):
        """Initialize prompt builder"""
        pass

    def build_forecast_summary_prompt(self, forecasts: List[Forecast]) -> str:
        """Build prompt for generating forecast summary
        
        Args:
            forecasts: List of weather forecasts
            
        Returns:
            Formatted prompt string
        """
        if not forecasts:
            return "Generate a brief weather summary."
        
        location = forecasts[0].location
        forecast_details = []
        
        for forecast in forecasts[:7]:  # Limit to 7 days
            forecast_details.append(
                f"- {forecast.forecast_date}: High {forecast.predicted_temperature_high:.1f}°C, "
                f"Low {forecast.predicted_temperature_low:.1f}°C, "
                f"{forecast.weather_condition}, "
                f"Precipitation: {forecast.precipitation_probability*100:.0f}%, "
                f"Confidence: {forecast.confidence_score*100:.0f}%"
            )
        
        prompt = f"""Generate a natural language weather forecast summary for {location.city}, {location.country}.

Weather Forecast:
{chr(10).join(forecast_details)}

Please provide:
1. A brief overview of the weather pattern for the week
2. Any notable weather changes or trends
3. Practical advice for planning activities

Keep the summary concise, friendly, and easy to understand."""
        
        return prompt

    def build_weather_explanation_prompt(self, current_weather: WeatherData, 
                                       forecast: Forecast) -> str:
        """Build prompt for explaining weather patterns
        
        Args:
            current_weather: Current weather conditions
            forecast: Weather forecast
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Explain the weather pattern for {current_weather.location.city}, {current_weather.location.country}.

Current Conditions:
- Temperature: {current_weather.temperature:.1f}°C
- Humidity: {current_weather.humidity:.0f}%
- Pressure: {current_weather.pressure:.1f} hPa
- Wind: {current_weather.wind_speed:.1f} m/s from {current_weather.wind_direction:.0f}°
- Conditions: {current_weather.weather_condition}
- Precipitation: {current_weather.precipitation:.1f} mm

Forecast for {forecast.forecast_date}:
- High: {forecast.predicted_temperature_high:.1f}°C
- Low: {forecast.predicted_temperature_low:.1f}°C
- Conditions: {forecast.weather_condition}
- Precipitation Probability: {forecast.precipitation_probability*100:.0f}%

Please explain:
1. What meteorological factors are influencing this weather
2. Why the forecast predicts these conditions
3. What this means for daily activities

Use simple, accessible language."""
        
        return prompt

    def build_question_answer_prompt(self, question: str, context: WeatherContext) -> str:
        """Build prompt for answering user questions about weather
        
        Args:
            question: User's question
            context: Weather context information
            
        Returns:
            Formatted prompt string
        """
        context_parts = []
        
        if context.location:
            context_parts.append(f"Location: {context.location.city}, {context.location.country}")
        
        if context.current_weather:
            w = context.current_weather
            context_parts.append(
                f"Current Weather: {w.temperature:.1f}°C, {w.weather_condition}, "
                f"Humidity {w.humidity:.0f}%, Wind {w.wind_speed:.1f} m/s"
            )
        
        if context.forecasts:
            forecast_summary = ", ".join([
                f"{f.forecast_date}: {f.predicted_temperature_high:.0f}°C"
                for f in context.forecasts[:3]
            ])
            context_parts.append(f"Upcoming Forecast: {forecast_summary}")
        
        context_str = "\n".join(context_parts) if context_parts else "No specific weather context available."
        
        prompt = f"""Answer the following weather-related question using the provided context.

Context:
{context_str}

Question: {question}

Please provide a clear, accurate, and helpful answer. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide general weather information that might be helpful."""
        
        return prompt


class ResponseParser:
    """Parses and formats responses from Gemini API"""
    
    def __init__(self):
        """Initialize response parser"""
        pass

    def parse_summary_response(self, response_text: str) -> str:
        """Parse forecast summary response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Formatted summary text
        """
        # Clean up response text
        cleaned = response_text.strip()
        
        # Remove any markdown formatting if present
        cleaned = cleaned.replace('**', '').replace('*', '')
        
        return cleaned

    def parse_explanation_response(self, response_text: str) -> str:
        """Parse weather explanation response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Formatted explanation text
        """
        cleaned = response_text.strip()
        cleaned = cleaned.replace('**', '').replace('*', '')
        return cleaned

    def parse_answer_response(self, response_text: str) -> str:
        """Parse question answer response
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Formatted answer text
        """
        cleaned = response_text.strip()
        cleaned = cleaned.replace('**', '').replace('*', '')
        return cleaned


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        
        # Rate limiting
        self.request_queue: List[Dict[str, Any]] = []
        self.max_requests_per_minute = 60
        self.last_request_time: Optional[datetime] = None
        
        # Fallback responses
        self.fallback_responses = {
            'summary': "Weather forecast is available. Please check the detailed forecast for more information.",
            'explanation': "Weather patterns are influenced by atmospheric pressure, temperature, and humidity. Check the current conditions and forecast for specific details.",
            'answer': "I'm currently unable to provide a detailed answer. Please refer to the weather forecast and current conditions for information."
        }

    def generate_forecast_summary(self, forecasts: List[Forecast]) -> str:
        """Generate natural language summary of weather forecast
        
        Args:
            forecasts: List of weather forecasts
            
        Returns:
            Natural language summary
        """
        if not forecasts:
            return self.fallback_responses['summary']
        
        try:
            # Build prompt
            prompt = self.prompt_builder.build_forecast_summary_prompt(forecasts)
            
            # Make API call (simulated for now)
            response = self._call_gemini_api(prompt)
            
            # Parse response
            summary = self.response_parser.parse_summary_response(response)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating forecast summary: {e}")
            return self.fallback_responses['summary']

    def explain_weather_pattern(self, current_weather: WeatherData, 
                               forecast: Forecast) -> str:
        """Explain weather patterns and forecast reasoning
        
        Args:
            current_weather: Current weather conditions
            forecast: Weather forecast
            
        Returns:
            Natural language explanation
        """
        try:
            # Build prompt
            prompt = self.prompt_builder.build_weather_explanation_prompt(
                current_weather, forecast
            )
            
            # Make API call
            response = self._call_gemini_api(prompt)
            
            # Parse response
            explanation = self.response_parser.parse_explanation_response(response)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining weather pattern: {e}")
            return self.fallback_responses['explanation']

    def answer_question(self, question: str, context: WeatherContext) -> str:
        """Answer user questions about weather
        
        Args:
            question: User's question
            context: Weather context information
            
        Returns:
            Natural language answer
        """
        try:
            # Build prompt
            prompt = self.prompt_builder.build_question_answer_prompt(question, context)
            
            # Make API call
            response = self._call_gemini_api(prompt)
            
            # Parse response
            answer = self.response_parser.parse_answer_response(response)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return self.fallback_responses['answer']

    def _call_gemini_api(self, prompt: str) -> str:
        """Make API call to Gemini
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            API response text
        """
        # Check rate limits
        if self._is_rate_limited():
            logger.warning("Rate limit reached, queueing request")
            self._queue_request(prompt)
            raise Exception("Rate limit exceeded")
        
        # Check if API key is available
        if not self.api_key:
            logger.warning("No Gemini API key configured, using fallback")
            raise Exception("No API key configured")
        
        # In production, this would make actual API call to Gemini
        # For now, return a simulated response
        logger.info("Simulating Gemini API call (no actual API key configured)")
        
        # Simulate API response based on prompt content
        if "forecast summary" in prompt.lower():
            return self._generate_simulated_summary(prompt)
        elif "explain" in prompt.lower():
            return self._generate_simulated_explanation(prompt)
        else:
            return self._generate_simulated_answer(prompt)

    def _is_rate_limited(self) -> bool:
        """Check if rate limit has been reached
        
        Returns:
            True if rate limited
        """
        if not self.last_request_time:
            return False
        
        time_since_last = (datetime.now() - self.last_request_time).total_seconds()
        
        # Simple rate limiting: max 1 request per second
        return time_since_last < 1.0

    def _queue_request(self, prompt: str) -> None:
        """Queue a request for later processing
        
        Args:
            prompt: Prompt to queue
        """
        self.request_queue.append({
            'prompt': prompt,
            'timestamp': datetime.now()
        })
        logger.info(f"Request queued. Queue size: {len(self.request_queue)}")

    def handle_rate_limit(self) -> Dict[str, Any]:
        """Handle rate limit situation
        
        Returns:
            Status information about rate limiting
        """
        return {
            'rate_limited': self._is_rate_limited(),
            'queue_size': len(self.request_queue),
            'message': 'Your request has been queued due to rate limits. It will be processed shortly.'
        }

    def _generate_simulated_summary(self, prompt: str) -> str:
        """Generate simulated forecast summary
        
        Args:
            prompt: Original prompt
            
        Returns:
            Simulated summary
        """
        return """The week ahead shows variable weather conditions with temperatures ranging from mild to moderate. 
Expect some precipitation mid-week, with clearer skies towards the weekend. 
Plan outdoor activities for the latter part of the week when conditions improve. 
Keep an umbrella handy for the next few days."""

    def _generate_simulated_explanation(self, prompt: str) -> str:
        """Generate simulated weather explanation
        
        Args:
            prompt: Original prompt
            
        Returns:
            Simulated explanation
        """
        return """The current weather pattern is influenced by a high-pressure system bringing stable conditions. 
Temperature variations are typical for this time of year, driven by diurnal heating and cooling cycles. 
The forecast suggests continued stability with gradual warming as the high-pressure system strengthens. 
These conditions are favorable for most outdoor activities, though morning temperatures may be cool."""

    def _generate_simulated_answer(self, prompt: str) -> str:
        """Generate simulated answer to question
        
        Args:
            prompt: Original prompt
            
        Returns:
            Simulated answer
        """
        return """Based on the current weather conditions and forecast, the weather should be generally favorable. 
Temperature and precipitation patterns suggest typical seasonal conditions. 
For specific planning, check the detailed hourly forecast and any weather warnings that may be in effect. 
Always prepare for slight variations from the forecast, especially for outdoor activities."""

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the Gemini client
        
        Returns:
            Dictionary with client information
        """
        return {
            'api_key_configured': bool(self.api_key),
            'rate_limit': self.max_requests_per_minute,
            'queue_size': len(self.request_queue),
            'last_request': self.last_request_time.isoformat() if self.last_request_time else None
        }
