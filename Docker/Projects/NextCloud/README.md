# **How it works**
The setup consists of two Docker containers running together on the same network. The first container runs MariaDB which stores all Nextcloud metadata, users, and settings. The second container runs Nextcloud itself which serves the web interface on port 8080. Both containers communicate internally using Docker's built-in DNS, which means Nextcloud reaches the database simply by using the hostname db instead of an IP address.
All data is persisted using Docker volumes, meaning if a container stops or restarts, no data is lost.

# **External Storage**
Nextcloud is configured to connect to an external file server using the SMB/CIFS protocol. This means the actual files are stored on a separate file server, while Nextcloud acts as the interface for managing and accessing them. The smbclient library is installed inside the Nextcloud container to enable this connection.

## **Security Notes**
- Credentials are stored in a .env file which is excluded from version control via .gitignore
- The .env file permissions should be restricted using chmod 600 .env
- Never commit the .env file to GitHub


## **Requirements**
- Docker
- Docker Compose Plugin
- Access to the file server on the same network
