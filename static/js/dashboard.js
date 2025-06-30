/**
 * Dashboard
 * 
 * @author AI Assistant (Claude)
 * @date 2025-01-28
 * @ai_assisted 是 - Claude 3.5 Sonnet
 * @version v1.0
 * @license MIT
 */


class Dashboard {
    constructor() {
        this.charts = {};
        this.currentPage = 1;
        this.pageSize = 10;
        this.currentFilter = 'all';
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadDashboardData();
        this.startAutoRefresh();
    }
    
    bindEvents() {
        // 刷新按钮
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadDashboardData();
        });
        
        // 历史记录筛选
        document.getElementById('historyFilter').addEventListener('change', (e) => {
            this.currentFilter = e.target.value;
            this.currentPage = 1;
            this.loadProcessingHistory();
        });
        
        // 导出历史记录
        document.getElementById('exportHistoryBtn').addEventListener('click', () => {
            this.exportHistory();
        });
        
        // 分页按钮
        document.getElementById('historyPrevBtn').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadProcessingHistory();
            }
        });
        
        document.getElementById('historyNextBtn').addEventListener('click', () => {
            this.currentPage++;
            this.loadProcessingHistory();
        });
    }
    
    async loadDashboardData() {
        this.showLoading(true);
        
        try {
            // 并行加载所有数据
            const [performanceStats, apiHealth, operationBreakdown] = await Promise.all([
                this.fetchPerformanceStats(),
                this.fetchApiHealth(),
                this.fetchOperationBreakdown()
            ]);
            
            this.updateMetricCards(performanceStats);
            this.updateApiHealthStatus(apiHealth);
            this.updateCharts(performanceStats, operationBreakdown);
            this.loadProcessingHistory();
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('加载仪表板数据失败');
        } finally {
            this.showLoading(false);
        }
    }
    
    async fetchPerformanceStats() {
        const response = await fetch('/api/performance/stats');
        if (!response.ok) throw new Error('Failed to fetch performance stats');
        const data = await response.json();
        if (!data.success) throw new Error('Failed to fetch performance stats');
        return data;
    }
    
    async fetchApiHealth() {
        const response = await fetch('/api/performance/health');
        if (!response.ok) throw new Error('Failed to fetch API health');
        const data = await response.json();
        if (!data.success) throw new Error('Failed to fetch API health');
        return data;
    }
    
    async fetchOperationBreakdown() {
        const response = await fetch('/api/performance/operations');
        if (!response.ok) throw new Error('Failed to fetch operation breakdown');
        const data = await response.json();
        if (!data.success) throw new Error('Failed to fetch operation breakdown');
        return data;
    }
    
    updateMetricCards(stats) {
        // 总处理次数
        document.getElementById('totalOperations').textContent = 
            this.formatNumber(stats.total_requests || 0);
        document.getElementById('operationsChange').textContent = 
            `最近24小时: ${stats.recent_requests || 0} 次`;
        
        // 成功率
        const successRate = ((stats.success_rate || 0) * 100).toFixed(1);
        document.getElementById('successRate').textContent = `${successRate}%`;
        document.getElementById('successProgressBar').style.width = `${successRate}%`;
        
        // 平均响应时间
        const avgTime = (stats.avg_duration_ms || 0).toFixed(0);
        document.getElementById('avgResponseTime').textContent = `${avgTime}ms`;
        document.getElementById('responseTimeChange').textContent = 
            `相比昨天: ${stats.time_change || 'N/A'}`;
        
        // 缓存命中率
        const cacheRate = ((stats.cache_hit_rate || 0) * 100).toFixed(1);
        document.getElementById('cacheHitRate').textContent = `${cacheRate}%`;
        document.getElementById('cacheProgressBar').style.width = `${cacheRate}%`;
    }
    
    updateApiHealthStatus(healthData) {
        const container = document.getElementById('apiHealthStatus');
        container.innerHTML = '';
        
        const apis = healthData.endpoints || [];
        
        apis.forEach(api => {
            const statusClass = api.healthy ? 'status-healthy' : 
                               api.warning ? 'status-warning' : 'status-error';
            const statusText = api.healthy ? '健康' : 
                              api.warning ? '警告' : '异常';
            
            const card = document.createElement('div');
            card.className = 'bg-gray-50 rounded-lg p-4';
            card.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium text-gray-900">${api.name}</h4>
                    <span class="status-indicator ${statusClass}"></span>
                </div>
                <div class="text-sm text-gray-600">
                    <div>状态: ${statusText}</div>
                    <div>响应时间: ${api.avg_response_time || 0}ms</div>
                    <div>成功率: ${((api.success_rate || 0) * 100).toFixed(1)}%</div>
                </div>
            `;
            container.appendChild(card);
        });
    }
    
    updateCharts(performanceStats, operationBreakdown) {
        this.updateOperationChart(operationBreakdown);
        this.updateResponseTimeChart(performanceStats.time_series || []);
    }
    
    updateOperationChart(operationData) {
        const ctx = document.getElementById('operationChart').getContext('2d');
        
        if (this.charts.operationChart) {
            this.charts.operationChart.destroy();
        }
        
        const labels = operationData.map(op => op.operation);
        const data = operationData.map(op => op.count);
        const colors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
            '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
        ];
        
        this.charts.operationChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, data.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updateResponseTimeChart(timeSeriesData) {
        const ctx = document.getElementById('responseTimeChart').getContext('2d');
        
        if (this.charts.responseTimeChart) {
            this.charts.responseTimeChart.destroy();
        }
        
        const labels = timeSeriesData.map(point => 
            new Date(point.timestamp).toLocaleTimeString()
        );
        const data = timeSeriesData.map(point => point.avg_duration);
        
        this.charts.responseTimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '平均响应时间 (ms)',
                    data: data,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '响应时间 (ms)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '时间'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    async loadProcessingHistory() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                size: this.pageSize,
                filter: this.currentFilter
            });
            
            const response = await fetch(`/api/performance/history?${params}`);
            if (!response.ok) throw new Error('Failed to fetch processing history');
            
            const data = await response.json();
            if (!data.success) throw new Error('Failed to fetch processing history');
            
            this.updateHistoryTable(data.records || []);
            this.updatePagination(data.total || 0);
            
        } catch (error) {
            console.error('Failed to load processing history:', error);
            this.showError('加载处理历史失败');
        }
    }
    
    updateHistoryTable(records) {
        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = '';
        
        records.forEach(record => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            
            const statusBadge = record.success ? 
                '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">成功</span>' :
                '<span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">失败</span>';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${new Date(record.timestamp).toLocaleString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${record.operation}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${statusBadge}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${record.duration_ms}ms
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${record.api_endpoint || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button class="text-blue-600 hover:text-blue-900" onclick="dashboard.showRecordDetails('${record.id}')">
                        查看详情
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    updatePagination(total) {
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, total);
        
        document.getElementById('historyStart').textContent = start;
        document.getElementById('historyEnd').textContent = end;
        document.getElementById('historyTotal').textContent = total;
        
        document.getElementById('historyPrevBtn').disabled = this.currentPage <= 1;
        document.getElementById('historyNextBtn').disabled = end >= total;
    }
    
    async exportHistory() {
        try {
            const response = await fetch('/api/performance/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filter: this.currentFilter,
                    format: 'csv'
                })
            });
            
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `performance_history_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Failed to export history:', error);
            this.showError('导出历史记录失败');
        }
    }
    
    showRecordDetails(recordId) {
        // 显示记录详情的模态框
        console.log('Show details for record:', recordId);
        // TODO: 实现详情模态框
    }
    
    startAutoRefresh() {
        // 每30秒自动刷新数据
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
    
    showError(message) {
        // 简单的错误提示
        alert(message);
        // TODO: 实现更好的错误提示UI
    }
    
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// 初始化仪表板
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});

// 页面卸载时停止自动刷新
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.stopAutoRefresh();
    }
});
