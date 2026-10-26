import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <div className="page-wrap">
          <Outlet />
        </div>
      </main>
    </div>
  );
}