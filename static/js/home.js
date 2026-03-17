/* ---------------- INDIAN NUMBER FORMATTING ---------------- */
function formatIndianNumber(num) {
    if (num === 0) return '0';
    
    const numStr = Math.abs(num).toString();
    const isNegative = num < 0;
    
    // For numbers less than 1000, no formatting needed
    if (numStr.length <= 3) {
        return isNegative ? '-' + numStr : numStr;
    }
    
    // Split the number into groups: first 3 digits, then groups of 2
    let result = '';
    let remaining = numStr;
    
    // Handle the rightmost 3 digits
    if (remaining.length > 3) {
        result = ',' + remaining.slice(-3) + result;
        remaining = remaining.slice(0, -3);
    } else {
        result = remaining + result;
        remaining = '';
    }
    
    // Handle groups of 2 digits from right to left
    while (remaining.length > 0) {
        if (remaining.length <= 2) {
            result = remaining + result;
            break;
        } else {
            result = ',' + remaining.slice(-2) + result;
            remaining = remaining.slice(0, -2);
        }
    }
    
    return isNegative ? '-' + result : result;
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialize premium homepage features
    initTypewriterEffect();
    initCounterAnimations();
    initPremiumKPIs();
    initMiniCharts();
    
    // Typewriter effect for hero subtitle
    function initTypewriterEffect() {
        const texts = [
            "Advanced Metropolitan City Crime Analytics Platform",
            "Crime Intelligence Dashboard with AI", 
            "AI-Powered Crime Insights Engine",
            "Metropolitan City Crime Data Integration Hub"
        ];
        
        let textIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        const typewriterElement = document.getElementById('typewriter-text');
        
        if (!typewriterElement) return;
        
        function typeWriter() {
            const currentText = texts[textIndex];
            
            if (isDeleting) {
                typewriterElement.textContent = currentText.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typewriterElement.textContent = currentText.substring(0, charIndex + 1);
                charIndex++;
            }
            
            let typeSpeed = isDeleting ? 50 : 100;
            
            if (!isDeleting && charIndex === currentText.length) {
                typeSpeed = 2000;
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                textIndex = (textIndex + 1) % texts.length;
                typeSpeed = 500;
            }
            
            setTimeout(typeWriter, typeSpeed);
        }
        
        typeWriter();
    }
    
    // Animated counters for hero stats
    function initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number[data-target]');
        
        const animateCounter = (element) => {
            const target = parseInt(element.getAttribute('data-target'));
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                if (target > 1000000) {
                    element.textContent = (current / 1000000).toFixed(1) + 'M';
                } else if (target > 1000) {
                    element.textContent = (current / 1000).toFixed(0) + 'K';
                } else {
                    element.textContent = Math.floor(current);
                }
            }, 16);
        };
        
        // Intersection Observer for counter animation
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                    entry.target.classList.add('animated');
                    animateCounter(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => observer.observe(counter));
    }
    
    // Load premium KPIs with enhanced formatting
    function initPremiumKPIs() {
        fetch("/api/home-kpis")
            .then(res => res.json())
            .then(data => {
                // Update premium metric cards
                updateMetricCard("total-population", data.total_population);
                updateMetricCard("total-arrests", data.total_arrests);
                
                // Calculate and update crime rate
                const crimeRate = Math.round((data.total_arrests / data.total_population) * 100000);
                updateMetricCard("crime-rate", crimeRate);
                
                // Update floating cards
                updateFloatingCard("live-arrests", data.total_arrests);
            })
            .catch(err => {
                console.error("Premium KPI error:", err);
                // Set premium fallback values
                updateMetricCard("total-population", 52000000);
                updateMetricCard("total-arrests", 2500000);
                updateMetricCard("crime-rate", 4800);
                updateFloatingCard("live-arrests", 2500000);
            });
        
        // Load gender ratio for premium display
        fetch("/api/gender-ratio?year=all")
            .then(res => res.json())
            .then(data => {
                updateMetricCard("gender-ratio", `${data.ratio}:1`);
            })
            .catch(err => {
                console.error("Gender ratio error:", err);
                updateMetricCard("gender-ratio", "4.2:1");
            });
    }
    
    function updateMetricCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            if (typeof value === 'number' && value > 1000) {
                element.textContent = formatIndianNumber(value);
            } else {
                element.textContent = value;
            }
            
            // Add animation class
            element.classList.add('metric-updated');
            setTimeout(() => element.classList.remove('metric-updated'), 1000);
        }
    }
    
    function updateFloatingCard(id, value) {
        const element = document.getElementById(id);
        if (element && typeof value === 'number') {
            element.textContent = formatIndianNumber(value);
        }
    }
    
    // Initialize mini charts for metric cards
    function initMiniCharts() {
        const chartConfigs = [
            { id: 'population-chart', data: [45, 52, 48, 61, 55, 67], color: '#3b82f6' },
            { id: 'arrests-chart', data: [28, 35, 42, 38, 45, 40], color: '#10b981' },
            { id: 'rate-chart', data: [15, 25, 35, 28, 40, 32], color: '#f59e0b' },
            { id: 'gender-chart', data: [20, 25, 30, 28, 35, 32], color: '#ef4444' }
        ];
        
        chartConfigs.forEach(config => {
            const canvas = document.getElementById(config.id);
            if (canvas) {
                createMiniChart(canvas, config.data, config.color);
            }
        });
    }
    
    function createMiniChart(canvas, data, color) {
        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['2016', '2017', '2018', '2019', '2020', '2021'],
                datasets: [{
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: { point: { radius: 0 } }
            }
        });
    }

    // Floating menu is now always visible - removed scroll logic

    // Add smooth scrolling for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all sections for animation
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });

    // Add counter animation for metrics
    const animateCounter = (element, target, duration = 2000) => {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = formatIndianNumber(Math.floor(current));
        }, 16);
    };

    // Animate hero stats when they come into view
    const heroStats = document.querySelectorAll('.hero-stat .stat-number');
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                entry.target.classList.add('animated');
                const target = parseInt(entry.target.textContent.replace(/[^0-9]/g, ''));
                if (!isNaN(target)) {
                    animateCounter(entry.target, target);
                }
            }
        });
    }, { threshold: 0.5 });

    heroStats.forEach(stat => {
        // Only animate numeric values, skip "15+" and "5" which are static
        const text = stat.textContent.trim();
        if (!text.includes('+') && !isNaN(parseInt(text))) {
            heroObserver.observe(stat);
        }
    });
});

