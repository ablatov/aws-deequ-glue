import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/Deequ - Data Quality Constraints/i);
  expect(linkElement).toBeInTheDocument();
});
