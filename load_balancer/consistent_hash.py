"""
consistent_hash.py

Implements a Consistent Hash Ring using:
- 512 slots
- 3 server containers
- 9 virtual servers per server
- Linear probing for collision resolution
"""

TOTAL_SLOTS = 512
NUM_SERVERS = 3
VIRTUAL_SERVERS = 9


class ConsistentHashMap:

    def __init__(self):
        # Hash ring
        self.ring = [None] * TOTAL_SLOTS

        # Store virtual server locations
        self.server_positions = {}

    # -----------------------------------------------------
    # Request Hash Function
    # H(i) = i² + 2i + 17
    # -----------------------------------------------------
    def request_hash(self, request_id):
        return (
            request_id ** 2
            + 2 * request_id
            + 17
        ) % TOTAL_SLOTS

    # -----------------------------------------------------
    # Virtual Server Hash Function
    # Φ(i,j) = i² + j² + 2j + 25
    # -----------------------------------------------------
    def virtual_server_hash(self, server_id, virtual_server):
        return (
            server_id ** 2
            + virtual_server ** 2
            + 2 * virtual_server
            + 25
        ) % TOTAL_SLOTS

    # -----------------------------------------------------
    # Linear Probing
    # -----------------------------------------------------
    def find_empty_slot(self, slot):

        while self.ring[slot] is not None:
            slot = (slot + 1) % TOTAL_SLOTS

        return slot

    # -----------------------------------------------------
    # Add Server
    # -----------------------------------------------------
    def add_server(self, server_id):

        self.server_positions[server_id] = []

        for virtual_server in range(VIRTUAL_SERVERS):

            slot = self.virtual_server_hash(
                server_id,
                virtual_server
            )

            slot = self.find_empty_slot(slot)

            self.ring[slot] = server_id

            self.server_positions[server_id].append(slot)

    # -----------------------------------------------------
    # Remove Server
    # -----------------------------------------------------
    def remove_server(self, server_id):

        if server_id not in self.server_positions:
            return

        for slot in self.server_positions[server_id]:
            self.ring[slot] = None

        del self.server_positions[server_id]

    # -----------------------------------------------------
    # Find server for a request
    # -----------------------------------------------------
    def get_server(self, request_id):

        slot = self.request_hash(request_id)

        start_slot = slot

        while self.ring[slot] is None:

            slot = (slot + 1) % TOTAL_SLOTS

            if slot == start_slot:
                return None

        return self.ring[slot]

    # -----------------------------------------------------
    # Initialise Hash Ring
    # -----------------------------------------------------
    def initialize(self):

        for server in range(1, NUM_SERVERS + 1):
            self.add_server(server)

    # -----------------------------------------------------
    # Display Ring
    # -----------------------------------------------------
    def display(self):

        print("\n==============================")
        print("CONSISTENT HASH RING")
        print("==============================\n")

        for server in self.server_positions:

            print(f"Server {server}")

            print(
                "Virtual Servers:",
                self.server_positions[server]
            )

            print()

    # -----------------------------------------------------
    # Display Request Mapping
    # -----------------------------------------------------
    def test_requests(self):

        print("\n==============================")
        print("REQUEST MAPPING")
        print("==============================\n")

        for request in range(1, 16):

            server = self.get_server(request)

            print(
                f"Request {request:2d}"
                f" -> Server {server}"
            )


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    hash_ring = ConsistentHashMap()

    hash_ring.initialize()

    hash_ring.display()

    hash_ring.test_requests()