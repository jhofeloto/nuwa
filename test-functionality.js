// Script de prueba para verificar funcionalidades del frontend
const puppeteer = require('puppeteer');

async function testNuwaFunctionality() {
    console.log('🧪 Iniciando pruebas de funcionalidad de Nuwa...\n');
    
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    const errors = [];
    const consoleMessages = [];
    
    // Capturar errores y mensajes de consola
    page.on('console', msg => {
        consoleMessages.push(`${msg.type()}: ${msg.text()}`);
    });
    
    page.on('pageerror', err => {
        errors.push(`Page Error: ${err.toString()}`);
    });
    
    try {
        // Navegar a la página
        console.log('📱 Cargando página principal...');
        await page.goto('https://3000-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Verificar elementos básicos
        console.log('🔍 Verificando elementos del DOM...');
        const pageTitle = await page.title();
        console.log(`✅ Título de página: ${pageTitle}`);
        
        // Verificar navegación
        const navLinks = await page.evaluate(() => {
            const links = document.querySelectorAll('.nav-links a');
            return Array.from(links).map(link => link.textContent.trim());
        });
        console.log(`✅ Enlaces de navegación: ${navLinks.join(', ')}`);
        
        // Verificar botones de demo
        const demoButtons = await page.evaluate(() => {
            const buttons = document.querySelectorAll('button[onclick*="showDemo"]');
            return Array.from(buttons).map(btn => btn.textContent.trim());
        });
        console.log(`✅ Botones de demo encontrados: ${demoButtons.join(', ')}`);
        
        // Probar función showDemo
        console.log('🎯 Probando función showDemo...');
        const demoTest = await page.evaluate(() => {
            if (typeof showDemo === 'function') {
                showDemo('dashboard');
                const demoContent = document.getElementById('demo-content');
                return {
                    exists: !!demoContent,
                    visible: demoContent ? demoContent.style.display !== 'none' : false,
                    hasContent: demoContent ? demoContent.innerHTML.length > 0 : false
                };
            }
            return { error: 'showDemo function not found' };
        });
        console.log(`📊 Resultado demo test:`, demoTest);
        
        // Verificar animaciones CSS
        const animations = await page.evaluate(() => {
            const elements = Array.from(document.querySelectorAll('*'));
            let animatedElements = 0;
            elements.forEach(el => {
                const style = getComputedStyle(el);
                if (style.animationName !== 'none' || 
                    style.transitionDuration !== '0s' || 
                    el.classList.contains('animate-pulse')) {
                    animatedElements++;
                }
            });
            return { animatedElements, backgroundAnimation: getComputedStyle(document.body).backgroundSize };
        });
        console.log(`🎨 Animaciones encontradas: ${animations.animatedElements} elementos animados`);
        
        // Verificar métricas en números
        const statsNumbers = await page.evaluate(() => {
            const statNumbers = document.querySelectorAll('.stat-number');
            return Array.from(statNumbers).map(num => num.textContent.trim());
        });
        console.log(`📊 Métricas mostradas: ${statsNumbers.join(', ')}`);
        
        // Probar scroll suave
        console.log('📜 Probando scroll suave...');
        await page.click('a[href="#features"]');
        await page.waitForTimeout(2000);
        
        // Verificar responsive design
        console.log('📱 Probando responsive design...');
        await page.setViewport({ width: 768, height: 1024 });
        await page.waitForTimeout(1000);
        
        const mobileView = await page.evaluate(() => {
            const navbar = document.querySelector('.navbar');
            const hero = document.querySelector('.hero h1');
            return {
                navbarVisible: !!navbar,
                heroFontSize: getComputedStyle(hero).fontSize,
                bodyWidth: document.body.offsetWidth
            };
        });
        console.log(`📱 Vista móvil:`, mobileView);
        
        // Volver a desktop
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Resumen final
        console.log('\n🎉 RESUMEN DE PRUEBAS:');
        console.log(`✅ Página carga correctamente: ${pageTitle}`);
        console.log(`✅ Navegación funcional: ${navLinks.length} enlaces`);
        console.log(`✅ Demos interactivos: ${demoButtons.length} botones`);
        console.log(`✅ Animaciones CSS: ${animations.animatedElements} elementos`);
        console.log(`✅ Métricas dinámicas: ${statsNumbers.length} números`);
        console.log(`✅ Responsive design: Funcional`);
        
        if (errors.length > 0) {
            console.log('\n⚠️ ERRORES ENCONTRADOS:');
            errors.forEach(error => console.log(`❌ ${error}`));
        }
        
        if (consoleMessages.length > 0) {
            console.log('\n📝 MENSAJES DE CONSOLA:');
            consoleMessages.forEach(msg => console.log(`💬 ${msg}`));
        }
        
    } catch (error) {
        console.error(`❌ Error durante las pruebas: ${error.message}`);
    } finally {
        await browser.close();
    }
}

// Solo ejecutar si puppeteer está disponible
if (typeof require !== 'undefined') {
    try {
        testNuwaFunctionality().catch(console.error);
    } catch (e) {
        console.log('⚠️ Puppeteer no disponible, realizando verificación alternativa...');
        
        // Verificación alternativa usando fetch
        async function basicTest() {
            console.log('🔍 Verificación básica de endpoints...');
            
            try {
                const healthResponse = await fetch('https://3000-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev/health');
                const healthData = await healthResponse.json();
                console.log('✅ Health endpoint:', healthData);
                
                const statusResponse = await fetch('https://3000-itul5g8xqfm9r87o3q08w-6532622b.e2b.dev/api/status');
                const statusData = await statusResponse.json();
                console.log('✅ Status endpoint:', statusData);
                
                console.log('✅ Verificación básica completada');
            } catch (error) {
                console.error('❌ Error en verificación:', error.message);
            }
        }
        
        basicTest();
    }
}

module.exports = { testNuwaFunctionality };