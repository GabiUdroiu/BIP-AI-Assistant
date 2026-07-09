import ChatPage from './pages/Chat';
import Dashboard from './pages/Dashboard';

export default function App() {
  // URL-based routing - check pathname
  const path = window.location.pathname;
  const isDashboard = path.includes('/dashboard');

  return <>{isDashboard ? <Dashboard /> : <ChatPage />}</>;
}
