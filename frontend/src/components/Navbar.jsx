import { useState } from 'react';
import { NavLink } from 'react-router-dom';

const navGroups = [
  {
    label: null,
    collapsible: false,
    links: [
      { to: '/', label: 'Overview', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { to: '/monitors', label: 'Monitor Sources', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
      { to: '/blindspots', label: 'Blind Spots', icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' },
    ],
  },
  {
    label: 'Test Generation',
    collapsible: true,
    links: [
      { to: '/tests', label: 'Generated Tests', icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' },
      { to: '/results', label: 'Test Results', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    ],
  },
  {
    label: 'Jira Integration',
    collapsible: true,
    links: [
      { to: '/jira', label: 'Jira Input', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
    ],
  },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Top Header Bar */}
      <header className="bg-[#0C6CBF] text-white h-[50px] flex items-center px-4 fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-teal-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <span className="text-white text-lg">
            <span className="font-bold">WatchDog</span>{' '}
            <span className="font-light">AI</span>
          </span>
        </div>

        <div className="ml-auto flex items-center gap-3">
          <span className="text-sm text-gray-300 hidden sm:block">Sparkathon 2026</span>
          <div className="w-8 h-8 rounded-full bg-[#0C6CBF] flex items-center justify-center text-xs font-semibold text-white">
            PD
          </div>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="ml-3 lg:hidden p-1.5 text-gray-400 hover:text-white"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </header>

      {/* Sidebar */}
      <aside className={`fixed top-[50px] left-0 h-[calc(100vh-50px)] w-[250px] bg-white border-r border-gray-200 overflow-y-auto z-40 transition-transform ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}>
        <nav className="py-4">
          {navGroups.map((group, gi) => (
            <div key={gi} className="mb-3">
              {group.label && (
                <div className="px-5 py-2 flex items-center justify-between cursor-default">
                  <span className="text-[13px] font-bold text-gray-700">{group.label}</span>
                  {group.collapsible && (
                    <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </div>
              )}
              {group.links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-5 py-2 text-[13px] transition-colors border-l-[3px] ${
                      isActive
                        ? 'text-[#0C6CBF] font-medium border-[#0C6CBF]'
                        : 'text-[#6B7280] font-normal border-transparent hover:text-[#0C6CBF]'
                    }`
                  }
                >
                  <svg className="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={link.icon} />
                  </svg>
                  {link.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-30 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}
    </>
  );
}
