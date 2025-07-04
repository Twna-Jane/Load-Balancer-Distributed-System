class ConsistentHashRing:
    """The modified consistent hash ring for analysis no. 4"""
    def __init__(self, servers=None, slots=512, virtual_nodes=9):
        self.servers = servers or []
        self.slots = slots
        self.virtual_nodes = virtual_nodes
        self.hash_ring = [None] * slots
        self.server_map = {}
        self._initialize_ring()

    def H(self, i):
        hash_value = 3*i
        return hash_value % self.slots

    def Phi(self, i, j):
        key = f"{i}-{j}"
        hash_value = pow(i, 2) + 4*j
        return hash_value % self.slots

    def _initialize_ring(self):
        for server_id, server_address in enumerate(self.servers):
            for replica_id in range(self.virtual_nodes):
                original_slot = self.Phi(server_id, replica_id)
                slot = original_slot
                i = 1
                while self.hash_ring[slot] is not None:
                    slot = (original_slot + i + (i * i)) % self.slots  # Quadratic probing
                    i += 1
                    if i >= self.slots:
                        raise Exception("Hash ring is full.")
                self.hash_ring[slot] = server_address
                self.server_map[slot] = server_address

    def get_server_for_request(self, request_id):
        original_slot = self.H(request_id)
        slot = original_slot
        i = 1
        while self.hash_ring[slot] is None:
            slot = (original_slot + i + (i * i)) % self.slots  # Quadratic probing
            i += 1
            if i >= self.slots:
                return None
        return self.hash_ring[slot]
