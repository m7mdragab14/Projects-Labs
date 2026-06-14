## Step 01: Deploy Redmine with Docker

In this step, Docker Compose is used to deploy both the **Redmine application** and a **PostgreSQL database**.

The `docker-compose.yml` file defines:

* A PostgreSQL container to store Redmine data.
* A Redmine application container.
* Persistent Docker volumes to keep data even after restarting the containers.
* A dedicated Docker bridge network for communication between services.
* Port mapping to expose the Redmine web interface on port **3000**.

The complete configuration can be found in the `docker-compose.yml` file included in this repository.

### Start the application

Run the following command to create and start all containers in detached mode:

```bash
docker compose up -d
```

### Verify the deployment

You can verify that the containers are running successfully by executing:

```bash
docker ps
```

If everything is configured correctly, Redmine will be accessible on:

```
http://<SERVER_IP>:3000
```

## Step 02: Configure Nginx

The repository includes a preconfigured Nginx reverse proxy configuration file located at:

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/redmine
```
### nano /etc/nginx/sites-available/redmine

```text
nginx/redmine.conf

```bash
sudo ln -s /etc/nginx/sites-available/redmine /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```
