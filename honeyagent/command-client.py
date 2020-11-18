def listen_for_commands():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("listening for commands")
            s.bind(('127.0.0.1',HONEYNODE_COMMAND_PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Command received from {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                data = data.decode('utf-8')
                data = json.loads(data)
                print(data)
                """
                    the command should look like 
                    {"command" : "handshake"}
                """
    except socket.error as e:
        print(f"Error creating commmand Socket\n {e}")