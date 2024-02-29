# import docker

# def stop_container(container_id):
#     try:
#         # Initialize the Docker client
#         client = docker.from_env()

#         # Get the container object
#         container = client.containers.get(container_id)

#         # Stop the container
#         container.stop()

#         print(f"Container {container_id} stopped successfully.")
#     except docker.errors.NotFound:
#         print(f"Container {container_id} not found.")
#     except docker.errors.APIError as e:
#         print(f"Error stopping container: {e}")

# # Example usage:
# container_id = "3845f971d2"
# stop_container(container_id)


import subprocess

def start_container(container_id):
    try:
        # Run the docker start command using subprocess
        subprocess.run(['docker', 'start', container_id], check=True)
        print(f"Container {container_id} started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting container: {e}")

# Example usage:
container_id = "3845f971d22b"
start_container(container_id)

