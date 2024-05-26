Applications deployment
=======================

## Task
 
Prepare a runtime for running programs at algorithmic contests.

There already exists the main UI with a dashboard. Your task is to implement a workers engine that compiles and executes attendees programs and scores them given test cases.

Technically, you have to implement a microservice with API as described in a sibiling file `api.yaml` in OpenAPI format. You may edit and preview it at [editor.swagger.io](https://editor.swagger.io/), where also some boilerplate code generators are available.

Scoring a single program (single call to your API) should spawn at least one container, in which attendee program will be scored. You should use [Docker Engine SDK](https://docs.docker.com/engine/api/sdk/) to run containers and gather results.

You may use any programming language to solve the task. However, python is greatly welcome :)


## Advices

* Do not care much about tasks and test cases – assume they are constant for the time being.

* Also, assume that c++ is the only available language for attendees.

* Ignore HA of your app.

* Prefix images with `mirror.gcr.io/google-containers/`, so that `ubuntu:20.04` becomes `mirror.gcr.io/google-containers/ubuntu:20.04`.


## Hints

<details>
    <summary>Hint 0 /docker in docker</summary>

    ```bash
    docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock ...
    ```

</details>

<details>
    <summary>Hint 1 /spoiler</summary>

    You need an image that will be used for users' programs compilation.

</details>

<details>
    <summary>Hint 2 /spoiler</summary>

    The same image may contain test cases and score the programs.

</details>

<details>
    <summary>Hint 3 /spoiler</summary>

    Limit the resources.

</details>


## More features

<details>
    <summary>Extra 1 /spoiler</summary>

    Hardening. User's code may be malicious :p

</details>
