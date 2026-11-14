# [ AgenTalk ]

import uuid,ray
import params
import AgenTalk

def init():
    return params.phase.worker

@AgenTalk.fastpass
def act(comKey,num):
    nodeID=ray.get_runtime_context().get_node_id()
    nodeIP=ray.util.get_node_ip_address()
    result={'nodeID':nodeID,'nodeIP':nodeIP,'num':num}
    pushGlobalRedis(comKey,result)
    echo(f"worker {num} done {nodeIP=}")