// Floating menu toggle function
function toggleFloatingNav() {
    const menuToggle = document.querySelector('.menu-toggle');
    const floatingNav = document.getElementById('floating-nav');
    
    menuToggle.classList.toggle('active');
    floatingNav.classList.toggle('active');
}

// Enhanced chatbot toggle with welcome message for home page
function toggleAssistant(event) {
    if (event) {
        event.preventDefault();
    }
    
    const overlay = document.getElementById('assistant-overlay');
    const panel = document.getElementById('assistant-panel');
    const body = document.body;
    
    if (panel.classList.contains('active')) {
        // Close chatbot
        panel.classList.remove('active');
        overlay.classList.remove('active');
        body.classList.remove('no-scroll');
    } else {
        // Open chatbot with home page welcome message
        panel.classList.add('active');
        overlay.classList.add('active');
        body.classList.add('no-scroll');
        
        // Add a welcome message specific to home page
        const assistantBody = document.getElementById('assistantBody');
        const isHomePage = window.location.pathname === '/' || window.location.pathname === '/home';
        
        if (isHomePage && !assistantBody.querySelector('.home-welcome')) {
            const welcomeMessage = document.createElement('div');
            welcomeMessage.className = 'assistant-bot home-welcome';
            welcomeMessage.innerHTML = `
                <strong>🎉 Welcome to the AI Crime Analytics Assistant!</strong><br><br>
                Try asking me questions like:<br>
                • "Compare Delhi and Mumbai crime rates"<br>
                • "Show me top 5 cities by arrests"<br>
                • "What's the trend for Bangalore?"<br>
                • "Male vs female arrests in Chennai"
            `;
            assistantBody.appendChild(welcomeMessage);
            
            // Scroll to bottom to show the new message
            assistantBody.scrollTop = assistantBody.scrollHeight;
        }
        
        // Focus on input
        setTimeout(() => {
            document.getElementById('assistantInput').focus();
        }, 300);
    }
}

// Close floating menu when clicking outside
document.addEventListener('click', (e) => {
    const floatingMenu = document.getElementById('floating-menu');
    const floatingNav = document.getElementById('floating-nav');
    
    if (floatingMenu && !floatingMenu.contains(e.target)) {
        document.querySelector('.menu-toggle').classList.remove('active');
        floatingNav.classList.remove('active');
    }
});
    
    // Enhanced intersection observer for premium animations
    const premiumObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Special handling for metric cards
                if (entry.target.classList.contains('metric-card-premium')) {
                    setTimeout(() => {
                        entry.target.style.transform = 'translateY(0) scale(1)';
                        entry.target.style.opacity = '1';
                    }, 100);
                }
            }
        });
    }, { 
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observe premium elements
    document.querySelectorAll('.metric-card-premium, .feature-card-premium, .tech-card-premium').forEach(element => {
        premiumObserver.observe(element);
    });

    // Add premium hover effects
    document.querySelectorAll('.btn-premium').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Premium particle effect on scroll - SIMPLIFIED FOR BETTER PERFORMANCE
    let ticking = false;
    
    function updateParticles() {
        const scrolled = window.pageYOffset;
        const parallax = scrolled * 0.2; // Reduced intensity
        
        // Only update if user prefers motion
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.querySelectorAll('.floating-shapes .shape').forEach((shape, index) => {
                const speed = (index + 1) * 0.05; // Reduced speed
                shape.style.transform = `translateY(${parallax * speed}px)`;
            });
        }
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateParticles);
            ticking = true;
        }
    }
    
    // Only add scroll listener if motion is preferred
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.addEventListener('scroll', requestTick, { passive: true });
    }

    // Premium smooth scrolling - SIMPLIFIED
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Premium Loading Screen
    window.addEventListener('load', () => {
    const loader = document.querySelector('.premium-loader');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
            setTimeout(() => loader.remove(), 500);
        }, 1000);
    }
});

