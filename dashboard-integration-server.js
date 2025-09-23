const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3500;

// MIME types
const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);
  let pathname = parsedUrl.pathname;

  // Default to demo page
  if (pathname === '/' || pathname === '/dashboard') {
    pathname = '/dashboard-integration-demo.html';
  }

  const filePath = path.join(__dirname, pathname);
  const ext = path.extname(filePath);
  const mimeType = mimeTypes[ext] || 'text/plain';

  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // API Routes for authentication demo
  if (pathname.startsWith('/api/')) {
    handleApiRequest(req, res, pathname);
    return;
  }

  // Serve static files
  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end(`
          <html>
            <head><title>404 Not Found</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
              <h1>404 - Page Not Found</h1>
              <p>The requested file was not found.</p>
              <a href="/">Go to Dashboard Demo</a>
            </body>
          </html>
        `);
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': mimeType });
      res.end(data);
    }
  });
});

function handleApiRequest(req, res, pathname) {
  res.setHeader('Content-Type', 'application/json');

  // Mock API endpoints for authentication testing
  if (pathname === '/api/auth/status') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'operational',
      message: 'Dashboard Integration Demo API',
      endpoints: [
        'GET /api/auth/status',
        'POST /api/auth/login',
        'POST /api/auth/register',
        'GET /api/user/profile',
        'GET /api/dashboard/stats'
      ],
      timestamp: new Date().toISOString()
    }));
    return;
  }

  if (pathname === '/api/auth/login' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const { email, password } = JSON.parse(body);
        
        // Mock authentication
        const mockUsers = {
          'demo@nuwa.earth': {
            id: 1,
            email: 'demo@nuwa.earth',
            username: 'demo_user',
            first_name: 'Demo',
            last_name: 'User',
            full_name: 'Demo User',
            role: 'project_manager',
            status: 'active',
            organization: { name: 'Nuwa Demo Org' },
            permissions: ['PROJECT_CREATE', 'PROJECT_READ', 'EVALUATION_READ', 'SATELLITE_READ'],
            last_login: new Date().toISOString(),
            created_at: '2025-09-23T14:54:56.446046Z'
          },
          'admin@nuwa.earth': {
            id: 2,
            email: 'admin@nuwa.earth',
            username: 'admin',
            first_name: 'Admin',
            last_name: 'User',
            full_name: 'Admin User',
            role: 'admin',
            status: 'active',
            organization: { name: 'Nuwa Platform' },
            permissions: ['PROJECT_CREATE', 'PROJECT_READ', 'USER_CREATE', 'USER_READ', 'SYSTEM_CONFIG'],
            last_login: new Date().toISOString(),
            created_at: '2025-09-20T10:00:00.000000Z'
          }
        };

        if (mockUsers[email] && password === 'DemoPassword123!') {
          res.writeHead(200);
          res.end(JSON.stringify({
            access_token: 'mock_jwt_token_' + Date.now(),
            refresh_token: 'mock_refresh_token_' + Date.now(),
            token_type: 'bearer',
            expires_in: 1800,
            user: mockUsers[email]
          }));
        } else {
          res.writeHead(401);
          res.end(JSON.stringify({
            detail: 'Invalid credentials'
          }));
        }
      } catch (error) {
        res.writeHead(400);
        res.end(JSON.stringify({
          detail: 'Invalid request body'
        }));
      }
    });
    return;
  }

  if (pathname === '/api/auth/register' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const { email, password, first_name, last_name, username } = JSON.parse(body);
        
        // Mock successful registration
        res.writeHead(200);
        res.end(JSON.stringify({
          message: 'Registration successful. Please check your email to verify your account.',
          success: true
        }));
      } catch (error) {
        res.writeHead(400);
        res.end(JSON.stringify({
          detail: 'Invalid request body'
        }));
      }
    });
    return;
  }

  if (pathname === '/api/dashboard/stats') {
    res.writeHead(200);
    res.end(JSON.stringify({
      totalProjects: 12,
      co2Captured: '2.4M tons',
      activeEvaluations: 8,
      teamMembers: 15,
      recentActivity: [
        { type: 'project_created', message: 'New project "Forest Restoration" created', timestamp: new Date().toISOString() },
        { type: 'evaluation_completed', message: 'Carbon assessment completed for Project Alpha', timestamp: new Date(Date.now() - 3600000).toISOString() },
        { type: 'user_joined', message: 'New team member joined', timestamp: new Date(Date.now() - 7200000).toISOString() }
      ]
    }));
    return;
  }

  // Default 404 for API routes
  res.writeHead(404);
  res.end(JSON.stringify({
    detail: 'API endpoint not found',
    available_endpoints: ['/api/auth/status', '/api/auth/login', '/api/auth/register', '/api/dashboard/stats']
  }));
}

server.listen(PORT, () => {
  console.log(`🚀 Dashboard Integration Demo Server running at:`);
  console.log(`   • Local: http://localhost:${PORT}`);
  console.log(`   • Dashboard Demo: http://localhost:${PORT}/dashboard`);
  console.log(`   • API Status: http://localhost:${PORT}/api/auth/status`);
  console.log('');
  console.log('📋 Demo Features:');
  console.log('   ✅ Authentication Integration');
  console.log('   ✅ Role-based Dashboard');
  console.log('   ✅ Permission-based Actions');
  console.log('   ✅ User Profile Display');
  console.log('   ✅ Mock API Integration');
  console.log('');
  console.log('🔑 Test Credentials:');
  console.log('   • Email: demo@nuwa.earth');
  console.log('   • Email: admin@nuwa.earth');
  console.log('   • Password: DemoPassword123!');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Dashboard Integration Demo Server...');
  server.close(() => {
    console.log('✅ Server closed gracefully');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed gracefully');
    process.exit(0);
  });
});