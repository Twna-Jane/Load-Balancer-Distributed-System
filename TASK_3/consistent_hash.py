class ConsistentHashRing:
    def __init__(self, servers=None, slots=512, virtual_nodes=9):
        self.servers = servers or []
        self.slots = slots
        self.virtual_nodes = virtual_nodes
        self.hash_ring = [None] * slots
        self.server_map = {}  # {slot: server_id}
        self._initialize_ring()

    def H(self, i):
        hash_value = pow(i, 2) + 2*i + 17
        return hash_value % self.slots

    def Phi(self, i, j):
        key = f"{i}-{j}"
        hash_value = pow(i, 2) + pow(j, 2) + 2*j + 25
        return hash_value % self.slots

    def _initialize_ring(self):
        for server_id, server_address in enumerate(self.servers):
            for replica_id in range(self.virtual_nodes):
                slot = self.Phi(server_id, replica_id)
                original_slot = slot
                while self.hash_ring[slot] is not None:
                    slot = (slot + 1) % self.slots  # Linear probing
                    if slot == original_slot:
                        raise Exception("Hash ring is full.")
                self.hash_ring[slot] = server_address
                self.server_map[slot] = server_address

    def get_server_for_request(self, request_id):
        slot = self.H(request_id)
        original_slot = slot
        while self.hash_ring[slot] is None:
            slot = (slot + 1) % self.slots
            if slot == original_slot:
                return None
        return self.hash_ring[slot]