// Enhanced chatbot toggle for premium experience
function toggleAssistant(event) {
    if (event) {
        event.preventDefault();
    }
    
    const overlay = document.getElementById('assistant-overlay');
    const panel = document.getElementById('assistant-panel');
    const body = document.body;
    
    if (panel.classList.contains('active')) {
        // Close with premium animation
        panel.style.transform = 'translateX(120%) scale(0.9)';
        overlay.style.opacity = '0';
        
        setTimeout(() => {
            panel.classList.remove('active');
            overlay.classList.remove('active');
            body.classList.remove('no-scroll');
        }, 300);
    } else {
        // Open with premium animation
        panel.classList.add('active');
        overlay.classList.add('active');
        body.classList.add('no-scroll');
        
        // Add premium welcome message
        const assistantBody = document.getElementById('assistantBody');
        const isHomePage = window.location.pathname === '/' || window.location.pathname === '/home';
        
        if (isHomePage && !assistantBody.querySelector('.premium-welcome')) {
            const welcomeMessage = document.createElement('div');
            welcomeMessage.className = 'assistant-bot premium-welcome';
            welcomeMessage.innerHTML = `
                <div class="premium-welcome-card">
                    <div class="welcome-icon">🚀</div>
                    <h3>Welcome to Metropolitan Cities AI Analytics!</h3>
                    <p>Experience next-generation metropolitan crime data analysis with our advanced AI chatbot assistant.</p>
                    <div class="welcome-features">
                        <span class="feature-tag">🧠 Machine Learning</span>
                        <span class="feature-tag">📊 Real-time Analytics</span>
                        <span class="feature-tag">🎯 Predictive Insights</span>
                    </div>
                    <div class="welcome-examples">
                        <strong>Try these metropolitan city queries:</strong><br>
                        • "Compare crime trends in Delhi vs Mumbai"<br>
                        • "Show me metropolitan crime patterns analysis"<br>
                        • "Generate insights for metro city policy makers"<br>
                        • "What are the emerging crime hotspots in major cities?"
                    </div>
                </div>
            `;
            assistantBody.appendChild(welcomeMessage);
            assistantBody.scrollTop = assistantBody.scrollHeight;
        }
        
        setTimeout(() => {
            document.getElementById('assistantInput').focus();
        }, 400);
    }
}

// Premium Performance Monitoring
const performanceMonitor = {
    init() {
        this.measurePageLoad();
        this.measureAnimationPerformance();
    },
    
    measurePageLoad() {
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            console.log(`Premium page loaded in ${loadTime.toFixed(2)}ms`);
            
            // Report to analytics if needed
            if (loadTime > 3000) {
                console.warn('Page load time exceeds 3 seconds');
            }
        });
    },
    
    measureAnimationPerformance() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        function countFrames() {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = frameCount;
                frameCount = 0;
                lastTime = currentTime;
                
                if (fps < 30) {
                    console.warn(`Low FPS detected: ${fps}`);
                }
            }
            
            requestAnimationFrame(countFrames);
        }
        
        requestAnimationFrame(countFrames);
    }
};

// Initialize premium features
performanceMonitor.init();
    // Make feature cards fully clickable
    document.querySelectorAll('.feature-card-premium').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on the feature button directly or feature stats
            if (e.target.closest('.feature-btn') || e.target.closest('.feature-stats')) {
                return;
            }
            
            // Find the link within the card
            const link = this.querySelector('.feature-btn');
            if (link) {
                // Check if it's an onclick handler or href
                if (link.onclick) {
                    link.onclick(e);
                } else if (link.href) {
                    window.location.href = link.href;
                }
            }
        });
        
        // Disable visual feedback (hover effects disabled)
        // card.addEventListener('mouseenter', function() {
        //     this.style.cursor = 'pointer';
        // });
    });

    // Add click animation to quick nav links
    document.querySelectorAll('.quick-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.3)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.left = (e.clientX - this.offsetLeft) + 'px';
            ripple.style.top = (e.clientY - this.offsetTop) + 'px';
            
            this.style.position = 'relative';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);