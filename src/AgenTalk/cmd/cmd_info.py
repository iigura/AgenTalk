import sys,json,textwrap
import ray
from ray.util.state import list_nodes
import AgenTalk

def showNodes():
    nodes=[n for n in ray.nodes()]
    headNodeID=getHeadNodeID()
    for nodeInfo in nodes:
        nodeID=nodeInfo.get('NodeID')
        alive=nodeInfo.get('Alive')
        headMark='[HEAD]:' if nodeID==headNodeID else 'remote:'
        if alive:
            print(f"{headMark} node ID: {nodeID}")
        else:
            print(f"{headMark}(DEAD NODE ID: {nodeID})")
        print(f"    IP Address: {nodeInfo.get('NodeManagerAddress')}")
        resources=nodeInfo.get('Resources')
        prettyJson=json.dumps(resources,indent=4,ensure_ascii=False)
        indentedJson=textwrap.indent(prettyJson,prefix=' '*8)
        print('    Resources:')
        print(indentedJson)

def getHeadNodeID():
    t=list_nodes(filters=[('is_head_node','=',True)])
    if t is None or len(t)==0:
        return None
    assert len(t)==1,f"len(t)={len(t)}"
    headNode=t[0]
    headNodeID=headNode.node_id
    return headNodeID

def main(configFilePath):
    AgenTalk.init(configFilePath,verbose=False,startRay=True)
    major=sys.version_info.major
    minor=sys.version_info.minor
    micro=sys.version_info.micro
    print(f"agt is running on Python {major}.{minor}.{micro}")
    showNodes()

if __name__=='__main__':
    main('../../../config.yaml')

