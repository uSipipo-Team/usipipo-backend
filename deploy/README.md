# uSipipo Backend - Deployment Guide

This directory contains deployment configuration files for production environments.

## Systemd Service

### Setup Instructions

1. **Copy the service file:**
   ```bash
   sudo cp deploy/usipipo-backend.service.example /etc/systemd/system/usipipo-backend.service
   ```

2. **Edit the service file:**
   Replace all placeholders (marked with `<PLACEHOLDER>`) with your actual values:
   - `<SYSTEM_USER>` - System user to run the service (e.g., `usipipo`, `www-data`)
   - `<SYSTEM_GROUP>` - System group (e.g., `usipipo`, `www-data`)
   - `<PATH_TO_USISIPO_BACKEND>` - Full path to backend directory (e.g., `/opt/usipipo/usipipo-backend`)
   - `<PATH_TO_VENV>` - Path to Python virtual environment
   - `<DB_USER>`, `<DB_PASSWORD>`, `<DB_HOST>`, `<DB_PORT>`, `<DB_NAME>` - Database credentials
   - `<YOUR_SECRET_KEY>` - Your application secret key
   - `<REDIS_HOST>`, `<REDIS_PORT>`, `<REDIS_DB>` - Redis configuration

3. **Create logs directory:**
   ```bash
   sudo mkdir -p /opt/usipipo/usipipo-backend/logs
   sudo chown usipipo:usipipo /opt/usipipo/usipipo-backend/logs
   ```

4. **Reload systemd and enable service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable usipipo-backend
   sudo systemctl start usipipo-backend
   ```

5. **Check service status:**
   ```bash
   sudo systemctl status usipipo-backend
   ```

6. **View logs:**
   ```bash
   sudo journalctl -u usipipo-backend -f
   ```

### Service Management Commands

```bash
# Start service
sudo systemctl start usipipo-backend

# Stop service
sudo systemctl stop usipipo-backend

# Restart service
sudo systemctl restart usipipo-backend

# Reload configuration (if supported)
sudo systemctl reload usipipo-backend

# Check status
sudo systemctl status usipipo-backend

# View logs
sudo journalctl -u usipipo-backend -f
sudo journalctl -u usipipo-backend --since "1 hour ago"

# Enable on boot
sudo systemctl enable usipipo-backend

# Disable on boot
sudo systemctl disable usipipo-backend
```

### Environment Variables

The service loads environment variables from `.env` file. See `example.env` in the root directory for all available options.

### Security Notes

- The service runs with hardened security settings (`ProtectSystem=strict`, `PrivateTmp=true`, etc.)
- Ensure the `.env` file has restricted permissions: `chmod 600 .env`
- Use a dedicated system user with minimal privileges
- Keep the virtual environment and application code read-only for the service user

## Docker Deployment

For Docker-based deployments, see `docker-compose.yml` and `Dockerfile` in the root directory.
