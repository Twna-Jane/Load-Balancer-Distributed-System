"""Utility functions for managing containers."""
import docker
import random
import re

def spawn_new_server(client: docker.DockerClient, server_name=None):
    """Create a new server container."""
    if server_name is not None:
        container_name = server_name
    else:
        # Generate a random server name if not provided
        tries = 0

        # Try to generate a unique server name
        while tries < 100:
            rand_id = random.randint(1000, 9999)
            container_name = f"server{rand_id}"
            if not get_container_by_name(client, container_name):
                break
            tries += 1
        if tries == 100:
            raise Exception("Failed to generate a unique server name.")

        server_name = container_name

    # Check if the container already exists
    existing = get_container_by_name(client, container_name)
    if existing:
        if existing.status == 'exited':
            print(f"Container {container_name} exists but is stopped. Restarting...")
            existing.start()
        else:
            print(f"Container {container_name} already running.")
        return f"{container_name}:5000"

    # Get the server_id from the container name
    server_id = extract_server_id(container_name)

    # Spawn the new server
    container = client.containers.run(
        image="myserver:latest",
        name=container_name,
        environment={"SERVER_ID": server_id},
        network="lb_network",
        detach=True
    )
    
    return f"{container_name}:5000"

def remove_server_container(client: docker.DockerClient, container_name: str):
    """Remove server container."""
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        print(f"Container {container_name} does not exist.")
    except docker.errors.APIError as e:
        print(f"Failed to remove container {container_name}: {e}")


def get_container_by_name(client: docker.DockerClient, container_name: str):
    """Get a Docker container by its name."""
    try:
        return client.containers.get(container_name)
    except docker.errors.NotFound:
        return None

def extract_container_name(server_name: str):
    return server_name.split(":")[0]

def extract_server_id(container_name):
    match = re.search(r'(\d+)$', container_name)
    if match:
        return match.group(1)
    else:
        return container_name 
