# Broker Orchestrator Containers

A container administrator receiving actions through a broker. 
Messages sent through specific channels perform actions on the 
host machine's docker by the Docker SDK for Python

Actions can be anything, like: 
executing a function/script (something like google functions, aws lambda, etc) 
up/start/build specific container
monitoring some status

When running a container just to run a script/function, it is possible to 
inform a 'response_channel', which sends the stdout of the execution 
to some channel of the broker. For example, you can program to do 
something like Step Functions. From the output of this run, 
do this other run with this input, and run this one when it's finished, etc.

You can also use it to upload multiple sites, something like: nginx-site-1, 
nginx-site-2, nginx-site-3. Passing to the executions their relative 
configurations in "volumes", with their .conf and site files

> # Actions
> Actions are identified by channels. So to run each of them, 
> send the messages to their specific channels
 
## channel: start_container.create
> Create/Start a container with the image and name passed in the message body
> ### message:
> Just create.start a container from an existing docker.hub image
>
>     {
>         "image": "nginx"
>         "name": "nginx-name-container"
>     }
> 
> ### message:
> Build an image and creates a container with the generated image, and then executes the command passed in parameters.
> To generate the container it is necessary to inform the parameter 'build: true', and also the 'context', where it has 
> to be the location where the Dockerfile that will generate the image is.

> In this type of action, you can run any script, be it python, node, golang, etc... The scripts can do whatever you need, 
> like: process data, send email, format images, run a script that makes a summary of the current ecosystem, etc...

>     {
>       "image": "python_generated_image",
>       "command":'python hello_world.py',
>       "name": "python-exec",
>       "context": '/orchestration_containers/examples/hello_world_python/',
>       "build": true,
>       "volumes": {
>           '/orchestration_containers/examples/hello_world_python/': {
>               'bind': '/opt/hello_world/',
>               'mode': 'rw'
>           }
>       }
>     }
> 
> > ## "volumes"
> > Volumes are used to point their local path to an internal path of the generated container. So, to run some script the 
> > items must be correctly rotated.
> > Attention: If you are using the script inside a container, you pass the local docker socket to it, and the path used 
> > to locate the files you want to execute, are not the container paths, but the path of the host machine that is running docker

> >       "volumes": {
> >         '/orchestration_containers/examples/hello_world_python/': {
> >             'bind': '/opt/hello_world/',
> >             'mode': 'rw'
> >         }
> >       }

> ## channel: start_container.response_channel
> ### message:
> Same actions as the item above, however, in this case we have a 'response_channel'.
> The 'response_channel' is used when you want the script to perform a certain action, and you need the output of the execution.

> Then it executes a container/script, takes the output of the execution and sends it back to the broker, through the 'response_channel'.

> A simple usage example would be to run a container to run your test tasks, and get the output to send to 'response_channel', then you would 
> know "my test routine didn't pass, I have a code problem" . Something like Github Actions does.

>     {
>       "image": "python_generated_image",
>       "command":'python hello_world.py',
>       "name": "python-exec",
>       "context": '/orchestration_containers/examples/hello_world_python/',
>        "response_channel": "response_channel_from_my_python_execution",
>        "build": true,
>        "volumes": {
>            '/orchestration_containers/examples/hello_world_python/': {
>                'bind': '/opt/hello_world/',
>                'mode': 'rw'
>            }
>        }
>     }


> ## channel: start_containers_not_running
> ### message:
> It only starts a container that is not currently running. Send a message with the name of the container, and then it will try to start.
> By default it will try to get the exact name, but it is also possible to do a "begins with", passing the parameter "exact_value: false" in the message

>     {
>         "name": "nginx-name-container"
>     }


> ## channel: monitor_container_status
> ### message:
> Starts a thread to monitor the status of a specific container, then when the status of the container is not the
> expected ('running'), then it triggers a message to 'response_channel', notifying that the container is no longer running.

> This is the unique non-blocking action, so you can start multiple "monitors" to monitor the status of multiple containers.

>     {
>         "name": "nginx_container",
>         "response_channel": "my_container_is_not_running"
>     }
