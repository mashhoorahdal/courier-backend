# Courier Backend API

A Django REST API for courier management system with JWT authentication, order tracking, and admin interface.

## Features

- **JWT Authentication** - Secure token-based authentication
- **Order Management** - Create, update, and track orders
- **Automatic Barcodes** - Unique CO-XXXXXXXXXXXX format barcodes
- **Status Management** - Validated order status transitions
- **Payment Processing** - Mark orders as paid/refunded
- **Public Tracking** - Track orders by barcode without authentication
- **Admin Interface** - Full Django admin for order management
- **CORS Support** - Configured for frontend integration
- **Production Ready** - Security settings and logging configured

## API Endpoints

### Authentication
- `POST /api/v1/token/` - Obtain JWT tokens
- `POST /api/v1/token/refresh/` - Refresh access token
- `POST /api/v1/register/` - User registration

### Orders
- `GET /api/v1/orders/` - List user's orders
- `POST /api/v1/orders/` - Create new order
- `PATCH /api/v1/orders/{id}/status/` - Update order status
- `PATCH /api/v1/orders/{id}/payment/` - Process payments

### Public
- `GET /api/v1/track/{barcode}/` - Track order by barcode
- `GET /api/v1/` - API information

### Admin
- `/admin/` - Django admin interface

## Local Development

### Prerequisites
- Docker and Docker Compose
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd courier-backend

# Start the services
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
```

### Testing the API
```bash
# Check API root
curl http://localhost:8000/api/v1/

# Register a user
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}' \
  http://localhost:8000/api/v1/register/

# Get JWT token
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  http://localhost:8000/api/v1/token/
```

## Deployment to Render

### Prerequisites
- Render account
- GitHub repository

### Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint" or "Web Service"
   - Connect your GitHub repository

3. **Configure the Service**
   - **Name**: `courier-backend`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: Free or Paid (as needed)

4. **Environment Variables**
   ```
   DEBUG=false
   SECRET_KEY=<generate-a-secure-key>
   DJANGO_ALLOWED_HOSTS=<your-render-domain>
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

5. **Database Setup**
   - In Render, create a PostgreSQL database
   - Copy the `DATABASE_URL` from database settings
   - Add it to your service environment variables

6. **Deploy**
   - Render will automatically build and deploy
   - The first deployment runs migrations automatically
   - Create a superuser after deployment:
   ```bash
   # Connect to your deployed service shell
   render shell
   python manage.py createsuperuser
   ```

### Post-Deployment

1. **Update CORS settings** with your frontend domain
2. **Test all endpoints** with the production URL
3. **Set up monitoring** if needed
4. **Configure backups** for the database

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable/disable debug mode | `True` |
| `SECRET_KEY` | Django secret key | Generated |
| `DATABASE_URL` | PostgreSQL connection string | SQLite |
| `DJANGO_ALLOWED_HOSTS` | Allowed host domains | `*` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `localhost:3000` |

## Project Structure

```
courier-backend/
├── courier/                 # Main app
│   ├── models.py           # Order model
│   ├── views.py            # API views
│   ├── serializers.py      # Data serializers
│   ├── urls.py             # App URLs
│   └── admin.py            # Admin configuration
├── courier_backend/         # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI application
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Local development
├── render.yaml            # Render deployment
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Security Features

- **JWT Authentication** with configurable token lifetimes
- **CORS Protection** with configurable allowed origins
- **HTTPS Enforcement** in production
- **Secure Cookies** and CSRF protection
- **Input Validation** on all API endpoints
- **SQL Injection Protection** via Django ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
