## Install Redmine using Docker
1. Create Project Directory
- sudo mkdir -p /opt/redmine
- cd /opt/redmine

2. Create docker-compose.yml

Create a file named docker-compose.yml and add the following configuration:
```yaml
services:
  postgres:
    image: postgres:16
    container_name: redmine_postgres
    restart: always
    environment:
      POSTGRES_DB: redmine
      POSTGRES_USER: redmine
      POSTGRES_PASSWORD: StrongPassword123!
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - redmine_network

  redmine:
    image: redmine:5.1
    container_name: redmine_app
    restart: always
    depends_on:
      - postgres
    environment:
      REDMINE_DB_POSTGRES: postgres
      REDMINE_DB_DATABASE: redmine
      REDMINE_DB_USERNAME: redmine
      REDMINE_DB_PASSWORD: StrongPassword123!
      REDMINE_SECRET_KEY_BASE: supersecretkey123changethis
    volumes:
      - redmine_files:/usr/src/redmine/files
      - redmine_plugins:/usr/src/redmine/plugins
      - redmine_themes:/usr/src/redmine/public/themes
    ports:
      - "3000:3000"
    networks:
      - redmine_network

volumes:
  postgres_data:
  redmine_files:
  redmine_plugins:
  redmine_themes:

networks:
  redmine_network:
    driver: bridge
```
3. Start the Containers

Run the following command to start Redmine and PostgreSQL:

docker compose up -d

Verify that the containers are running:

docker ps
🌐 Step 04: Configure Nginx Reverse Proxy
1. Install Nginx
sudo apt update
sudo apt install -y nginx
2. Create Nginx Configuration
sudo nano /etc/nginx/sites-available/redmine

Paste the following configuration:

server {
    listen 80;
    server_name 192.168.1.17;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:3000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
3. Enable the Configuration
sudo ln -s /etc/nginx/sites-available/redmine /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
4. Test the Configuration
sudo nginx -t

Expected output:

nginx: configuration file /etc/nginx/nginx.conf test is successful
5. Restart Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
✅ Access Redmine

Open your browser and navigate to:

http://192.168.1.17

If everything is configured correctly, the Redmine login page should appear.
