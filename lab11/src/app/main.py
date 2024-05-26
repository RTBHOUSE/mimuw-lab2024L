import io
import tarfile

import docker
import docker.models.containers
from flask import Flask, request, jsonify


app = Flask('score')

docker_client = docker.from_env()


def to_tar_archive_bytes(code):
    # Create a buffer in memory
    buffer = io.BytesIO()

    # Create a tarfile object in write mode, using the buffer as the file object
    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        # Create a file object for the new file
        file = io.BytesIO(code)
        # Create a TarInfo object with the file name
        tarinfo = tarfile.TarInfo(name='myfile.txt')
        # Set the size of the file
        tarinfo.size = len(code)
        # Add the file to the tarball
        tar.addfile(tarinfo, fileobj=file)

    # Get the contents of the buffer
    return buffer.getvalue()


def validate_attendee_code(task_id, code):
    container = docker_client.containers.create(
        'cpp-builder:latest',
        detach=True,
        environment={'TASK_ID': task_id, 'CODE': code},
    )

    put_success = container.put_archive('/userdata', to_tar_archive_bytes(code))
    assert put_success

    container.start()
    result = container.wait(timeout=5)
    assert result['StatusCode'] == 0
    outcome = container.logs()
    container.remove()

    result = []
    for line in outcome.splitlines():
        compilation_code, diff_code = line.split(b' ')
        result.append({
            'exit_code': int(compilation_code),
            'result': int(diff_code)
        })
    return result


@app.route('/tasks/<string:task_id>/score', methods=['POST'])
def run_attendee_program(task_id: str):
    assert request.content_type == 'text/plain'
    code = request.data
    return jsonify(validate_attendee_code(task_id, code))


@app.route('/healthcheck')
def healthcheck():
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run(debug=False)
