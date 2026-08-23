import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AWSAccountProvider } from './context/AWSAccountContext';
import { Layout } from './components/Layout';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { AWSAccountsPage } from './pages/AWSAccountsPage';
import { ResourcesPage } from './pages/ResourcesPage';
import { ResourceDetailPage } from './pages/ResourceDetailPage';
import { CostAnalysisPage } from './pages/CostAnalysisPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { ForecastPage } from './pages/ForecastPage';
import { AnomaliesPage } from './pages/AnomaliesPage';
import { BudgetsPage } from './pages/BudgetsPage';
import { AlertsPage } from './pages/AlertsPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { ReportsPage } from './pages/ReportsPage';
import { AdminPage } from './pages/AdminPage';
import { ProfilePage } from './pages/ProfilePage';

const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        Initializing Smart Cloud Cost Guardian...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user?.role !== 'ADMIN') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AWSAccountProvider>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Authenticated Dashboard shell */}
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/accounts" element={<AWSAccountsPage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/resources/:id" element={<ResourceDetailPage />} />
              <Route path="/costs" element={<CostAnalysisPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/anomalies" element={<AnomaliesPage />} />
              <Route path="/budgets" element={<BudgetsPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/assistant" element={<AIAssistantPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute adminOnly>
                    <AdminPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AWSAccountProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
