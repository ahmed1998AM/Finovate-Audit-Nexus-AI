"""
Finovate Audit Nexus AI - API Service Layer
Frontend API communication service
Enterprise AI Financial Audit & Intelligence Platform
"""

import axios, { AxiosInstance, AxiosError } from 'axios';

interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface AuditRequest {
  projectId: string;
  financialData: Record<string, any>;
  auditType: 'full' | 'fraud' | 'compliance' | 'risk';
  standards?: string[];
}

interface AuditResult {
  auditId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: Record<string, any>;
  timestamp: string;
}

interface AIProviderConfig {
  provider: string;
  apiKey: string;
  model: string;
  isDefault: boolean;
}

class APIService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.REACT_APP_API_URL || 'http://localhost:8000/api') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ==================== Audit Operations ====================

  async startAudit(request: AuditRequest): Promise<APIResponse<AuditResult>> {
    try {
      const response = await this.client.post<APIResponse<AuditResult>>(
        '/audits/start',
        request
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAuditStatus(auditId: string): Promise<APIResponse<AuditResult>> {
    try {
      const response = await this.client.get<APIResponse<AuditResult>>(
        `/audits/${auditId}/status`
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAuditResults(auditId: string): Promise<APIResponse<AuditResult>> {
    try {
      const response = await this.client.get<APIResponse<AuditResult>>(
        `/audits/${auditId}/results`
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async listAudits(filters?: Record<string, any>): Promise<APIResponse<AuditResult[]>> {
    try {
      const response = await this.client.get<APIResponse<AuditResult[]>>(
        '/audits',
        { params: filters }
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteAudit(auditId: string): Promise<APIResponse<{ success: boolean }>> {
    try {
      const response = await this.client.delete<APIResponse<{ success: boolean }>>(
        `/audits/${auditId}`
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // ==================== AI Provider Operations ====================

  async getAIProviders(): Promise<APIResponse<AIProviderConfig[]>> {
    try {
      const response = await this.client.get<APIResponse<AIProviderConfig[]>>(
        '/ai/providers'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async configureAIProvider(config: AIProviderConfig): Promise<APIResponse<AIProviderConfig>> {
    try {
      const response = await this.client.post<APIResponse<AIProviderConfig>>(
        '/ai/providers/configure',
        config
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async testAIProvider(provider: string): Promise<APIResponse<{ success: boolean; message: string }>> {
    try {
      const response = await this.client.post<APIResponse<{ success: boolean; message: string }>>(
        `/ai/providers/${provider}/test`
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAIEngineStatus(): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>>>(
        '/ai/status'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async setDefaultAIProvider(provider: string): Promise<APIResponse<{ success: boolean }>> {
    try {
      const response = await this.client.post<APIResponse<{ success: boolean }>>(
        '/ai/providers/set-default',
        { provider }
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // ==================== Agent Operations ====================

  async executeAgent(
    agentType: string,
    data: Record<string, any>
  ): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.post<APIResponse<Record<string, any>>>(
        `/agents/${agentType}/execute`,
        data
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAgentStatus(agentId: string): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>>>(
        `/agents/${agentId}/status`
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async listAgents(): Promise<APIResponse<Record<string, any>[]>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>[]>>(
        '/agents'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // ==================== Report Operations ====================

  async generateReport(
    auditId: string,
    format: 'pdf' | 'excel' | 'json'
  ): Promise<APIResponse<{ reportUrl: string }>> {
    try {
      const response = await this.client.post<APIResponse<{ reportUrl: string }>>(
        `/reports/generate`,
        { auditId, format }
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async downloadReport(reportId: string): Promise<Blob> {
    try {
      const response = await this.client.get(
        `/reports/${reportId}/download`,
        { responseType: 'blob' }
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ==================== Dashboard Operations ====================

  async getDashboardMetrics(): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>>>(
        '/dashboard/metrics'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getDashboardCharts(): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>>>(
        '/dashboard/charts'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // ==================== Settings Operations ====================

  async getSettings(): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.get<APIResponse<Record<string, any>>>(
        '/settings'
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async updateSettings(settings: Record<string, any>): Promise<APIResponse<Record<string, any>>> {
    try {
      const response = await this.client.put<APIResponse<Record<string, any>>>(
        '/settings',
        settings
      );
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // ==================== Error Handling ====================

  private handleError(error: any): APIResponse<any> {
    console.error('API Error:', error);

    if (error.response) {
      // Server responded with error status
      return {
        success: false,
        error: error.response.data?.error || 'An error occurred',
        message: error.response.data?.message || error.message
      };
    } else if (error.request) {
      // Request made but no response
      return {
        success: false,
        error: 'No response from server',
        message: 'Please check your connection'
      };
    } else {
      // Error in request setup
      return {
        success: false,
        error: 'Request error',
        message: error.message
      };
    }
  }

  // ==================== Utility Methods ====================

  setAuthToken(token: string): void {
    localStorage.setItem('authToken', token);
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearAuthToken(): void {
    localStorage.removeItem('authToken');
    delete this.client.defaults.headers.common['Authorization'];
  }

  setBaseURL(url: string): void {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }
}

// Export singleton instance
export const apiService = new APIService();

export default APIService;
