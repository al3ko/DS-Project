import subprocess
import random
import string


class DockerManager:

    def __init__(self):
        self.image_name = "loadbalancer-server"
        self.network = "load-balancer_loadbalancer"

    # ------------------------------------------
    # Generate a random container name
    # ------------------------------------------
    def random_hostname(self, length=6):
        letters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    # ------------------------------------------
    # Start a new server container
    # ------------------------------------------
    def start_server(self, hostname=None, server_id=None):

        if hostname is None:
            hostname = self.random_hostname()

        if server_id is None:
            server_id = random.randint(1000, 9999)

        command = [
            "docker",
            "run",
            "-d",
            "--name",
            hostname,
            "--network",
            self.network,
            "-e",
            f"SERVER_ID={server_id}",
            self.image_name
        ]

        print("Running command:", command, flush=True)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        print("Return code:", result.returncode, flush=True)
        print("STDOUT:", result.stdout, flush=True)
        print("STDERR:", result.stderr, flush=True)

        if result.returncode != 0:
            return None

        return hostname

    # ------------------------------------------
    # Stop and remove a server
    # ------------------------------------------
    def remove_server(self, hostname):

        subprocess.run(
            ["docker", "rm", "-f", hostname],
            capture_output=True,
            text=True
        )

    # ------------------------------------------
    # List running server containers
    # ------------------------------------------
    def list_servers(self):

        result = subprocess.run(
            [
                "docker",
                "ps",
                "--format",
                "{{.Names}}"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return []

        names = []

        for name in result.stdout.splitlines():
            if name.startswith("Server") or len(name) == 6:
                names.append(name)

        return names

    # ------------------------------------------
    # Check if a container exists
    # ------------------------------------------
    def exists(self, hostname):
        return hostname in self.list_servers()