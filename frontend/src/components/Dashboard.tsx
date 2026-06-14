"""
Finovate Audit Nexus AI - Modern Dashboard Component
Enterprise AI Financial Audit & Intelligence Platform
"""

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
  Button, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
  Tabs, TabsContent, TabsList, TabsTrigger,
  Alert, AlertDescription
} from '@/components/ui/index';
import {
  Activity, AlertTriangle, CheckCircle, TrendingUp, Users,
  Settings, BarChart3, PieChart as PieChartIcon, LineChart as LineChartIcon
} from 'lucide-react';

interface DashboardProps {
  userId?: string;
  theme?: 'light' | 'dark';
}

interface AuditMetrics {
  totalAudits: number;
  completedAudits: number;
  pendingAudits: number;
  complianceScore: number;
  fraudRiskScore: number;
}

interface AIProviderStatus {
  name: string;
  status: 'active' | 'inactive' | 'error';
  model: string;
  tokensUsed: number;
  requestsCount: number;
}

const Dashboard: React.FC<DashboardProps> = ({ userId, theme = 'light' }) => {
  const [metrics, setMetrics] = useState<AuditMetrics>({
    totalAudits: 0,
    completedAudits: 0,
    pendingAudits: 0,
    complianceScore: 0,
    fraudRiskScore: 0
  });

  const [aiProviders, setAiProviders] = useState<AIProviderStatus[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('openai');
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for demonstration
  const mockChartData = [
    { name: 'Jan', audits: 40, compliance: 85, fraud: 12 },
    { name: 'Feb', audits: 50, compliance: 88, fraud: 10 },
    { name: 'Mar', audits: 45, compliance: 90, fraud: 8 },
    { name: 'Apr', audits: 60, compliance: 92, fraud: 6 },
    { name: 'May', audits: 55, compliance: 94, fraud: 5 },
    { name: 'Jun', audits: 70, compliance: 96, fraud: 3 }
  ];

  const mockProviders: AIProviderStatus[] = [
    {
      name: 'OpenAI',
      status: 'active',
      model: 'gpt-4',
      tokensUsed: 125000,
      requestsCount: 450
    },
    {
      name: 'Anthropic',
      status: 'active',
      model: 'claude-3-opus',
      tokensUsed: 95000,
      requestsCount: 320
    },
    {
      name: 'Google Gemini',
      status: 'active',
      model: 'gemini-pro',
      tokensUsed: 78000,
      requestsCount: 280
    },
    {
      name: 'Groq',
      status: 'active',
      model: 'mixtral-8x7b',
      tokensUsed: 45000,
      requestsCount: 150
    },
    {
      name: 'Ollama',
      status: 'inactive',
      model: 'llama2',
      tokensUsed: 0,
      requestsCount: 0
    }
  ];

  useEffect(() => {
    // Simulate loading data
    setLoading(true);
    setTimeout(() => {
      setMetrics({
        totalAudits: 285,
        completedAudits: 245,
        pendingAudits: 40,
        complianceScore: 94.5,
        fraudRiskScore: 8.2
      });
      setAiProviders(mockProviders);
      setChartData(mockChartData);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />;
      case 'inactive':
        return <Activity className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'} p-8`}>
      {/* Header */}
      <div className="mb-8">
        <h1 className={`text-4xl font-bold mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          Finovate Audit Nexus AI
        </h1>
        <p className={`text-lg ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
          Enterprise AI Financial Audit & Intelligence Platform
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="ai-providers">AI Providers</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Audits Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Total Audits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{metrics.totalAudits}</div>
                <p className="text-xs text-gray-500 mt-1">
                  <TrendingUp className="w-3 h-3 inline mr-1" />
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            {/* Completed Audits Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{metrics.completedAudits}</div>
                <p className="text-xs text-gray-500 mt-1">
                  {((metrics.completedAudits / metrics.totalAudits) * 100).toFixed(1)}% completion rate
                </p>
              </CardContent>
            </Card>

            {/* Compliance Score Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{metrics.complianceScore}%</div>
                <p className="text-xs text-gray-500 mt-1">
                  <CheckCircle className="w-3 h-3 inline mr-1" />
                  Excellent standing
                </p>
              </CardContent>
            </Card>

            {/* Fraud Risk Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Fraud Risk</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">{metrics.fraudRiskScore}%</div>
                <p className="text-xs text-gray-500 mt-1">
                  <AlertTriangle className="w-3 h-3 inline mr-1" />
                  Low risk level
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Audit Trends Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Audit Trends</CardTitle>
                <CardDescription>Monthly audit completion trend</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="audits" stroke="#3b82f6" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Compliance vs Fraud Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Compliance & Fraud Metrics</CardTitle>
                <CardDescription>Monthly comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="compliance" fill="#10b981" />
                    <Bar dataKey="fraud" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* AI Providers Tab */}
        <TabsContent value="ai-providers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Provider Management</CardTitle>
              <CardDescription>Monitor and manage LLM providers</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {aiProviders.map((provider) => (
                <div
                  key={provider.name}
                  className={`p-4 border rounded-lg ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded ${getStatusColor(provider.status)}`}>
                        {getStatusIcon(provider.status)}
                      </div>
                      <div>
                        <h3 className="font-semibold">{provider.name}</h3>
                        <p className="text-sm text-gray-500">Model: {provider.model}</p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(provider.status)}>
                      {provider.status.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Tokens Used</p>
                      <p className="font-semibold">{provider.tokensUsed.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Requests</p>
                      <p className="font-semibold">{provider.requestsCount}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Provider Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Select Default Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a provider" />
                </SelectTrigger>
                <SelectContent>
                  {aiProviders
                    .filter((p) => p.status === 'active')
                    .map((provider) => (
                      <SelectItem key={provider.name} value={provider.name.toLowerCase()}>
                        {provider.name} ({provider.model})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <Button className="mt-4 w-full">Save Provider Selection</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Analytics</CardTitle>
              <CardDescription>Detailed performance metrics and insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-4">Audit Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Completed', value: metrics.completedAudits },
                          { name: 'Pending', value: metrics.pendingAudits }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        <Cell fill="#10b981" />
                        <Cell fill="#f59e0b" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Performance Metrics</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">Compliance Score</span>
                        <span className="text-sm font-semibold">{metrics.complianceScore}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${metrics.complianceScore}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">Audit Completion</span>
                        <span className="text-sm font-semibold">
                          {((metrics.completedAudits / metrics.totalAudits) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{
                            width: `${(metrics.completedAudits / metrics.totalAudits) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Settings</CardTitle>
              <CardDescription>Configure platform preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  API keys and sensitive information are securely stored. Never share your keys.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Default Theme</label>
                  <Select defaultValue={theme}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Language</label>
                  <Select defaultValue="en">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="ar">العربية</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Number Format</label>
                  <Select defaultValue="en">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English (1,000.00)</SelectItem>
                      <SelectItem value="ar">Arabic (١٬٠٠٠٫٠٠)</SelectItem>
                      <SelectItem value="in">Indian (10,00,000)</SelectItem>
                      <SelectItem value="cn">Chinese (1,000.00)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button className="w-full">Save Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
