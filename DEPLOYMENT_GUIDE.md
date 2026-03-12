# Deployment Guide - Crime Analytics Dashboard

## 🚀 Production Deployment

### Prerequisites
- Python 3.8+
- pip package manager
- Git
- Web server (Apache/Nginx) or cloud platform

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd crime-analytics-dashboard
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python app.py
# Database will be created automatically
```

6. **Run the application**
```bash
# Development
python app.py

# Production with Gunicorn
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `DATABASE_URL` | Database connection | `sqlite:///feedback.db` |
| `GROQ_API_KEY` | Groq API key for LLM | Required |
| `DEBUG` | Debug mode | `False` |

### Cloud Deployment

#### Heroku
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GROQ_API_KEY=your-groq-key
git push heroku main
```

#### AWS/GCP/Azure
- Use the provided `wsgi.py` file
- Configure environment variables
- Set up load balancer and SSL certificate
- Configure logging and monitoring

### Security Checklist

- [x] Secret key configured
- [x] Debug mode disabled
- [x] Security headers implemented
- [x] Input validation in place
- [x] SQL injection protection
- [x] XSS protection
- [x] CSRF protection
- [x] HTTPS enforcement

### Performance Optimization

- [x] Query caching implemented
- [x] Static file optimization
- [x] Database query optimization
- [x] Pagination for large datasets
- [x] Efficient data structures

### Monitoring & Logging

- Application logs: `logs/app.log`
- Error tracking: Built-in Flask error handlers
- Performance monitoring: Built-in metrics
- Health check endpoint: `/api/health-check`

### Backup & Recovery

- Database: SQLite file backup
- Static files: Version controlled
- Configuration: Environment variables
- Data files: CSV files in `data/` directory

### Troubleshooting

#### Common Issues

1. **Import errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility

2. **Database errors**
   - Verify database file permissions
   - Check disk space

3. **API errors**
   - Verify Groq API key
   - Check network connectivity

4. **Performance issues**
   - Monitor memory usage
   - Check query performance
   - Review caching configuration

### Support

For technical support or questions:
- Check the documentation in `/docs`
- Review error logs in `/logs`
- Submit feedback through the application
- Contact the development team

### Version Information

- Application Version: 1.0.0
- Python Version: 3.8+
- Flask Version: 3.0.3
- Last Updated: January 2026