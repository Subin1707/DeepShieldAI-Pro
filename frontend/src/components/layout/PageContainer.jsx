import { useEffect, useState } from "react";

import Footer from "./Footer.jsx";
import Navbar from "./Navbar.jsx";
import Sidebar from "./Sidebar.jsx";

function PageContainer({ children, title, subtitle }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activePath, setActivePath] = useState(window.location.hash || "#/");

  useEffect(() => {
    const handleHashChange = () => setActivePath(window.location.hash || "#/");
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  return (
    <div className="min-h-screen overflow-x-hidden bg-shield-bg text-slate-100">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-[18rem] top-16 h-72 w-72 rounded-full bg-cyan-400/12 blur-3xl" />
        <div className="absolute right-0 top-24 h-80 w-80 rounded-full bg-violet-500/12 blur-3xl" />
        <div className="absolute bottom-0 left-1/2 h-72 w-96 rounded-full bg-emerald-400/8 blur-3xl" />
      </div>

      <Navbar
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen((value) => !value)}
      />

      <div className="pt-16">
        <Sidebar
          open={sidebarOpen}
          activePath={activePath}
          onNavigate={() => setSidebarOpen(false)}
        />

        <div className="flex min-h-[calc(100vh-4rem)] flex-col lg:ml-72">
          <main className="flex-1 px-4 py-6 lg:px-8">
            {(title || subtitle) && (
              <div className="mb-6">
                {title && (
                  <h2 className="bg-gradient-to-r from-white via-cyan-100 to-violet-100 bg-clip-text text-3xl font-extrabold text-transparent">
                    {title}
                  </h2>
                )}
                {subtitle && <p className="mt-2 text-slate-400">{subtitle}</p>}
              </div>
            )}
            {children}
          </main>
          <Footer />
        </div>
      </div>
    </div>
  );
}

export default PageContainer;
