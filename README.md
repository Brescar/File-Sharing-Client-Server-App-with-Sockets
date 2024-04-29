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

2. Open a new terminal and split it into two windows (Ctrl+Shift+5).  
    
    In the first window, write "python server.py" command (or "py server.py").

    In the second window, write "python client.py" command. Inside of this window, you have five possible commands: "connect", "list_my_files", "list_all_files", "download_files" and "disconnect".  

    In order to connect, write "connect username password" command (instead of username you have to write the value of your username and as for password you write the value of your password).

    Ex: "connect cristi cristi"

    At that moment, you will see that inside of "user_folder", the program will create a directory with the structured name "username_files" (for example, "cristi_folder"). There you can manually create a text file.

    To display the list of your files, write "list_my_files" command.

    To display the list of all files of all connected users, write "list_all_files" command.

    To download a file, you must write "download_file username filename" (username represents the value of your username and filename represents the of one of your created files). After that, press "Enter" and the downloaded file will be stored inside of "downloads" directory.

    And if you want to log out, just write "disconnect" command. 

3. PROFIT.
