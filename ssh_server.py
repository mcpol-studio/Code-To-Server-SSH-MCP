from mcp.server.fastmcp import FastMCP
from typing import Optional
import ssh_config
import ssh_ops

# Initialize FastMCP
mcp = FastMCP("ssh-tools")

@mcp.tool()
def ssh_upload_file(
    remote_path: str,
    content: str,
    host: str = ssh_config.HOST_DEFAULT,
    username: str = ssh_config.USERNAME_DEFAULT,
    port: int = ssh_config.PORT_DEFAULT,
    password: Optional[str] = ssh_config.PASSWORD_DEFAULT,
    private_key: Optional[str] = None
) -> str:
    """
    Upload a string content to a file on a remote server.
    
    Args:
        remote_path: Destination path on the remote server.
        content: Text content to write.
        host: Remote hostname or IP (Default: Hardcoded).
        username: SSH username (Default: Hardcoded).
        port: SSH port (default 22).
        password: SSH password (Default: Hardcoded).
        private_key: SSH private key content (optional).
    """
    return ssh_ops.upload_from_string(host, port, username, password, private_key, remote_path, content)

@mcp.tool()
def ssh_upload_local_path(
    local_path: str,
    remote_path: str,
    host: str = ssh_config.HOST_DEFAULT,
    username: str = ssh_config.USERNAME_DEFAULT,
    port: int = ssh_config.PORT_DEFAULT,
    password: Optional[str] = ssh_config.PASSWORD_DEFAULT,
    private_key: Optional[str] = None
) -> str:
    """
    Upload a local file OR directory to a remote server.
    If local_path is a directory, it will be uploaded recursively.
    
    Args:
        local_path: Absolute path to the local file or directory.
        remote_path: Destination path on the remote server.
        host: Remote hostname or IP (Default: Hardcoded).
        username: SSH username (Default: Hardcoded).
        port: SSH port (default 22).
        password: SSH password (Default: Hardcoded).
        private_key: SSH private key content (optional).
    """
    return ssh_ops.upload_local_path(host, port, username, password, private_key, local_path, remote_path)

@mcp.tool()
def ssh_upload_and_extract(
    local_path: str,
    remote_path: str,
    format: Optional[str] = None,
    host: str = ssh_config.HOST_DEFAULT,
    username: str = ssh_config.USERNAME_DEFAULT,
    port: int = ssh_config.PORT_DEFAULT,
    password: Optional[str] = ssh_config.PASSWORD_DEFAULT,
    private_key: Optional[str] = None
) -> str:
    """
    Upload a compressed archive (zip, tar, tar.gz) and extract it on the remote server.
    
    Args:
        local_path: Absolute path to local archive file.
        remote_path: Destination directory on remote server.
        format: Archive format ('zip', 'tar', 'tar_gz'). Optional, auto-detected from extension.
        host: Remote hostname or IP (Default: Hardcoded).
        username: SSH username (Default: Hardcoded).
        port: SSH port (default 22).
        password: SSH password (Default: Hardcoded).
        private_key: SSH private key content (optional).
    """
    return ssh_ops.upload_and_extract(host, port, username, password, private_key, local_path, remote_path, format)

@mcp.tool()
def ssh_exec_command(
    command: str,
    host: str = ssh_config.HOST_DEFAULT,
    username: str = ssh_config.USERNAME_DEFAULT,
    port: int = ssh_config.PORT_DEFAULT,
    password: Optional[str] = ssh_config.PASSWORD_DEFAULT,
    private_key: Optional[str] = None
) -> str:
    """
    Execute a shell command on a remote server using SSH.
    
    Args:
        command: Command to execute.
        host: Remote hostname or IP (Default: Hardcoded).
        username: SSH username (Default: Hardcoded).
        port: SSH port (default 22).
        password: SSH password (Default: Hardcoded).
        private_key: SSH private key content (optional).
    """
    return ssh_ops.execute_command(host, port, username, password, private_key, command)

if __name__ == "__main__":
    mcp.run()
