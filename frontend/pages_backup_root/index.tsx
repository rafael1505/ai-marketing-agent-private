export default function HomePage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🎉 Full Stack is Working!</h1>
      <div style={{ margin: '20px 0' }}>
        <h2>Service Status:</h2>
        <ul>
          <li>✅ MongoDB: Running</li>
          <li>✅ Backend API: Running on port 8088</li>
          <li>✅ Frontend: Running on port 3001</li>
        </ul>
      </div>
      <p>All services are operational! 🚀</p>
    </div>
  );
}