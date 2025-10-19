import simpy, random, numpy as np

class KPIs:
    def __init__(self):
        self.wait_times = []
        self.flow_times = []
        self.completed = 0
        self.wip_peak = 0
        self.stockouts = 0
        self.replenishments = 0

    def snapshot_wip(self, wip):
        self.wip_peak = max(self.wip_peak, wip)

class Order:
    _id = 0
    def __init__(self, env, proc_time, due=None, priority=0, item_type=None, quantity=1):
        Order._id += 1
        self.id = Order._id
        self.arrival = env.now
        self.proc_time = proc_time
        self.due = due
        self.priority = priority
        self.item_type = item_type or f"item_{random.randint(1, 10)}"  # 10 product types
        self.quantity = quantity
        self.start = None
        self.end = None
        self.stockout = False

def spt_key(o): return (o.proc_time, o.arrival)
def fifo_key(o): return o.arrival
def edd_key(o): return (float('inf') if o.due is None else o.due, o.arrival)

def priority_with_aging(o, now, alpha=0.001):
    """Priority + aging factor to prevent starvation"""
    wait = 0 if o.start else (now - o.arrival)
    return (-o.priority - alpha * wait, o.arrival)

POLICY_MAP = {
    'FIFO': fifo_key,
    'SPT': spt_key,
    'EDD': edd_key,
    'PRIORITY': lambda o: (o.priority * -1, o.arrival)  # 高优先级更小
}

class WarehouseSim:
    def __init__(self, env, num_servers=2, policy='FIFO', seed=42, initial_inventory=100, reorder_point=20, reorder_quantity=50):
        random.seed(seed); np.random.seed(seed)
        self.env = env
        self.server = simpy.Resource(env, capacity=num_servers)
        self.policy = policy
        self.queue = []         # We maintain the queue ourselves, sorted by strategy
        self.kpis = KPIs()
        self.in_system = 0
        
        # Inventory management
        self.inventory = {}  # item_type -> quantity
        self.initial_inventory = initial_inventory
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity
        self.pending_orders = {}  # item_type -> list of orders waiting for stock
        
        # Initialize inventory
        for i in range(1, 11):
            self.inventory[f"item_{i}"] = initial_inventory
            self.pending_orders[f"item_{i}"] = []
        
        # Replenishment status tracking (prevent duplicate replenishment)
        self.replenishing = {f"item_{i}": False for i in range(1, 11)}

    def submit(self, order: Order):
        # Check inventory
        if self.inventory[order.item_type] >= order.quantity:
            # In stock, add directly to processing queue
            self.inventory[order.item_type] -= order.quantity
            self.queue.append(order)
            self.in_system += 1
            self.kpis.snapshot_wip(self.in_system)
            
            # Check if replenishment is needed (prevent duplicate triggering)
            if (self.inventory[order.item_type] <= self.reorder_point and 
                not self.replenishing[order.item_type]):
                self.replenishing[order.item_type] = True
                self.env.process(self.replenish_inventory(order.item_type))
        else:
            # Out of stock, add to waiting queue
            order.stockout = True
            self.kpis.stockouts += 1
            self.pending_orders[order.item_type].append(order)
            self.in_system += 1
            self.kpis.snapshot_wip(self.in_system)
            
            # Trigger replenishment (prevent duplicate triggering)
            if not self.replenishing[order.item_type]:
                self.replenishing[order.item_type] = True
                self.env.process(self.replenish_inventory(order.item_type))

    def replenish_inventory(self, item_type):
        """Replenishment process"""
        # Replenishment delay (1-5 minutes)
        replenish_time = np.random.uniform(60, 300)
        yield self.env.timeout(replenish_time)
        
        # Increase inventory
        self.inventory[item_type] += self.reorder_quantity
        self.kpis.replenishments += 1
        self.replenishing[item_type] = False  # Reset replenishment status
        
        # Process waiting orders
        while (self.pending_orders[item_type] and 
               self.inventory[item_type] >= self.pending_orders[item_type][0].quantity):
            order = self.pending_orders[item_type].pop(0)
            self.inventory[item_type] -= order.quantity
            order.stockout = False
            self.queue.append(order)

    def dispatcher(self):
        while True:
            if self.queue and self.server.count < self.server.capacity:
                # Strategy selection (supports aging factor)
                now = self.env.now
                if self.policy == 'PRIORITY':
                    self.queue.sort(key=lambda o: priority_with_aging(o, now))
                else:
                    self.queue.sort(key=POLICY_MAP[self.policy])
                order = self.queue.pop(0)
                self.env.process(self.process_order(order))
            yield self.env.timeout(0.1)

    def process_order(self, order: Order):
        with self.server.request() as req:
            yield req
            order.start = self.env.now
            wait = order.start - order.arrival
            # Processing
            yield self.env.timeout(order.proc_time)
            order.end = self.env.now
            flow = order.end - order.arrival
            self.kpis.wait_times.append(wait)
            self.kpis.flow_times.append(flow)
            self.kpis.completed += 1
            self.in_system -= 1

def arrival_generator(env, sim: WarehouseSim, lam=10, mean_proc=8):
    while True:
        # Inter-arrival time follows exponential distribution (Poisson arrival)
        inter_arrival = np.random.exponential(lam)
        yield env.timeout(inter_arrival)
        # Random processing time (can be changed to triangular/lognormal)
        proc = max(1, np.random.normal(loc=mean_proc, scale=2))
        due = env.now + max(10, np.random.normal(loc=30, scale=5))
        priority = 1 if random.random() < 0.2 else 0  # 20% urgent orders
        # Random product type and quantity
        item_type = f"item_{random.randint(1, 10)}"
        quantity = random.choices([1, 2, 3, 5], weights=[0.5, 0.3, 0.15, 0.05])[0]
        sim.submit(Order(env, proc_time=proc, due=due, priority=priority, 
                        item_type=item_type, quantity=quantity))

def run_once(sim_time=3600, num_servers=2, policy='FIFO', lam=10, mean_proc=8, seed=42, 
             initial_inventory=100, reorder_point=20, reorder_quantity=50, seed_offset=0):
    # Reset order ID and random seed
    Order._id = 0
    actual_seed = seed + seed_offset
    
    env = simpy.Environment()
    sim = WarehouseSim(env, num_servers=num_servers, policy=policy, seed=actual_seed,
                      initial_inventory=initial_inventory, reorder_point=reorder_point, 
                      reorder_quantity=reorder_quantity)
    env.process(arrival_generator(env, sim, lam=lam, mean_proc=mean_proc))
    env.process(sim.dispatcher())
    env.run(until=sim_time)

    k = sim.kpis
    def avg(a): return sum(a)/len(a) if a else 0.0
    
    # Calculate stockout rate
    total_orders = k.completed + k.stockouts
    stockout_rate = k.stockouts / total_orders if total_orders > 0 else 0
    
    return {
        "policy": policy,
        "completed": k.completed,
        "avg_wait": round(avg(k.wait_times), 2),
        "p90_wait": round(np.percentile(k.wait_times, 90) if k.wait_times else 0, 2),
        "avg_flow": round(avg(k.flow_times), 2),
        "throughput_per_hr": round(k.completed / (sim_time/3600), 2),
        "wip_peak": k.wip_peak,
        "stockout_rate": round(stockout_rate, 3),
        "replenishments": k.replenishments
    }

if __name__ == "__main__":
    print(run_once(policy='FIFO'))
