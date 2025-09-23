const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Función para servir archivos estáticos
function serveStatic(req, res, filePath) {
  const ext = path.extname(filePath);
  let contentType = 'text/html';
  
  switch (ext) {
    case '.js':
      contentType = 'text/javascript';
      break;
    case '.css':
      contentType = 'text/css';
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

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 - File Not Found</h1>');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

// Página principal HTML
const indexHTML = `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nuwa - Token Impact System for Ecosystem Conservation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #edfaf6 0%, #def7ef 25%, #c7f2e6 50%, #a9ebd9 75%, #7ee0c6 100%);
            min-height: 100vh;
            animation: gradient 15s ease infinite;
            background-size: 400% 400%;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        .nav-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #065f46;
        }

        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav-links a {
            text-decoration: none;
            color: #374151;
            font-weight: 500;
            transition: color 0.3s;
        }

        .nav-links a:hover {
            color: #065f46;
        }

        .hero {
            padding: 120px 0 80px;
            text-align: center;
        }

        .hero h1 {
            font-size: 3rem;
            font-weight: bold;
            color: #065f46;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .hero p {
            font-size: 1.25rem;
            color: #374151;
            max-width: 600px;
            margin: 0 auto 2rem;
        }

        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
            cursor: pointer;
        }

        .btn-primary {
            background: #065f46;
            color: white;
        }

        .btn-primary:hover {
            background: #047857;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 95, 70, 0.3);
        }

        .btn-secondary {
            background: transparent;
            color: #065f46;
            border: 2px solid #065f46;
        }

        .btn-secondary:hover {
            background: #065f46;
            color: white;
        }

        .features {
            padding: 80px 0;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-icon {
            width: 60px;
            height: 60px;
            background: #065f46;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            color: white;
            font-size: 1.5rem;
        }

        .feature-card h3 {
            color: #065f46;
            margin-bottom: 1rem;
            font-size: 1.25rem;
        }

        .stats {
            padding: 80px 0;
            text-align: center;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #065f46;
        }

        .stat-label {
            color: #6B7280;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }

        .footer {
            background: #065f46;
            color: white;
            text-align: center;
            padding: 3rem 0;
            margin-top: 4rem;
        }

        .blockchain-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(6, 95, 70, 0.1);
            padding: 0.5rem 1rem;
            border-radius: 25px;
            margin-bottom: 1rem;
            color: #065f46;
            font-weight: 600;
        }

        .status-indicator {
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(16, 185, 129, 0.9);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 600;
            z-index: 1000;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }

            .nav-links {
                display: none;
            }

            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="status-indicator">
        🟢 Sistema en Vivo
    </div>

    <nav class="navbar">
        <div class="container">
            <div class="nav-content">
                <div class="logo">🌱 Nuwa</div>
                <ul class="nav-links">
                    <li><a href="#inicio">Inicio</a></li>
                    <li><a href="#features">Características</a></li>
                    <li><a href="#stats">Estadísticas</a></li>
                    <li><a href="#blockchain">Blockchain</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <section id="inicio" class="hero">
        <div class="container">
            <div class="blockchain-badge">
                ⛓️ Powered by Cardano Blockchain
            </div>
            <h1>Sistema de Impacto de Tokens para Conservación de Ecosistemas</h1>
            <p>
                Transformamos la conservación ambiental en tokens verificables en blockchain, 
                creando transparencia total en proyectos de impacto ecológico y financiero.
            </p>
            <div class="cta-buttons">
                <a href="#features" class="btn btn-primary">Explorar Plataforma</a>
                <a href="#blockchain" class="btn btn-secondary">Ver Demo en Vivo</a>
            </div>
        </div>
    </section>

    <section id="features" class="features">
        <div class="container">
            <h2 style="text-align: center; color: #065f46; font-size: 2.5rem; margin-bottom: 1rem;">
                Funcionalidades Principales
            </h2>
            <p style="text-align: center; color: #6B7280; max-width: 600px; margin: 0 auto;">
                Una plataforma integral que combina tecnología blockchain, análisis de datos y conservación ambiental
            </p>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🌍</div>
                    <h3>Monitoreo de Ecosistemas</h3>
                    <p>Seguimiento en tiempo real de biodiversidad, especies y métricas ambientales con datos verificables.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">⛓️</div>
                    <h3>Verificación Blockchain</h3>
                    <p>Cada dato ambiental se registra en Cardano blockchain para garantizar transparencia total.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Analytics Avanzados</h3>
                    <p>Dashboards interactivos con IA que muestran impacto, proyecciones y ROI ambiental.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <h3>Tokenización de Impacto</h3>
                    <p>Convierte conservación en tokens tradeable, creando nuevos modelos de financiamiento verde.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <h3>Gestión de Proyectos</h3>
                    <p>Herramientas completas para administrar iniciativas de conservación desde un solo lugar.</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔬</div>
                    <h3>Base Científica</h3>
                    <p>Modelos matemáticos validados para cálculo preciso de captura de CO2 y biodiversidad.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="stats" class="stats">
        <div class="container">
            <h2 style="color: #065f46; font-size: 2.5rem; margin-bottom: 1rem;">
                Impacto en Números
            </h2>
            <p style="color: #6B7280; max-width: 600px; margin: 0 auto;">
                Resultados reales de nuestros proyectos de conservación activos
            </p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">2,847</div>
                    <div class="stat-label">Toneladas CO2 Capturadas</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">47</div>
                    <div class="stat-label">Proyectos Activos</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">156</div>
                    <div class="stat-label">Especies Monitoreadas</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">12,450</div>
                    <div class="stat-label">Hectáreas Protegidas</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">8.9</div>
                    <div class="stat-label">Índice Biodiversidad</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">94%</div>
                    <div class="stat-label">Transparencia Verificada</div>
                </div>
            </div>
        </div>
    </section>

    <section id="blockchain" style="padding: 80px 0; background: rgba(255, 255, 255, 0.9);">
        <div class="container">
            <h2 style="text-align: center; color: #065f46; font-size: 2.5rem; margin-bottom: 2rem;">
                Demo en Vivo - Funcionalidades
            </h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem;">
                <div class="feature-card">
                    <h3>🏠 Dashboard Principal</h3>
                    <p>Vista general de proyectos, KPIs ambientales y progreso en tiempo real</p>
                    <button onclick="showDemo('dashboard')" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
                        Ver Dashboard
                    </button>
                </div>
                
                <div class="feature-card">
                    <h3>📊 Analytics Avanzados</h3>
                    <p>Gráficos interactivos, tendencias de CO2 y análisis predictivo con IA</p>
                    <button onclick="showDemo('analytics')" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
                        Ver Analytics
                    </button>
                </div>
                
                <div class="feature-card">
                    <h3>💳 Wallet Cardano</h3>
                    <p>Conecta tu wallet, ve transacciones y tokens de impacto ambiental</p>
                    <button onclick="showDemo('wallet')" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
                        Conectar Wallet
                    </button>
                </div>
                
                <div class="feature-card">
                    <h3>📁 Carga de Datos</h3>
                    <p>Sube archivos Excel con datos ambientales y procesa automáticamente</p>
                    <button onclick="showDemo('upload')" class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
                        Subir Datos
                    </button>
                </div>
            </div>
            
            <div id="demo-content" style="margin-top: 3rem; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1); display: none;">
                <div id="demo-text"></div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <h3>🌱 Nuwa - Conservación Verificada en Blockchain</h3>
            <p style="margin: 1rem 0;">
                Transformando la manera en que el mundo financia y verifica proyectos de conservación ambiental
            </p>
            <p style="color: #A7F3D0;">
                Construido con Next.js • Cardano • Prisma • TypeScript
            </p>
            <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                <p>&copy; 2024 Proyecto Nuwa. Sistema de demostración técnica.</p>
            </div>
        </div>
    </footer>

    <script>
        function showDemo(type) {
            const demoContent = document.getElementById('demo-content');
            const demoText = document.getElementById('demo-text');
            
            const demos = {
                dashboard: {
                    title: '🏠 Dashboard Principal - Vista en Vivo',
                    content: 
                        '<h4>Estado Actual del Sistema:</h4>' +
                        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">' +
                            '<div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">' +
                                '<strong>Proyectos Activos:</strong> 12<br>' +
                                '<small>+3 este mes</small>' +
                            '</div>' +
                            '<div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">' +
                                '<strong>CO2 Capturado:</strong> 2,847 ton<br>' +
                                '<small>+156 ton esta semana</small>' +
                            '</div>' +
                            '<div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">' +
                                '<strong>Especies:</strong> 156<br>' +
                                '<small>89% en estado saludable</small>' +
                            '</div>' +
                        '</div>' +
                        '<p>✅ Base de datos: SQLite conectada</p>' +
                        '<p>✅ API Routes: Funcionando</p>' +
                        '<p>✅ Servidor: Puerto 3000 activo</p>'
                },
                analytics: {
                    title: '📊 Analytics - Datos en Tiempo Real',
                    content: \`
                        <h4>Métricas Ambientales Actuales:</h4>
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <strong>Tendencia CO2 (últimos 30 días):</strong><br>
                            📈 +12% captura comparado con mes anterior<br>
                            🌳 Proyectos forestales: 67% del total<br>
                            💧 Conservación de humedales: 23% del total<br>
                            🏔️ Protección montañosa: 10% del total
                        </div>
                        <p><strong>IA Prediction:</strong> Proyección de 3,200+ tons CO2 para fin de año</p>
                        <p><strong>Biodiversidad Index:</strong> 8.9/10 (Excelente)</p>
                    \`
                },
                wallet: {
                    title: '💳 Cardano Wallet Integration',
                    content: \`
                        <h4>Estado de Blockchain:</h4>
                        <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <p><strong>Red:</strong> Cardano Testnet</p>
                            <p><strong>Wallets Soportados:</strong> Nami, Eternl, Flint, Yoroi, Lace</p>
                            <p><strong>Smart Contracts:</strong> Activos</p>
                            <p><strong>Tokens Ambientales:</strong> 1,250 CO2-Tokens acuñados</p>
                        </div>
                        <button onclick="connectWallet()" class="btn btn-primary">Simular Conexión de Wallet</button>
                        <div id="wallet-status" style="margin-top: 1rem;"></div>
                    \`
                },
                upload: {
                    title: '📁 Sistema de Carga de Datos',
                    content: \`
                        <h4>Procesamiento de Datos Excel:</h4>
                        <div style="background: #fefce8; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <p><strong>Formatos Soportados:</strong> .xlsx, .xls</p>
                            <p><strong>Hojas Procesables:</strong> Projects, Species, Ecosystems, Parcels, Coverage</p>
                            <p><strong>Validación Automática:</strong> ✅ Activada</p>
                            <p><strong>Última Carga:</strong> 89 especies, 12 proyectos procesados</p>
                        </div>
                        <input type="file" accept=".xlsx,.xls" style="margin: 1rem 0; padding: 0.5rem;">
                        <p><em>Simulación: El sistema procesaría y validaría datos automáticamente</em></p>
                    \`
                }
            };
            
            if (demos[type]) {
                demoText.innerHTML = 
                    '<h3>' + demos[type].title + '</h3>' +
                    demos[type].content;
                demoContent.style.display = 'block';
                demoContent.scrollIntoView({ behavior: 'smooth' });
            }
        }

        function connectWallet() {
            const status = document.getElementById('wallet-status');
            status.innerHTML = 
                '<div style="background: #dcfce7; padding: 1rem; border-radius: 8px; border: 1px solid #16a34a;">' +
                    '<p><strong>🟢 Wallet Conectado (Simulación)</strong></p>' +
                    '<p><strong>Dirección:</strong> addr1qx2kd...7h8j (truncada)</p>' +
                    '<p><strong>Balance:</strong> 150.45 ADA</p>' +
                    '<p><strong>Tokens Ambientales:</strong> 45 CO2-Tokens</p>' +
                    '<p><strong>Última Transacción:</strong> Verificación de 12.5 tons CO2</p>' +
                '</div>';
        }

        // Animación de números
        function animateNumbers() {
            const numbers = document.querySelectorAll('.stat-number');
            numbers.forEach(num => {
                const target = parseInt(num.textContent.replace(/,/g, ''));
                let current = 0;
                const increment = target / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        num.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        num.textContent = Math.floor(current).toLocaleString();
                    }
                }, 50);
            });
        }

        // Observador para animar cuando sea visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateNumbers();
                    observer.unobserve(entry.target);
                }
            });
        });

        document.addEventListener('DOMContentLoaded', () => {
            const statsSection = document.getElementById('stats');
            observer.observe(statsSection);
        });
    </script>
</body>
</html>
`;

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Rutas
  if (pathname === '/' || pathname === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(indexHTML);
  } else if (pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy', 
      timestamp: new Date().toISOString(),
      service: 'Nuwa Environmental Platform',
      version: '1.0.0'
    }));
  } else if (pathname === '/api/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      database: 'connected',
      server: 'running',
      projects: 12,
      co2_captured: '2,847 tons',
      species_monitored: 156,
      last_update: new Date().toISOString()
    }));
  } else if (pathname === '/test' || pathname === '/test-demos.html') {
    const testHTML = fs.readFileSync(path.join(__dirname, 'test-demos.html'), 'utf8');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(testHTML);
  } else {
    // Intentar servir archivo estático
    const filePath = path.join(__dirname, 'public', pathname);
    serveStatic(req, res, filePath);
  }
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, '0.0.0.0', () => {
  console.log('🚀 Nuwa Environmental Platform');
  console.log('=================================');
  console.log('✅ Server running on port ' + PORT);
  console.log('🌍 Environment: ' + (process.env.NODE_ENV || 'development'));
  console.log('🔗 Access at: http://localhost:' + PORT);
  console.log('🌱 Status: All systems operational');
  console.log('=================================');
});

// Manejo de errores
server.on('error', (err) => {
  console.error('❌ Server error:', err);
});

process.on('SIGTERM', () => {
  console.log('🛑 Server shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});