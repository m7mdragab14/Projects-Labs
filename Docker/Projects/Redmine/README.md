## Step 03: Deploy Redmine with Docker

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
