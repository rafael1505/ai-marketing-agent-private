import { NextApiRequest, NextApiResponse } from 'next';

/**
 * API diagnostics tool for company API issues
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Get the axios library
    const axios = require('axios');
    
    // Get the API URL parameter or use the default
    const apiUrl = req.query.url || 'http://127.0.0.1:8088/api/v1';
    const endpoint = req.query.endpoint || '/companies/active';
    
    // Get token from the request
    const token = req.headers.authorization || req.query.token;
    
    // Headers to send
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = token.toString().startsWith('Bearer ') 
        ? token.toString() 
        : `Bearer ${token}`;
    }
    
    // Log the attempt
    console.log(`Diagnostic tool testing connection to ${apiUrl}${endpoint}`);
    console.log(`With headers: ${JSON.stringify(headers)}`);
    
    try {
      // Try the request with proxy disabled
      const response = await axios.get(`${apiUrl}${endpoint}`, {
        headers,
        proxy: false,
        timeout: 5000,
      });
      
      // Success!
      return res.status(200).json({
        success: true,
        message: 'Connection successful',
        status: response.status,
        data: response.data
      });
    } catch (directError: any) {
      console.error('Direct connection failed:', directError.message);
      
      // Try with a proxy rewrite
      try {
        const proxyResponse = await axios.get(`/companies-proxy/active`, {
          headers,
          timeout: 5000,
        });
        
        return res.status(200).json({
          success: true,
          message: 'Connection successful via proxy rewrite',
          status: proxyResponse.status,
          data: proxyResponse.data
        });
      } catch (proxyError: any) {
        console.error('Proxy rewrite connection failed:', proxyError.message);
        
        // All attempts failed
        return res.status(500).json({
          success: false,
          message: 'All connection attempts failed',
          directError: directError.message,
          proxyError: proxyError.message
        });
      }
    }
  } catch (error: any) {
    console.error('Diagnostic tool error:', error.message);
    return res.status(500).json({
      success: false,
      message: 'Diagnostic tool error',
      error: error.message
    });
  }
}
