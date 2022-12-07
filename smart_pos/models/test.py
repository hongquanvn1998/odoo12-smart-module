import inspect
class Node:
    list_node = []
    def __init__(self,name,child_id) -> None:
        self.name = name
        self.child_id = child_id
        Node.list_node.append({'list_name':self.name,'child_id':self.child_id})

    def __str__(self) -> str:
        print("name {} and child_id {}".format(self.name,self.child_id))
        return "name {} and child_id {}".format(self.name,self.child_id)
    
Node3 = Node("3",False)

Node2 = Node("2",Node3)

Node1 = Node("1",Node2)


# attributes = inspect.getmembers(Node, lambda a:not(inspect.isroutine(a)))
# list_attribute = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
# print(list_attribute)
# print(Node3.__dict__)

print(Node.list_node)

