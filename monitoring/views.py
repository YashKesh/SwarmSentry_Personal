from django.shortcuts import render
from django.shortcuts import redirect

import docker
from datetime import datetime, timedelta
from django.utils import timezone
# Create your views here.
def homepage(request):
    return render(request,"firstboard.html")

from django.http import JsonResponse
import docker

def list_docker_images(request):
    client = docker.from_env()
    try:
        # Get a list of all Docker images
        images = client.images.list()
        # Get the total number of Docker images
        total_images = len(images)

        # Get a list of all Docker containers
        containers = client.containers.list(all=True)
        # Get the total number of Docker containers
        total_containers = len(containers)
        # Get the total number of running containers
        running_containers = sum(1 for container in containers if container.status == 'running')
        stopped_containers = sum(1 for container in containers if container.status == 'exited')
        # Extract image details
        image_details = []
        current_time = timezone.now()
        for image in images:
            image_id = image.short_id.split(':')[1][:10]

            # Convert image size to MB
            image_size = round(image.attrs['Size'] / (1024 * 1024), 2)
            created_time = datetime.strptime(image.attrs['Created'], '%Y-%m-%dT%H:%M:%SZ')
            created_time = timezone.make_aware(created_time)  # Make the datetime object timezone-aware
            time_difference = current_time - created_time
            days_ago = time_difference.days
            image_info = {
                'repository': image.tags[0] if image.tags else '',
                'id': image_id,
                'size': f"{image_size} MB",
                 'created': f"{days_ago} days ago"
            }
            image_details.append(image_info)
        return render(request, 'firstboard.html', {'images': image_details, 'total_images': total_images, 'total_containers': total_containers,'running_containers':running_containers,'stopped_containers':stopped_containers})
    except docker.errors.APIError as e:
        return render(request, 'firstboard.html', {'error': str(e)})
    except Exception as e:
        return render(request, 'firstboard.html', {'error': str(e)})



# views.py
# views.py
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import docker

def pull_image(request):
    if request.method == 'POST':
        image_name = request.POST.get('image_name')
        print("Received image name:", image_name)  # Debug statement
        try:
            client = docker.from_env()
            pulled_image = client.images.pull(image_name)
            return redirect('homepage')
        except docker.errors.ImageNotFound as e:
            return JsonResponse({'error': f"Image '{image_name}' not found."}, status=404)
        except docker.errors.APIError as e:
            return JsonResponse({'error': f"Failed to pull image '{image_name}'. Reason: {e}"}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

from django.shortcuts import render
import docker

def container_list(request, repository):
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Get a list of all containers
        containers = client.containers.list(all=True)
        # Filter containers by image repository
        image_containers = [container for container in containers if repository in container.image.tags]
        
        # Process containers to trim ID and convert created time to "hours ago" format
        for container in image_containers:
             # Trim the container ID to 10 characters
            
            # Parse the creation time string into a datetime object
            created_time = datetime.strptime(container.attrs['Created'][:19], '%Y-%m-%dT%H:%M:%S')
            
            # Calculate the time difference between current time and creation time
            time_difference = datetime.utcnow() - created_time
            
            # Extract the number of hours
            hours_ago = int(time_difference.total_seconds() / 3600)
            
            # Format the "hours ago" string
            container.created_ago = f"{hours_ago} hours ago"
        
        return render(request, 'container_list.html', {'repository': repository, 'containers': image_containers})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
    
def page_title(request):
    # Get the title of the HTML page
    title = getattr(request, '_title', '')
    return {'page_title': title}


from django.shortcuts import redirect

from django.urls import reverse
from django.urls import reverse
from django.http import HttpResponseRedirect

def create_container(request):
    if request.method == 'POST':
        repository = request.POST.get('repository')
        try:
            # Connect to the Docker daemon
            client = docker.from_env()
            # Create and run the container
            container = client.containers.run(repository, detach=True)
            # Construct the URL for the container list page
            container_list_url = reverse('container_list', kwargs={'repository': repository})
            # Redirect to the container list page for the specific image
            return HttpResponseRedirect(container_list_url)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    
from django.urls import reverse
from django.http import HttpResponseRedirect

def start_container(request, container_id):
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.start()
        return JsonResponse({'status': 'success'})
    except docker.errors.APIError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def stop_container(request, container_id):
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.stop()
        return JsonResponse({'status': 'success'})
    except docker.errors.APIError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def delete_container(request, container_id):
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.remove(force=True)
        return JsonResponse({'status': 'success'})
    except docker.errors.APIError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

from django.http import JsonResponse

def delete_image(request):
    if request.method == 'POST':
        repository = request.POST.get('repository')
        try:
            client = docker.from_env()
            # Remove image from Docker
            client.images.remove(repository, force=True)
            return JsonResponse({'status': 'success'})
        except docker.errors.APIError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# views.py
import docker
from django.shortcuts import render
from django.http import JsonResponse

def all_containers(request):
    try:
        # Connect to the Docker daemon
        client = docker.from_env()
        # Get a list of all containers
        containers = client.containers.list(all=True)
        # Prepare container information
        container_info = []
        for container in containers:
            # Parse the creation time string into a datetime object
            created_time = datetime.strptime(container.attrs['Created'][:19], '%Y-%m-%dT%H:%M:%S')
            
            # Calculate the time difference between current time and creation time
            time_difference = datetime.utcnow() - created_time
            
            # Extract the number of hours
            hours_ago = int(time_difference.total_seconds() / 3600)
            
            # Format the "hours ago" string
            container.created_ago = f"{hours_ago} hours ago"
            container_info.append({
                'id': container.short_id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0],
                'created': container.attrs['Created'],
                'created_ago': container.created_ago,

            })
        return render(request, 'allcontainers.html', {'containers': container_info})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})







