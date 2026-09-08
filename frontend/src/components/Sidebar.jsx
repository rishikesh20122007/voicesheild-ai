import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/analyze', label: 'Analyze Audio' },
  { to: '/history', label: 'Scan History' },
];

function Sidebar() {
  return (
    <aside className="bg-vs-panel border-r border-slate-700 w-56 min-h-screen p-4">
      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block px-3 py-2 rounded text-sm transition ${
                isActive
                  ? 'bg-vs-accent text-vs-dark font-semibold'
                  : 'text-slate-300 hover:bg-slate-800'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;