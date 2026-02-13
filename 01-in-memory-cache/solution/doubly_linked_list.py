"""
Doubly linked list with sentinel nodes.
"""

from models import Node

class DoublyLinkedList:
    """
    Doubly linked list with sentinel nodes.

    Supports O(1):
    - add_to_head(node)   → Mark as most recently used
    - remove(node)        → Detach a node from anywhere in the list
    - remove_tail()       → Evict least recently used, returns the removed node
    - move_to_head(node)  → Shortcut: remove + add_to_head

    Visual:
        HEAD ↔ [most recent] ↔ [...] ↔ [least recent] ↔ TAIL
    """
    
    def __init__(self):
        self.head: Node = Node(key="__HEAD__", value=None)
        self.tail: Node = Node(key="__TAIL__", value=None)
        self.head.next = self.tail
        self.tail.prev = self.head
        
        self.size = 0

    def add_to_head(self, node: Node):
        """
        Add a node to the head of the list.
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        
        self.size += 1
        
    def remove(self, node: Node):
        """
        Remove a node from the list.
        """
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        
    def remove_tail(self) -> Node:
        """
        Remove the least recently used node from the tail of the list.
        """
        if self.size == 0:
            return None
        node = self.tail.prev
        self.remove(node)
        return node
    
    def move_to_head(self, node: Node):
        """
        Move a node to the head of the list.
        """
        self.remove(node)
        self.add_to_head(node)
        
    def is_empty(self) -> bool:
        """
        Check if the list is empty.
        """
        return self.size == 0
    
    def __len__(self) -> int:
        """
        Return the size of the list.
        """
        return self.size
    
    def __str__(self) -> str:
        """
        Return a string representation of the list.
        """
        nodes = []
        current = self.head.next
        while current != self.tail:
            nodes.append(f"[{current.key}:{current.value}]")
            current = current.next
        return "HEAD ↔ " + " ↔ ".join(nodes) + " ↔ TAIL" if nodes else "HEAD ↔ TAIL (empty)"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the list.
        """
        return self.__str__()
    