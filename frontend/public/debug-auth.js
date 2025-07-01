// Helper script to provide development auth token
(function() {
  // In the browser, we can't check process.env.NODE_ENV directly
  // Instead, use a URL parameter or hostname check to enable debug mode
  const isLocalhost = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  
  if (!isLocalhost) return;
  
  console.log('Debug auth script running...');
  
  // Check if token exists, if not, add a development token
  if (!localStorage.getItem('token')) {
    console.log('Setting development mock token');
    localStorage.setItem('token', 'mock_test_token_dev_12345');
  } else {
    console.log('Auth token already exists in localStorage');
  }
})();
