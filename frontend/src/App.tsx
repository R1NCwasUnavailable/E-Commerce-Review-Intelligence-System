import { createBrowserRouter, RouterProvider, NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, MessageSquarePlus, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Analyze from './pages/Analyze';

// In React Router v7, it's highly recommended to use the data router approach.
function Layout() {
  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon" style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-tertiary))', width: '32px', height: '32px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: 900, fontSize: '18px' }}>R</span>
          </div>
          ReviewIntel
        </div>
        
        <nav>
          <NavLink 
            to="/" 
            className={({isActive}) => isActive ? "nav-link active" : "nav-link"}
          >
            <LayoutDashboard size={20} />
            Dashboard
          </NavLink>
          <NavLink 
            to="/analyze" 
            className={({isActive}) => isActive ? "nav-link active" : "nav-link"}
          >
            <MessageSquarePlus size={20} />
            Analyze Data
          </NavLink>
        </nav>
        
        <div style={{ marginTop: 'auto' }}>
          <div className="nav-link" style={{ opacity: 0.5, cursor: 'not-allowed' }}>
            <Settings size={20} />
            Settings
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content fade-in">
        <Outlet />
      </main>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: "analyze",
        element: <Analyze />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
