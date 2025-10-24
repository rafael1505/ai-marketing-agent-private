/**/**/**

 * DatabaseStatusIndicator Component

 * Compact database status indicator for header/sidebar use. * DatabaseStatusIndicator Component * DatabaseStatusIndicator Component

 */

 *  * 

import React from 'react';

 * Displays a small indicator showing the current database connection status. * Compact database status indicator for header/sidebar use.

interface DatabaseStatusIndicatorProps {

  className?: string; * Can be clicked to navigate to the full database status page. * Shows current database type and connection status with minimal space.

  showText?: boolean;

  onClick?: () => void; */ */

}



export const DatabaseStatusIndicator: React.FC<DatabaseStatusIndicatorProps> = ({

  className = '',import React from 'react';'use client';

  showText = false,

  onClickimport { useDatabaseStatus } from '../hooks/useDatabaseStatus';

}) => {

  // Mock status for nowimport { databaseStatusService } from '../services/databaseStatusService';import React from 'react';

  const statusInfo = {

    isConnected: true,import { useDatabaseStatus } from '../hooks/useDatabaseStatus';

    healthStatus: 'healthy',

    environment: 'development'interface DatabaseStatusIndicatorProps {import { databaseStatusService } from '../services/databaseStatusService';

  };

  className?: string;

  const handleClick = () => {

    if (onClick) {  showText?: boolean;interface DatabaseStatusIndicatorProps {

      onClick();

    } else {  onClick?: () => void;  className?: string;

      window.location.href = '/database-status';

    }}  showLabel?: boolean;

  };

  showEnvironment?: boolean;

  const getStatusColor = () => {

    if (statusInfo.isConnected && statusInfo.healthStatus === 'healthy') {export const DatabaseStatusIndicator: React.FC<DatabaseStatusIndicatorProps> = ({  onClick?: () => void;

      return 'bg-green-500';

    } else if (statusInfo.isConnected) {  className = '',}

      return 'bg-yellow-500';

    } else {  showText = false,

      return 'bg-red-500';

    }  onClickexport const DatabaseStatusIndicator: React.FC<DatabaseStatusIndicatorProps> = ({

  };

}) => {  className = '',

  return (

    <div   const { status, basicHealth, isLoading, error } = useDatabaseStatus(true, 60000); // 1-minute refresh  showLabel = true,

      className={`inline-flex items-center space-x-2 cursor-pointer hover:opacity-80 transition-opacity ${className}`}

      onClick={handleClick}  showEnvironment = true,

      title={`Database Status: ${statusInfo.healthStatus} (${statusInfo.environment})`}

    >  // Handle click to navigate to database status page  onClick,

      <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>

      {showText && (  const handleClick = () => {}) => {

        <span className="text-sm text-gray-700">

          DB: {statusInfo.healthStatus}    if (onClick) {  const { status, basicHealth, isLoading, error } = useDatabaseStatus(true, 60000); // 1-minute refresh

        </span>

      )}      onClick();

    </div>

  );    } else {  // Get status information from available data

};

      // Default navigation to database status page  const getStatusInfo = () => {

export default DatabaseStatusIndicator;
      window.location.href = '/database-status';    if (status?.data) {

    }      return {

  };        type: status.data.database_type,

        environment: status.data.environment,

  // Determine status info        isConnected: status.data.connection_status.is_connected,

  const getStatusInfo = () => {        healthStatus: status.data.connection_status.health_status,

    if (isLoading) {        indicator: status.data.indicator,

      return {      };

        isConnected: false,    } else if (basicHealth?.database) {

        healthStatus: 'loading',      return {

        environment: 'unknown'        type: basicHealth.database.type,

      };        environment: basicHealth.database.environment,

    }        isConnected: basicHealth.database.status === 'connected',

        healthStatus: basicHealth.database.health,

    if (error || !status) {        indicator: null,

      return {      };

        isConnected: false,    }

        healthStatus: 'error',    return null;

        environment: 'unknown'  };

      };

    }  const statusInfo = getStatusInfo();



    return {  // Get status color

      isConnected: status.isConnected || false,  const getStatusColor = () => {

      healthStatus: status.healthStatus || 'unknown',    if (!statusInfo) return '#6b7280'; // gray-500

      environment: status.environment || 'unknown'    return databaseStatusService.getStatusColor(statusInfo.isConnected, statusInfo.healthStatus);

    };  };

  };

  // Get environment color

  const statusInfo = getStatusInfo();  const getEnvironmentColor = () => {

    if (!statusInfo) return '#6b7280'; // gray-500

  // Get status color    return databaseStatusService.getEnvironmentColor(statusInfo.environment);

  const getStatusColor = () => {  };

    return databaseStatusService.getStatusColor(statusInfo.isConnected, statusInfo.healthStatus);

  };  // Get display icon

  const getDisplayIcon = () => {

  // Get environment color    if (isLoading) return '⟳';

  const getEnvironmentColor = () => {    if (error && !statusInfo) return '❌';

    return databaseStatusService.getEnvironmentColor(statusInfo.environment);    if (!statusInfo) return '❓';

  };    return statusInfo.indicator?.icon || '🗄️';

  };

  if (isLoading) {

    return (  // Get database type display

      <div className={`inline-flex items-center space-x-2 ${className}`}>  const getTypeDisplay = () => {

        <div className="w-3 h-3 bg-gray-400 rounded-full animate-pulse"></div>    if (!statusInfo) return 'Unknown';

        {showText && <span className="text-sm text-gray-500">Loading...</span>}    return statusInfo.type?.replace('_', ' ').toUpperCase() || 'UNKNOWN';

      </div>  };

    );

  }  // Get environment display

  const getEnvironmentDisplay = () => {

  return (    if (!statusInfo) return 'Unknown';

    <div     return statusInfo.environment?.toUpperCase() || 'UNKNOWN';

      className={`inline-flex items-center space-x-2 cursor-pointer hover:opacity-80 transition-opacity ${className}`}  };

      onClick={handleClick}

      title={`Database Status: ${statusInfo.healthStatus} (${statusInfo.environment})`}  const handleClick = () => {

    >    if (onClick) {

      {/* Status indicator dot */}      onClick();

      <div     } else {

        className={`w-3 h-3 rounded-full ${getStatusColor()}`}      // Default action: navigate to database status page

      ></div>      window.location.href = '/database-status';

          }

      {/* Optional text display */}  };

      {showText && (

        <div className="flex items-center space-x-1 text-sm">  return (

          <span className="text-gray-700">DB:</span>    <div 

          <span className={`font-medium ${getStatusColor().replace('bg-', 'text-')}`}>      className={`flex items-center space-x-2 cursor-pointer hover:opacity-80 transition-opacity ${className}`}

            {statusInfo.healthStatus}      onClick={handleClick}

          </span>      title={`Database: ${getTypeDisplay()} (${getEnvironmentDisplay()}) - Click for details`}

          <span     >

            className={`px-1.5 py-0.5 rounded text-xs font-medium ${getEnvironmentColor()}`}      {/* Status indicator dot */}

          >      <div 

            {statusInfo.environment.toUpperCase()}        className="w-2 h-2 rounded-full flex-shrink-0"

          </span>        style={{ backgroundColor: getStatusColor() }}

        </div>      />

      )}

    </div>      {/* Database icon */}

  );      <span className="text-sm flex-shrink-0">

};        {getDisplayIcon()}

      </span>

export default DatabaseStatusIndicator;
      {/* Database type label */}
      {showLabel && (
        <span className="text-xs font-medium text-gray-700 flex-shrink-0">
          {getTypeDisplay()}
        </span>
      )}

      {/* Environment badge */}
      {showEnvironment && statusInfo && (
        <span 
          className="px-1.5 py-0.5 rounded text-xs font-medium flex-shrink-0"
          style={{ 
            backgroundColor: `${getEnvironmentColor()}20`,
            color: getEnvironmentColor()
          }}
        >
          {getEnvironmentDisplay()}
        </span>
      )}

      {/* Connection status */}
      {statusInfo && (
        <span 
          className="text-xs flex-shrink-0"
          style={{ color: getStatusColor() }}
        >
          {statusInfo.isConnected ? '●' : '○'}
        </span>
      )}
    </div>
  );
};