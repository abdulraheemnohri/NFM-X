import { Outlet, Link } from 'react-router-dom';

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold text-gray-900">NFM-X</h1>
          <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium">Home</Link>
          <Link to="/memories" className="text-gray-600 hover:text-gray-900 font-medium">Memories</Link>
          <Link to="/stats" className="text-gray-600 hover:text-gray-900 font-medium">Stats</Link>
        </div>
      </nav>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
