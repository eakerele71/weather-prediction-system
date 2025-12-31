import { render, screen } from '@testing-library/react';
import App from './App';

test('renders weather prediction system header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Weather Prediction System/i);
  expect(headerElement).toBeInTheDocument();
});
