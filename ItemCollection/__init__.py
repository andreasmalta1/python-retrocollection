# The backend file contains the main class Item which stores the record collection items

import datetime
import os
from typing import List
import jsonpickle


# The class Item has 3 class variables, the ITEM_LIST, the TYPE_LIST and the NAME
# The ITEM_LIST contains the list of all the items in the collection
# The TYPE_LIST contains the categories which the items can be assorted in
# The NAME contains the name/username of the record collector
# The Item class contains the title of item, the type of the item, the date it was added to the collection, the date it
# was manufactured and the description. It also has a self generated id.
class Item:
    ITEM_LIST: List = []
    TYPE_LIST: List = []
    NAME: str = None

    def __init__(self, title: str, item_type: str, doa: datetime.date, dom: datetime.date, description: str):
        self.__id = Item.__get_next_id()
        self.title: str = title
        self.item_type: str = item_type
        self.doa: datetime.date = doa
        self.dom: datetime.date = dom
        self.description: str = description
        Item.ITEM_LIST.append(self)

    # The __get_next_id method generates the id for the item being created by always incrementing by one from the
    # largest number
    @staticmethod
    def __get_next_id() -> int:
        largest_id = 0
        for i in Item.ITEM_LIST:
            if i.__id > largest_id:
                largest_id = i.__id
        return largest_id + 1

    # The get_by_id method allows the user to recall an item from the collection using the id
    # This will be used when editing a specific item in the collection
    @staticmethod
    def get_by_id(item_id: int):
        for i in Item.ITEM_LIST:
            if i.id == item_id:
                return i

    @property
    def id(self) -> int:
        return self.__id

    # The load_types method reads the item types in the type.json file.
    # The initial file has 4 categories written to the file.
    # The user has the ability to add more types from the program. These will be added in the json file and loaded with
    # each program run
    @staticmethod
    def load_types() -> None:
        Item.TYPE_LIST.clear()
        with open("UserFiles/type.json") as infile:
            json_object = infile.read()
            types_json = jsonpickle.decode(json_object)
            for x in types_json:
                Item.TYPE_LIST.append(x)

    # The save_to_file method saves the items in the collection to item.json file
    @staticmethod
    def save_to_file() -> None:
        json_object = jsonpickle.encode(Item.ITEM_LIST, unpicklable=False)
        with open("UserFiles/items.json", "w") as outfile:
            outfile.write(json_object)

    # The load_from_file method retrieves all the items from the item.json if this file is present
    @staticmethod
    def load_from_file() -> None:
        Item.ITEM_LIST.clear()

        if not os.path.isfile("UserFiles/items.json") or not os.path.getsize("UserFiles/items.json") > 0:
            return

        with open("UserFiles/items.json") as infile:
            json_object = infile.read()
            dictionary = jsonpickle.decode(json_object)
            for item in dictionary:
                Item(item["title"],
                     item["item_type"],
                     datetime.datetime.strptime(item["doa"], "%Y-%m-%d").date(),
                     datetime.datetime.strptime(item["dom"], "%Y-%m-%d").date(),
                     item["description"])

    # The load_name method retrieves the record collectors name from the name.json if it exists
    # This name is used for GUI purposes by displaying it on all the windows
    @staticmethod
    def load_name() -> None:

        if not os.path.isfile("UserFiles/name.json") or not os.path.getsize("UserFiles/name.json") > 0:
            return

        with open("UserFiles/name.json") as infile:
            json_object = infile.read()
            Item.NAME = jsonpickle.decode(json_object)
