// Helper script to provide development auth token
(function() {
  // In the browser, we can't check process.env.NODE_ENV directly
  // Instead, use a URL parameter or hostname check to enable debug mode
  const isLocalhost = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  
  if (!isLocalhost) return;
  
  console.log('Debug auth script running...');
  
  // Use the valid JWT token that the backend recognizes
  const validDevToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc0ODYxNjIwNiwiZXhwIjoxNzUxMjA4MjA2fQ.5tet1p59rOC6bsn7hnyr-i3O-C42IyVJ1qevxLDwfYw';
  
  // Check if token exists, if not, add a development token
  const currentToken = localStorage.getItem('token');
  if (!currentToken || currentToken.startsWith('mock_test_token')) {
    console.log('Setting valid development JWT token');
    localStorage.setItem('token', validDevToken);
  } else {
    console.log('Auth token already exists in localStorage:', currentToken.substring(0, 20) + '...');
  }
})();
