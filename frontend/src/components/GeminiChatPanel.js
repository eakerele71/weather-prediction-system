import { useState, useRef, useEffect } from 'react';
import { useWeather } from '../context/WeatherContext';
import WeatherCard from './WeatherCard';
import './GeminiChatPanel.css';

const GeminiChatPanel = () => {
  const { currentLocation, askGemini, explainWeather } = useWeather();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message when location changes
  useEffect(() => {
    if (currentLocation && messages.length === 0) {
      setMessages([
        {
          type: 'assistant',
          content: `Hi! I'm your AI weather assistant. Ask me anything about the weather in ${currentLocation}!`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [currentLocation, messages.length]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await askGemini(inputValue, {
        location: currentLocation,
      });

      const assistantMessage = {
        type: 'assistant',
        content: response.response || response.explanation || 'I apologize, but I couldn\'t generate a response.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExplainWeather = async () => {
    if (!currentLocation || isLoading) return;

    const userMessage = {
      type: 'user',
      content: `Explain the current weather in ${currentLocation}`,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await explainWeather(currentLocation);

      const assistantMessage = {
        type: 'assistant',
        content: response.explanation || 'I apologize, but I couldn\'t generate an explanation.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!currentLocation) {
    return (
      <WeatherCard title="AI Weather Assistant" className="gemini-chat-panel">
        <div className="chat-empty-state">
          <div className="empty-state-icon">🤖</div>
          <p>Select a location to start chatting with the AI weather assistant</p>
        </div>
      </WeatherCard>
    );
  }

  return (
    <WeatherCard title="AI Weather Assistant" className="gemini-chat-panel">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message ${message.type}`}
            >
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : message.type === 'error' ? '⚠️' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">{formatTime(message.timestamp)}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-loading">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-quick-actions">
          <button
            className="quick-action-btn"
            onClick={handleExplainWeather}
            disabled={isLoading}
          >
            <span className="quick-action-icon">💡</span>
            Explain Weather
          </button>
        </div>

        <div className="chat-input-container">
          <textarea
            className="chat-input"
            placeholder="Ask me anything about the weather..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            rows="2"
          />
          <button
            className="chat-send-btn"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M2 10L18 2L10 18L8 11L2 10Z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>
      </div>
    </WeatherCard>
  );
};

export default GeminiChatPanel;
