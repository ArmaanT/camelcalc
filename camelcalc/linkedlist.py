from typing import Generic, Optional, TypeVar

from camelcalc.utils import to_string


T = TypeVar("T")


class Node(Generic[T]):
    data: T
    prev: "Optional[Node[T]]"
    next: "Optional[Node[T]]"

    def __init__(self, val: T):
        self.data = val
        self.prev = None
        self.next = None

    def __str__(self) -> str:
        return str(self.data)


class DoublyLinkedList(Generic[T]):
    head: "Optional[Node[T]]"
    tail: "Optional[Node[T]]"
    # Used for iterator
    curr: "Optional[Node[T]]"

    def __init__(self) -> None:
        self.head = None
        self.tail = None

    def __str__(self) -> str:
        return "\n".join(reversed(list(to_string(self))))

    def __iter__(self) -> "DoublyLinkedList[T]":
        self.curr = self.head
        return self

    def __next__(self) -> T:
        if self.curr is None:
            raise StopIteration()
        data = self.curr.data
        self.curr = self.curr.next
        return data

    def remove_chain(self, node: Node[T]) -> None:
        """
        Remove a node and all the nodes following it.
        Used when (a stack of) camels moves
        """

        # Node is head
        if node.prev is None:
            self.head = None
            self.tail = None
        else:  # Node is not head
            self.tail = node.prev
            node.prev.next = None
            node.prev = None

    def insert_chain_tail(self, node: Node[T], tail: Node[T]) -> None:
        """
        Insert a chain of nodes at the end of the DoublyLinkedList.
        Used when (a stack of) camels move forward
        """

        # DLL is empty
        if self.tail is None:
            self.head = node
            self.tail = tail
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = tail

    def insert_chain_head(self, node: Node[T], tail: Node[T]) -> None:
        """
        Insert a chain of nodes at the beginning of the DoublyLinkedList.
        Used when (a stack of) camels move backward
        """

        # DLL is empty
        if self.head is None:
            self.head = node
            self.tail = tail
        else:
            self.head.prev = tail
            tail.next = self.head
            self.head = node

    def insert_single_head(self, data: T) -> None:
        """
        Create a new node holding `data` and insert it
        in the head of the DoublyLinkedList
        """
        node = Node(data)

        # DLL is empty
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node

    def extend(self, dll: "DoublyLinkedList[T]") -> None:
        """
        Extend this DoublyLinkedList with all nodes from `dll`
        """

        if dll.head is not None:
            assert dll.tail is not None
            self.insert_chain_tail(dll.head, dll.tail)
