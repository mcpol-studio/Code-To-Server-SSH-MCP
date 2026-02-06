# ssh_client.py
import paramiko
import io

def create_ssh_client(host, port, username, password=None, private_key=None, private_key_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    pkey = None
    if private_key:
        pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key))
    elif private_key_file:
         pkey = paramiko.RSAKey.from_private_key_file(private_key_file)

    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        pkey=pkey
    )
    return client
