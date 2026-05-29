// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from '@/components/layout/Header';
import { StatusBanner } from '@/components/layout/StatusBanner';
import { PredictionsView } from '@/components/views/PredictionsView';
import { StandingsView } from '@/components/views/StandingsView';
import { HistoryView } from '@/components/views/HistoryView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Show stale data immediately while refetching in background
      // This prevents loading spinners on tab focus
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-bg-primary font-body text-text-primary">
          <Header />
          <StatusBanner />
          <main>
            <Routes>
              <Route path="/" element={<PredictionsView />} />
              <Route path="/standings" element={<StandingsView />} />
              <Route path="/history" element={<HistoryView />} />
              {/* Catch-all → predictions */}
              <Route path="*" element={<PredictionsView />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}