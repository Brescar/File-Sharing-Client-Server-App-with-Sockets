# File-Sharing-Client-Server-App-with-Sockets

## Description

File Sharing System: Authenticate, share, and manage files seamlessly across authenticated clients. Real-time notifications, downloads, and synchronized directories ensure efficient collaboration.

## Features

- **Authentication:** - ✔

  - The client authenticates through the account, sending the server a list of the files it publishes, and receives the list of all the files published by the other authenticated clients. ✔

- **Notifications:** - ✔

  - When a client authenticates, the other authenticated clients receive a notification of their addition, along with the list of files they publish. ✔

- **Files connected to client:** - ✔

  - When a client ends its session with the server, it confirms the end of the session and notifies the other authenticated clients to delete the respective client from the list. ✔

- **Request-based downloads:** - ✔

  - A client can request the server to download a file from other clients. ✔
  - The server requests the owner of the respective file to read its content. ✔
  - Afterwards, the server delivers the content of the file to the client who requested it. ✔

- **Local storage:** - ✔

  - The client saves the file in his file system. ✔

- **Monitored host directory with notifications:** - ✔
  - Each client will have an exposed host directory that will be monitored. ✔
  - When adding a new file to this directory, the client will notify the rest of the clients by means of the server of the addition of the file. ✔
  - When deleting a file from this directory, the client will similarly notify the other clients through the server. ✔

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/Brescar/File-Sharing-Client-Server-App-with-Sockets.git
   ```

2. ???

3. PROFIT.
