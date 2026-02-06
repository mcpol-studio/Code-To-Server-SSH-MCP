import os
import io
import stat
from ssh_client import create_ssh_client

def upload_from_string(host, port, username, password, private_key, remote_path, content):
    client = None
    sftp = None
    try:
        client = create_ssh_client(host, port, username, password, private_key=private_key)
        sftp = client.open_sftp()
        
        file_obj = io.BytesIO(content.encode('utf-8'))
        sftp.putfo(file_obj, remote_path)
        
        return f"Successfully uploaded content to {remote_path} on {host}"
    except Exception as e:
        return f"Error uploading content: {str(e)}"
    finally:
        if sftp: sftp.close()
        if client: client.close()

def execute_command(host, port, username, password, private_key, command):
    client = None
    try:
        client = create_ssh_client(host, port, username, password, private_key=private_key)
        stdin, stdout, stderr = client.exec_command(command)
        
        exit_status = stdout.channel.recv_exit_status()
        out_str = stdout.read().decode('utf-8')
        err_str = stderr.read().decode('utf-8')
        
        result = f"Command exited with status {exit_status}\n"
        if out_str: result += f"STDOUT:\n{out_str}\n"
        if err_str: result += f"STDERR:\n{err_str}\n"
            
        return result
    except Exception as e:
        return f"Error executing command: {str(e)}"
    finally:
        if client: client.close()

def _ensure_remote_dir(sftp, remote_dir):
    """Recursively ensure remote directory exists."""
    if remote_dir == '/':
        sftp.chdir('/')
        return
    if remote_dir == '':
        return
        
    try:
        sftp.chdir(remote_dir)
    except IOError:
        dirname, basename = os.path.split(remote_dir.rstrip('/'))
        _ensure_remote_dir(sftp, dirname)
        try:
            sftp.mkdir(basename)
            sftp.chdir(basename)
        except IOError:
            # Handle concurrent creation or other errors gracefully
            pass

def _upload_dir_recursive(sftp, local_dir, remote_dir):
    """Recursively upload a directory."""
    # Ensure remote base directory exists
    _ensure_remote_dir(sftp, remote_dir)
    
    # We need to go back to root or keep track of absolute paths because ensure_remote_dir changes cwd
    # Simpler strategy: use absolute paths for put/mkdir and don't rely on chdir for state
    
    # Iterate walk
    for root, dirs, files in os.walk(local_dir):
        # Calculate relative path from local_dir
        rel_path = os.path.relpath(root, local_dir)
        if rel_path == ".":
            current_remote_base = remote_dir
        else:
            current_remote_base = os.path.join(remote_dir, rel_path).replace("\\", "/")

        # Create remote directories
        for d in dirs:
            remote_subdir = os.path.join(current_remote_base, d).replace("\\", "/")
            try:
                sftp.stat(remote_subdir)
            except IOError:
                sftp.mkdir(remote_subdir)

        # Upload files
        for f in files:
            local_file_path = os.path.join(root, f)
            remote_file_path = os.path.join(current_remote_base, f).replace("\\", "/")
            sftp.put(local_file_path, remote_file_path)

def upload_local_path(host, port, username, password, private_key, local_path, remote_path):
    client = None
    sftp = None
    try:
        if not os.path.exists(local_path):
            return f"Error: Local path '{local_path}' does not exist."

        client = create_ssh_client(host, port, username, password, private_key=private_key)
        sftp = client.open_sftp()
        
        if os.path.isfile(local_path):
            # If remote path looks like a directory, append filename
            if remote_path.endswith('/') or remote_path.endswith('\\'):
                 remote_path = os.path.join(remote_path, os.path.basename(local_path)).replace("\\", "/")
            
            # Ensure parent directory exists
            parent_dir = os.path.dirname(remote_path.rstrip('/'))
            _ensure_remote_dir(sftp, parent_dir)
            sftp.chdir('/') # Reset CWD just in case
            
            sftp.put(local_path, remote_path)
            return f"Successfully uploaded file '{local_path}' to '{remote_path}'"
            
        elif os.path.isdir(local_path):
            _upload_dir_recursive(sftp, local_path, remote_path)
            return f"Successfully uploaded directory '{local_path}' to '{remote_path}'"
            
    except Exception as e:
        import traceback
        return f"Error uploading local path: {str(e)}\n{traceback.format_exc()}"
    finally:
        if sftp: sftp.close()
        if client: client.close()

def upload_and_extract(host, port, username, password, private_key, local_path, remote_path, archive_format=None):
    client = None
    sftp = None
    remote_archive_path = None
    try:
        if not os.path.exists(local_path):
            return f"Error: Local path '{local_path}' does not exist."
            
        client = create_ssh_client(host, port, username, password, private_key=private_key)
        sftp = client.open_sftp()
        
        # Determine format
        if not archive_format:
            if local_path.lower().endswith('.zip'):
                archive_format = 'zip'
            elif local_path.lower().endswith('.tar.gz') or local_path.lower().endswith('.tgz'):
                archive_format = 'tar_gz'
            elif local_path.lower().endswith('.tar'):
                archive_format = 'tar'
            else:
                return "Error: Could not infer format. Please specify 'zip', 'tar', or 'tar_gz'."

        # 1. Ensure remote dest dir exists
        _ensure_remote_dir(sftp, remote_path)
        
        # 2. Upload archive to a temporary location inside the remote_path
        filename = os.path.basename(local_path)
        # Handle Windows paths in filename just in case, though basename should cover it
        remote_archive_path = os.path.join(remote_path, filename).replace("\\", "/")
        
        sftp.put(local_path, remote_archive_path)
        
        # 3. Extract
        cmd = ""
        if archive_format == 'zip':
            # unzip -o (overwrite) -d (dest)
            cmd = f"unzip -o '{remote_archive_path}' -d '{remote_path}'"
        elif archive_format == 'tar_gz':
            cmd = f"tar -xzf '{remote_archive_path}' -C '{remote_path}'"
        elif archive_format == 'tar':
            cmd = f"tar -xf '{remote_archive_path}' -C '{remote_path}'"
        else:
            return f"Error: Unsupported format '{archive_format}'"
            
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            err = stderr.read().decode('utf-8')
            return f"Error extracting: {err}"
            
        return f"Successfully uploaded and extracted '{local_path}' to '{remote_path}'"
        
    except Exception as e:
        import traceback
        return f"Error processing archive: {str(e)}\n{traceback.format_exc()}"
    finally:
        # Cleanup remote archive regardless of success/failure
        if sftp and remote_archive_path:
            try:
                sftp.remove(remote_archive_path)
            except:
                pass 
        if sftp: sftp.close()
        if client: client.close()
