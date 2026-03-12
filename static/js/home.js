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
    // Load home KPIs
    fetch("/api/home-kpis")
        .then(res => res.json())
        .then(data => {
            // Population data
            document.getElementById("kpi-total").innerText =
                formatIndianNumber(data.total_population);
            
            document.getElementById("kpi-male-pop").innerText =
                formatIndianNumber(data.male_population);
                
            document.getElementById("kpi-female-pop").innerText =
                formatIndianNumber(data.female_population);

            // Calculate crime rate per 100K
            const crimeRate = Math.round((data.total_arrests / data.total_population) * 100000);
            document.getElementById("kpi-crime-rate").innerText = formatIndianNumber(crimeRate);
            
            // Set total arrests
            document.getElementById("kpi-total-arrests").innerText = 
                data.total_arrests ? formatIndianNumber(data.total_arrests) : "Loading...";
        })
        .catch(err => {
            console.error("Home KPI error:", err);
            // Set fallback values
            document.getElementById("kpi-total").innerText = "50M+";
            document.getElementById("kpi-male-pop").innerText = "26M+";
            document.getElementById("kpi-female-pop").innerText = "24M+";
            document.getElementById("kpi-total-arrests").innerText = "2.5M+";
            document.getElementById("kpi-crime-rate").innerText = "5,000";
        });

    // Load gender ratio
    fetch("/api/gender-ratio?year=all")
        .then(res => res.json())
        .then(data => {
            document.getElementById("kpi-gender-ratio").innerText =
                `${data.ratio} : 1`;
        })
        .catch(err => {
            console.error("Gender ratio error:", err);
            document.getElementById("kpi-gender-ratio").innerText = "4.2 : 1";
        });

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
