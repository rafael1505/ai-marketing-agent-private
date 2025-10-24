/**/**/**

 * DatabaseStatusCard Component

 *  * DatabaseStatusCard Component * DatabaseStatusCard Component

 * A React component for displaying database connection status and health information.

 * Supports both compact and full views with optional auto-refresh capabilities. *  * 

 */

 * Professional React component for displaying database status information * Professional React component for displaying database status information

'use client';

 * with real-time updates, modern UI design, and comprehensive error handling. * with real-time updates, modern UI design, and comprehensive error handling.

import React, { useState, useEffect } from 'react';

 */ */

interface DatabaseStatusCardProps {

  className?: string;

  compact?: boolean;

  showRefreshButton?: boolean;import React, { useState, useEffect } from 'react';import React from 'react';

  autoRefresh?: boolean;

  refreshInterval?: number;

}

interface DatabaseStatusCardProps { */

interface DatabaseStatus {

  connected: boolean;  className?: string;

  database: string;

  version: string;  showRefreshButton?: boolean;interface DatabaseStatusCardProps {

  activeConnections: number;

  lastUpdated: string;  autoRefresh?: boolean;

}

  refreshInterval?: number;  className?: string;'use client';

export const DatabaseStatusCard: React.FC<DatabaseStatusCardProps> = ({

  className = '',  compact?: boolean;

  compact = false,

  showRefreshButton = true,}  showRefreshButton?: boolean;

  autoRefresh = false,

  refreshInterval = 30000,

}) => {

  const [status, setStatus] = useState<DatabaseStatus>({export const DatabaseStatusCard: React.FC<DatabaseStatusCardProps> = ({  autoRefresh?: boolean;import React, { useState } from 'react';

    connected: true,

    database: 'MongoDB',  className = "",

    version: '6.0',

    activeConnections: 5,  showRefreshButton = true,  refreshInterval?: number;import { useDatabaseStatus } from '../hooks/useDatabaseStatus';

    lastUpdated: new Date().toLocaleString(),

  });  autoRefresh = true,



  const [isLoading, setIsLoading] = useState(false);  refreshInterval = 30000,  compact?: boolean;import { databaseStatusService } from '../services/databaseStatusService';



  const refreshStatus = async () => {  compact = false

    setIsLoading(true);

    // Simulate API call delay}) => {}

    setTimeout(() => {

      setStatus(prev => ({  const [status, setStatus] = useState({

        ...prev,

        lastUpdated: new Date().toLocaleString(),    connected: true,// Icons (using Lucide React icons - you may need to install: npm install lucide-react)

      }));

      setIsLoading(false);    database: "MongoDB",

    }, 500);

  };    version: "6.0",export const DatabaseStatusCard: React.FC<DatabaseStatusCardProps> = ({const DatabaseIcon = () => (



  useEffect(() => {    connections: 5,

    if (autoRefresh && refreshInterval > 0) {

      const interval = setInterval(refreshStatus, refreshInterval);    lastUpdated: new Date().toISOString()  className = '',  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">

      return () => clearInterval(interval);

    }  });

  }, [autoRefresh, refreshInterval]);

    showRefreshButton = false,    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7M4 7c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4M4 7h16m-4 4l-4 4-4-4" />

  if (compact) {

    return (  const [loading, setLoading] = useState(false);

      <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>

        <div className="flex items-center justify-between">  autoRefresh = false,  </svg>

          <div className="flex items-center space-x-2">

            <div className={`w-3 h-3 rounded-full ${status.connected ? 'bg-green-500' : 'bg-red-500'}`} />  const refreshStatus = async () => {

            <span className="text-sm font-medium">

              {status.connected ? 'Connected' : 'Disconnected'}    setLoading(true);  refreshInterval = 30000,);

            </span>

          </div>    try {

          <span className="text-xs text-gray-500">{status.database}</span>

        </div>      // Simulate API call  compact = false

      </div>

    );      await new Promise(resolve => setTimeout(resolve, 1000));

  }

      setStatus({}) => {const RefreshIcon = ({ className = "w-4 h-4" }: { className?: string }) => (

  return (

    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>        ...status,

      <div className="flex items-center justify-between mb-4">

        <h3 className="text-lg font-semibold text-gray-900">Database Status</h3>        lastUpdated: new Date().toISOString()  // Mock data for now  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">

        {showRefreshButton && (

          <button      });

            onClick={refreshStatus}

            disabled={isLoading}    } catch (error) {  const status = {    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />

            className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"

          >      console.error('Failed to refresh status:', error);

            {isLoading ? 'Refreshing...' : 'Refresh'}

          </button>    } finally {    isConnected: true,  </svg>

        )}

      </div>      setLoading(false);



      <div className="grid grid-cols-2 gap-4">    }    healthStatus: 'healthy',);

        <div>

          <label className="text-sm font-medium text-gray-600">Status</label>  };

          <div className="flex items-center space-x-2 mt-1">

            <div className={`w-3 h-3 rounded-full ${status.connected ? 'bg-green-500' : 'bg-red-500'}`} />    environment: 'development',

            <span className={`text-sm font-medium ${status.connected ? 'text-green-700' : 'text-red-700'}`}>

              {status.connected ? 'Connected' : 'Disconnected'}  useEffect(() => {

            </span>

          </div>    if (autoRefresh) {    database_type: 'mongodb',const CheckCircleIcon = () => (

        </div>

      const interval = setInterval(refreshStatus, refreshInterval);

        <div>

          <label className="text-sm font-medium text-gray-600">Database</label>      return () => clearInterval(interval);    connection_url: 'mongodb://localhost:27017',  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">

          <p className="text-sm text-gray-900 mt-1">{status.database}</p>

        </div>    }



        <div>  }, [autoRefresh, refreshInterval]);    database_name: 'ai_marketing_agent'    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />

          <label className="text-sm font-medium text-gray-600">Version</label>

          <p className="text-sm text-gray-900 mt-1">{status.version}</p>

        </div>

  if (compact) {  };  </svg>

        <div>

          <label className="text-sm font-medium text-gray-600">Active Connections</label>    return (

          <p className="text-sm text-gray-900 mt-1">{status.activeConnections}</p>

        </div>      <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>);

      </div>

        <div className="flex items-center justify-between">

      <div className="mt-4 pt-4 border-t border-gray-200">

        <p className="text-xs text-gray-500">          <div className="flex items-center space-x-2">  if (compact) {

          Last updated: {status.lastUpdated}

        </p>            <div className={`w-3 h-3 rounded-full ${status.connected ? 'bg-green-500' : 'bg-red-500'}`} />

      </div>

    </div>            <span className="text-sm font-medium">    return (const AlertCircleIcon = () => (

  );

};              {status.connected ? 'Connected' : 'Disconnected'}



export default DatabaseStatusCard;            </span>      <div className={`bg-white border rounded-lg p-4 ${className}`}>  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">

          </div>

          <span className="text-xs text-gray-500">{status.database}</span>        <div className="flex items-center space-x-3">    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />

        </div>

      </div>          <div className="w-4 h-4 bg-green-500 rounded-full"></div>  </svg>

    );

  }          <div>);



  return (            <div className="font-medium text-sm">Connected</div>

    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>

      <div className="flex items-center justify-between mb-4">            <div className="text-xs text-gray-500">{status.database_type}</div>const XCircleIcon = () => (

        <h3 className="text-lg font-semibold text-gray-900">Database Status</h3>

        {showRefreshButton && (          </div>  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">

          <button

            onClick={refreshStatus}        </div>    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />

            disabled={loading}

            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"      </div>  </svg>

          >

            {loading ? 'Refreshing...' : 'Refresh'}    ););

          </button>

        )}  }

      </div>

interface DatabaseStatusCardProps {

      <div className="grid grid-cols-2 gap-4">

        <div>  return (  className?: string;

          <label className="text-sm font-medium text-gray-600">Status</label>

          <div className="flex items-center space-x-2 mt-1">    <div className={`bg-white border rounded-lg p-6 ${className}`}>  compact?: boolean;

            <div className={`w-3 h-3 rounded-full ${status.connected ? 'bg-green-500' : 'bg-red-500'}`} />

            <span className={`text-sm font-medium ${status.connected ? 'text-green-700' : 'text-red-700'}`}>      <div className="flex items-center justify-between mb-4">  showRefreshButton?: boolean;

              {status.connected ? 'Connected' : 'Disconnected'}

            </span>        <h3 className="text-lg font-medium">Database Status</h3>  autoRefresh?: boolean;

          </div>

        </div>        {showRefreshButton && (  refreshInterval?: number;



        <div>          <button className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600">}

          <label className="text-sm font-medium text-gray-600">Database</label>

          <p className="text-sm text-gray-900 mt-1">{status.database}</p>            Refresh

        </div>

          </button>export const DatabaseStatusCard: React.FC<DatabaseStatusCardProps> = ({

        <div>

          <label className="text-sm font-medium text-gray-600">Version</label>        )}  className = '',

          <p className="text-sm text-gray-900 mt-1">{status.version}</p>

        </div>      </div>  compact = false,



        <div>        showRefreshButton = true,

          <label className="text-sm font-medium text-gray-600">Active Connections</label>

          <p className="text-sm text-gray-900 mt-1">{status.connections}</p>      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">  autoRefresh = true,

        </div>

      </div>        <div>  refreshInterval = 30000,



      <div className="mt-4 pt-4 border-t border-gray-200">          <div className="text-sm text-gray-500">Connection Status</div>}) => {

        <p className="text-xs text-gray-500">

          Last updated: {new Date(status.lastUpdated).toLocaleString()}          <div className="flex items-center space-x-2 mt-1">  const [isRefreshing, setIsRefreshing] = useState(false);

        </p>

      </div>            <div className="w-3 h-3 bg-green-500 rounded-full"></div>  

    </div>

  );            <span className="font-medium">Connected</span>  const {

};
          </div>    status,

        </div>    health,

            basicHealth,

        <div>    isLoading,

          <div className="text-sm text-gray-500">Health Status</div>    error,

          <div className="font-medium mt-1 text-green-600">{status.healthStatus}</div>    lastUpdated,

        </div>    refresh,

            isAutoRefreshing,

        <div>    startAutoRefresh,

          <div className="text-sm text-gray-500">Database Type</div>    stopAutoRefresh,

          <div className="font-medium mt-1">{status.database_type}</div>  } = useDatabaseStatus(autoRefresh, refreshInterval);

        </div>

          const handleManualRefresh = async () => {

        <div>    setIsRefreshing(true);

          <div className="text-sm text-gray-500">Environment</div>    try {

          <div className="font-medium mt-1">      await refresh();

            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">    } finally {

              {status.environment.toUpperCase()}      setIsRefreshing(false);

            </span>    }

          </div>  };

        </div>

      </div>  const toggleAutoRefresh = () => {

          if (isAutoRefreshing) {

      <div className="mt-4 pt-4 border-t">      stopAutoRefresh();

        <div className="text-sm text-gray-500">Connection Details</div>    } else {

        <div className="mt-2 space-y-1">      startAutoRefresh();

          <div className="text-sm">    }

            <span className="text-gray-500">URL:</span> {status.connection_url}  };

          </div>

          <div className="text-sm">  // Get status information from available data

            <span className="text-gray-500">Database:</span> {status.database_name}  const getStatusInfo = () => {

          </div>    if (status?.data) {

        </div>      return {

      </div>        type: status.data.database_type,

    </div>        environment: status.data.environment,

  );        isConnected: status.data.connection_status.is_connected,

};        healthStatus: status.data.connection_status.health_status,

        indicator: status.data.indicator,

export default DatabaseStatusCard;        details: status.data.details,
        metadata: status.data.metadata,
      };
    } else if (basicHealth?.database) {
      return {
        type: basicHealth.database.type,
        environment: basicHealth.database.environment,
        isConnected: basicHealth.database.status === 'connected',
        healthStatus: basicHealth.database.health,
        indicator: null,
        details: null,
        metadata: null,
      };
    }
    return null;
  };

  const statusInfo = getStatusInfo();

  // Get status color
  const getStatusColor = () => {
    if (!statusInfo) return 'text-gray-500';
    return databaseStatusService.getStatusColor(statusInfo.isConnected, statusInfo.healthStatus);
  };

  // Get environment color
  const getEnvironmentColor = () => {
    if (!statusInfo) return 'text-gray-500';
    return databaseStatusService.getEnvironmentColor(statusInfo.environment);
  };

  // Get status icon
  const getStatusIcon = () => {
    if (!statusInfo) return <AlertCircleIcon />;
    if (statusInfo.isConnected && statusInfo.healthStatus === 'connected') {
      return <CheckCircleIcon />;
    } else if (statusInfo.isConnected) {
      return <AlertCircleIcon />;
    } else {
      return <XCircleIcon />;
    }
  };

  if (error && !statusInfo) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center space-x-2">
          <XCircleIcon />
          <div>
            <h3 className="text-sm font-medium text-red-800">Database Status Error</h3>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
        {showRefreshButton && (
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200 transition-colors"
          >
            {isRefreshing ? 'Retrying...' : 'Retry'}
          </button>
        )}
      </div>
    );
  }

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="flex items-center space-x-1">
          <div style={{ color: getStatusColor() }}>
            {getStatusIcon()}
          </div>
          <span className="text-sm font-medium">
            {statusInfo?.indicator?.icon || '🗄️'} {statusInfo?.type?.toUpperCase() || 'UNKNOWN'}
          </span>
        </div>
        <div 
          className="px-2 py-1 rounded-full text-xs font-medium"
          style={{ 
            backgroundColor: `${getEnvironmentColor()}20`,
            color: getEnvironmentColor()
          }}
        >
          {statusInfo?.environment?.toUpperCase() || 'UNKNOWN'}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100">
        <div className="flex items-center space-x-2">
          <DatabaseIcon />
          <h3 className="text-lg font-semibold text-gray-900">Database Status</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Auto-refresh toggle */}
          <button
            onClick={toggleAutoRefresh}
            className={`px-2 py-1 text-xs rounded ${
              isAutoRefreshing 
                ? 'bg-green-100 text-green-700' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Auto: {isAutoRefreshing ? 'ON' : 'OFF'}
          </button>
          
          {/* Manual refresh button */}
          {showRefreshButton && (
            <button
              onClick={handleManualRefresh}
              disabled={isRefreshing || isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50"
            >
              <RefreshIcon className={`w-4 h-4 ${(isRefreshing || isLoading) ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {isLoading && !statusInfo ? (
          <div className="flex items-center justify-center py-8">
            <RefreshIcon className="w-6 h-6 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-500">Loading database status...</span>
          </div>
        ) : statusInfo ? (
          <div className="space-y-4">
            {/* Main Status */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div style={{ color: getStatusColor() }} className="flex-shrink-0">
                  {getStatusIcon()}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">
                      {statusInfo.indicator?.icon || '🗄️'}
                    </span>
                    <span className="text-lg font-semibold text-gray-900">
                      {statusInfo.type?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                    </span>
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${getEnvironmentColor()}20`,
                        color: getEnvironmentColor()
                      }}
                    >
                      {statusInfo.environment?.toUpperCase() || 'UNKNOWN'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {statusInfo.indicator?.description || 'Database connection status'}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <div 
                  className="text-sm font-medium"
                  style={{ color: getStatusColor() }}
                >
                  {statusInfo.isConnected ? 'Connected' : 'Disconnected'}
                </div>
                <div className="text-xs text-gray-500">
                  {statusInfo.healthStatus}
                </div>
              </div>
            </div>

            {/* Connection Details */}
            {statusInfo.details && (
              <div className="bg-gray-50 rounded-lg p-3">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Connection Details</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {statusInfo.details.host && (
                    <div>
                      <span className="text-gray-500">Host:</span>
                      <span className="ml-1 font-medium">{statusInfo.details.host}</span>
                    </div>
                  )}
                  {statusInfo.details.port && (
                    <div>
                      <span className="text-gray-500">Port:</span>
                      <span className="ml-1 font-medium">{statusInfo.details.port}</span>
                    </div>
                  )}
                  {statusInfo.details.database_name && (
                    <div className="col-span-2">
                      <span className="text-gray-500">Database:</span>
                      <span className="ml-1 font-medium">{statusInfo.details.database_name}</span>
                    </div>
                  )}
                  {statusInfo.details.version && (
                    <div>
                      <span className="text-gray-500">Version:</span>
                      <span className="ml-1 font-medium">{statusInfo.details.version}</span>
                    </div>
                  )}
                </div>
                
                {statusInfo.details.features && statusInfo.details.features.length > 0 && (
                  <div className="mt-2">
                    <span className="text-gray-500 text-sm">Features:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {statusInfo.details.features.map((feature, index) => (
                        <span 
                          key={index}
                          className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Performance Metrics */}
            {health && (
              <div className="bg-gray-50 rounded-lg p-3">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Performance</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {health.response_time_ms && (
                    <div>
                      <span className="text-gray-500">Response Time:</span>
                      <span className="ml-1 font-medium">{health.response_time_ms}ms</span>
                    </div>
                  )}
                  {statusInfo.metadata?.service_uptime && (
                    <div>
                      <span className="text-gray-500">Uptime:</span>
                      <span className="ml-1 font-medium">
                        {databaseStatusService.formatUptime(statusInfo.metadata.service_uptime)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Last Updated */}
            {lastUpdated && (
              <div className="text-xs text-gray-500 text-center">
                Last updated: {lastUpdated.toLocaleString()}
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No database status information available
          </div>
        )}
      </div>
    </div>
  );
};