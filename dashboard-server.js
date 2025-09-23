const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
    const urlPath = req.url === '/' ? '/advanced-dashboard-demo.html' : req.url;
    
    // Route for advanced dashboard demo
    if (urlPath === '/advanced-dashboard-demo.html' || urlPath === '/dashboard' || urlPath === '/') {
        try {
            const filePath = path.join(__dirname, 'advanced-dashboard-demo.html');
            const content = fs.readFileSync(filePath, 'utf8');
            
            res.writeHead(200, {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            });
            res.end(content);
        } catch (err) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end(`
                <h1>Dashboard Not Found</h1>
                <p>Error loading dashboard: ${err.message}</p>
                <p><a href="/">Try again</a></p>
            `);
        }
        return;
    }
    
    // Handle static files
    let filePath = path.join(__dirname, urlPath === '/' ? 'advanced-dashboard-demo.html' : urlPath);
    
    // Security check - ensure file is within the project directory
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('Forbidden');
        return;
    }
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end(`
                <h1>404 - File Not Found</h1>
                <p>The requested file was not found.</p>
                <p><a href="/">Go to Dashboard</a></p>
            `);
            return;
        }
        
        // Set content type based on file extension
        const ext = path.extname(filePath);
        let contentType = 'text/html';
        
        switch (ext) {
            case '.css':
                contentType = 'text/css';
                break;
            case '.js':
                contentType = 'text/javascript';
                break;
            case '.json':
                contentType = 'application/json';
                break;
            case '.png':
                contentType = 'image/png';
                break;
            case '.jpg':
            case '.jpeg':
                contentType = 'image/jpeg';
                break;
            case '.svg':
                contentType = 'image/svg+xml';
                break;
        }
        
        res.writeHead(200, { 
            'Content-Type': contentType,
            'Cache-Control': 'no-cache'
        });
        res.end(data);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log('🚀 Nuwa Advanced Dashboard Server');
    console.log('=================================');
    console.log(`✅ Server running on port ${PORT}`);
    console.log(`🌍 Environment: production`);
    console.log(`🔗 Access at: http://localhost:${PORT}`);
    console.log(`📊 Dashboard: http://localhost:${PORT}/dashboard`);
    console.log(`🌱 Status: Dashboard operational`);
    console.log('=================================');
});
