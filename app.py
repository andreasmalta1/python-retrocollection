# The front end file contains all the window classes and the main logic to run the program

import os
import sys
import jsonpickle
from PyQt5 import uic
from PyQt5.Qt import QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QHeaderView, QMessageBox
from ItemCollection import Item

global i


# The MenuWindow class is used to display the main menu, containing 5 buttons
# 1. Add Items
# 2. Edit Items
# 3. Show Items
# 4. Add Type
# 5. Exit
# The first four buttons all link to other different windows and the exit buttons quits the program
class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/main_menu.ui", self)
        self.setGeometry(0, 0, 700, 700)
        self.build_ui()
        self._error_message = ""
        Item.load_types()

    def build_ui(self):
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.btn_add_item.clicked.connect(add_items_window)
        self.ui.btn_edit.clicked.connect(edit_items_window)
        self.ui.btn_show.clicked.connect(show_items_window)
        self.ui.btn_add_type.clicked.connect(add_type_window)
        self.ui.btn_exit.clicked.connect(exit_app)


# The AddWindow class is the view for when adding a new item to the collection
# The user enters the necessary data as required and presses the add button to add the item to the list
# The calendars are restricted to not allow users to select future dates
# The user also has the ability to clear the form
# The list of items is also shown in the same view in a table and the user has the ability to delete items.
# In the table, the first four columns are resized to fit contents and the the description column is stretched to the
# max possible length since this might be longer than the other fields
class AddWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/add_items.ui", self)
        self.setGeometry(0, 0, 700, 700)
        self.build_ui()
        self._error_message = ""

    def build_ui(self):
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.btn_add.clicked.connect(self.add_items)
        self.ui.btn_clear.clicked.connect(self.clear_items)
        self.ui.btn_delete.clicked.connect(self.delete_items)
        self.ui.cal_doa.setMaximumDate(QDate.currentDate())
        self.ui.cal_dom.setMaximumDate(QDate.currentDate())
        self.ui.cmb_type.addItems(Item.TYPE_LIST)

        self.ui.tbl_items.setColumnCount(5)
        self.ui.tbl_items.setHorizontalHeaderLabels(("Title", "Item Type", "DOA", "DOM", "Description"))
        self.ui.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tbl_items.horizontalHeader().setStretchLastSection(True)
        my_font = QFont()
        my_font.setBold(True)
        self.ui.tbl_items.horizontalHeader().setFont(my_font)

        self.load_items()

    # Loads the items in the view table
    def load_items(self) -> None:
        for x in reversed(range(self.ui.tbl_items.rowCount())):
            self.ui.tbl_items.removeRow(x)

        Item.load_from_file()
        r = 0
        for x in Item.ITEM_LIST:
            self.ui.tbl_items.insertRow(r)
            self.ui.tbl_items.setItem(r, 0, QTableWidgetItem(x.title))
            self.ui.tbl_items.setItem(r, 1, QTableWidgetItem(x.item_type))
            self.ui.tbl_items.setItem(r, 2, QTableWidgetItem(x.doa.strftime("%d/%m/%Y")))
            self.ui.tbl_items.setItem(r, 3, QTableWidgetItem(x.dom.strftime("%d/%m/%Y")))
            self.ui.tbl_items.setItem(r, 4, QTableWidgetItem(x.description))
            r += 1

    # This method validates the user input by ensuring that the title and description fields have been filled
    # The validation also ensures that the date of manufacture is not after the date added to collection
    def is_valid_input(self) -> bool:
        is_valid = True
        if not self.ui.txt_title.text():
            self._error_message += "Item title is missing.\n"
            is_valid = False
        if not self.ui.txt_description.text():
            self._error_message += "Item description is missing.\n"
            is_valid = False
        if self.ui.cal_dom.selectedDate() > self.ui.cal_doa.selectedDate():
            self._error_message += "Date of Manufacture must not be after Date Added to Collection.\n"
            is_valid = False
        print(self._error_message)
        return is_valid

    def add_items(self) -> None:

        # Shows any error messages to the user
        if not self.is_valid_input():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self._error_message)
            msg.setGeometry(225, 250, 300, 300)
            msg.setWindowTitle("Error in Entry")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self._error_message = ""
            return

        # Adding the item entered by the user to the Item class
        # After entering the item, it is added to the items.json file and the items are loaded again.
        # The form is also emptied allowing to user to enter another item
        title = self.ui.txt_title.text()
        item_type = self.ui.cmb_type.currentText()
        doa = self.ui.cal_doa.selectedDate().toPyDate()
        dom = self.ui.cal_dom.selectedDate().toPyDate()
        description = self.ui.txt_description.text()
        Item(title, item_type, doa, dom, description)
        Item.save_to_file()
        self.clear_items()
        self.load_items()

    # The clear_items method is used to clear the form view and reset the dates to the current date
    # This method is run when the user presses the clear button or when the user adds a new item to the list
    def clear_items(self) -> None:
        self.ui.txt_title.clear()
        self.ui.cmb_type.clear()
        self.ui.cmb_type.addItems(Item.TYPE_LIST)
        self.ui.txt_description.clear()
        self.ui.cal_doa.setSelectedDate(QDate.currentDate())
        self.ui.cal_dom.setSelectedDate(QDate.currentDate())

    # The delete_items method is used to delete items in the table by pressing the delete button.
    # The user is only allowed to delete one item at a time and an error message is displayed if no items are selected
    def delete_items(self) -> None:
        rows = sorted(set(index.row() for index in
                          self.ui.tbl_items.selectedIndexes()))

        if len(rows) < 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setGeometry(225, 250, 300, 300)
            msg.setText("Please select an item to delete")
            msg.setWindowTitle("No Item Selected")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        ask = QMessageBox()
        ask.setIcon(QMessageBox.Question)
        ask.setGeometry(175, 250, 300, 300)
        ask.setText("Are you sure you want to delete this item")
        ask.setWindowTitle("Deleting item")
        ask.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ask.activateWindow()
        user_choice = ask.exec_()

        if user_choice == QMessageBox.No:
            return

        # Exception handling is used  to ensure that the user does not encounter any index errors that cause the program
        # to crash
        # When such an error is met no action is taken as deletion will still take place
        try:
            for row in rows:
                Item.ITEM_LIST.pop(row)
        except IndexError:
            pass

        Item.save_to_file()
        self.load_items()


# The LoginWindow class allows the user to enter their name/username so that it is displayed at the top of all screens
# Thus this class is only performed the first time that the program is run
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/startup.ui", self)
        self.setGeometry(0, 0, 700, 700)
        self.build_ui()
        self._error_message = ""

    # The is_valid_method function confirms that user has not left the name field empty
    def is_valid_input(self) -> bool:
        is_valid = True
        if not self.ui.txt_name.text():
            self._error_message += "Name is missing.\n"
            is_valid = False

        return is_valid

    def build_ui(self):
        self.ui.btn_name.clicked.connect(self.name_save)

    def name_save(self) -> None:
        if not self.is_valid_input():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(self._error_message)
            msg.setGeometry(225, 250, 300, 300)
            msg.setWindowTitle("Error in Entry")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self._error_message = ""
            return

        # The entered name is saved to the class variable NAME when the button is pressed.
        # The name is then stored in the name.json file
        Item.NAME = self.ui.txt_name.text()
        json_object = jsonpickle.encode(Item.NAME, unpicklable=False)
        with open("UserFiles/name.json", "w") as outfile:
            outfile.write(json_object)
        Item.load_name()

        # After storing the name the MenuWindow class is called and the user is shown the program's main menu
        # The LoginWindow is closed at the same time
        w = MenuWindow()
        w.show()
        LoginWindow.close(self)


# The EditWindow class is the view that allows the user to choose which item to edit.
# Users also have the option to delete items from this view
# In this view all the items are loaded in a table and the user has two buttons
# 1. Edit
# 2. Delete
class EditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/edit_items.ui", self)
        self.setGeometry(0, 0, 700, 700)
        self.build_ui()

    def build_ui(self):
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.btn_delete.clicked.connect(self.delete_items)
        self.ui.btn_edit.clicked.connect(self.edit_items)
        self.ui.tbl_items.setColumnCount(5)
        self.ui.tbl_items.setHorizontalHeaderLabels(("Title", "Item Type", "DOA", "DOM", "Description"))
        self.ui.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tbl_items.horizontalHeader().setStretchLastSection(True)
        my_font = QFont()
        my_font.setBold(True)
        self.ui.tbl_items.horizontalHeader().setFont(my_font)

        self.load_items()

    # Method to load the items
    def load_items(self) -> None:
        for x in reversed(range(self.ui.tbl_items.rowCount())):
            self.ui.tbl_items.removeRow(x)

        Item.load_from_file()
        r = 0
        for x in Item.ITEM_LIST:
            self.ui.tbl_items.insertRow(r)
            self.ui.tbl_items.setItem(r, 0, QTableWidgetItem(x.title))
            self.ui.tbl_items.setItem(r, 1, QTableWidgetItem(x.item_type))
            self.ui.tbl_items.setItem(r, 2, QTableWidgetItem(x.doa.strftime("%d/%m/%Y")))
            self.ui.tbl_items.setItem(r, 3, QTableWidgetItem(x.dom.strftime("%d/%m/%Y")))
            self.ui.tbl_items.setItem(r, 4, QTableWidgetItem(x.description))
            r += 1

    # Method to delete one item at a time as before
    def delete_items(self) -> None:
        rows = sorted(set(index.row() for index in
                          self.ui.tbl_items.selectedIndexes()))

        if len(rows) < 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setGeometry(225, 250, 300, 300)
            msg.setText("Please select an item to delete")
            msg.setWindowTitle("No Item Selected")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        ask = QMessageBox()
        ask.setIcon(QMessageBox.Question)
        ask.setGeometry(175, 250, 300, 300)
        ask.setText("Are you sure you want to delete this item")
        ask.setWindowTitle("Deleting item")
        ask.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ask.activateWindow()
        user_choice = ask.exec_()

        if user_choice == QMessageBox.No:
            return

        # Exception handling to ensure program does not cause due to index errors
        try:
            for row in rows:
                Item.ITEM_LIST.pop(row)
        except IndexError:
            pass

        Item.save_to_file()
        self.load_items()

    # In the edit_items method, the item selected by the user is saved in the global variable i so that the item can be
    # edited in the following view called from this function
    # This method also displays an error message if an item has not been selected
    def edit_items(self) -> None:
        global i
        rows = sorted(set(index.row() for index in
                          self.ui.tbl_items.selectedIndexes()))

        if len(rows) < 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setGeometry(225, 250, 300, 300)
            msg.setText("Please select an item to edit")
            msg.setWindowTitle("No Item Selected")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        # The global variable i stores the Item using the method get_by_id.
        # get_by_id receives as an argument the row value. This is incremented by one since the table rows start from 0
        # and the item id's start from 1
        for row in rows:
            i = Item.get_by_id(row + 1)

        # The view where the user actually edits the item is called and the current view is temporarily closed
        w_edit = EditorWindow()
        w_edit.show()
        EditWindow.close(self)


# EditorWindow is the class that loads the selected item and allows the user to edit any field and save the changes
class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/editor.ui", self)
        self.build_ui()
        self.setGeometry(0, 0, 700, 700)
        self._error_message = ""

    def build_ui(self):
        # The fields are filled in by the contents saved in the global variable i containing the Item data
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.txt_title.setText(i.title)
        self.ui.cmb_type.addItems(Item.TYPE_LIST)
        self.ui.cmb_type.setCurrentText(i.item_type)
        self.ui.cal_doa.setSelectedDate(i.doa)
        self.ui.cal_dom.setSelectedDate(i.dom)
        self.ui.txt_description.setText(i.description)
        self.ui.cal_doa.setMaximumDate(QDate.currentDate())
        self.ui.cal_dom.setMaximumDate(QDate.currentDate())

        self.ui.btn_edit.clicked.connect(self.editor)
        self.ui.btn_clear.clicked.connect(self.clear_items)

    # The program verifies the new inputs by the user to ensure that no field is left empty
    # The validation also ensures that the date of manufacture is not after the date added to collection
    def is_valid_input(self) -> bool:
        is_valid = True
        if not self.ui.txt_title.text():
            self._error_message += "Item title is missing.\n"
            is_valid = False
        if not self.ui.txt_description.text():
            self._error_message += "Item description is missing.\n"
            is_valid = False
        if self.ui.cal_dom.selectedDate() > self.ui.cal_doa.selectedDate():
            self._error_message += "Date of Manufacture must not be after Date Added to Collection.\n"
            is_valid = False

        return is_valid

    def editor(self) -> None:

        if not self.is_valid_input():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setGeometry(225, 250, 300, 300)
            msg.setText(self._error_message)
            msg.setWindowTitle("Error in Entry")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self._error_message = ""
            return

        # The contents of the item saved in the global variable i are then overwritten by the new contents
        # inputted by the user
        # The new item item is then saved to file
        i.title = self.ui.txt_title.text()
        i.item_type = self.ui.cmb_type.currentText()
        i.doa = self.ui.cal_doa.selectedDate().toPyDate()
        i.dom = self.ui.cal_dom.selectedDate().toPyDate()
        i.description = self.ui.txt_description.text()
        Item.save_to_file()
        self.clear_items()

        # The EditorWindow view is closed and the edit view is shown again
        # When calling the EditWindow the items are loaded again and the changes are implemented instantly
        EditorWindow.close(self)
        edit_items_window()

    def clear_items(self) -> None:
        self.ui.txt_title.clear()
        self.ui.cmb_type.clear()
        self.ui.cmb_type.addItems(Item.TYPE_LIST)
        self.ui.txt_description.clear()
        self.ui.cal_doa.setSelectedDate(QDate.currentDate())
        self.ui.cal_dom.setSelectedDate(QDate.currentDate())


# The ShowWindow class allows the user to view all the items in a chosen category
# This view contains a drop down menu that allows the user to select one of the categories and a search button which
# when pressed performs the search
class ShowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/show_items.ui", self)
        self.setGeometry(0, 0, 700, 700)
        self.build_ui()

    def build_ui(self):
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.cmb_item_type.clear()
        self.ui.cmb_item_type.addItems(Item.TYPE_LIST)
        self.ui.btn_search.clicked.connect(self.load_items)
        self.ui.tbl_items.setColumnCount(5)
        self.ui.tbl_items.setHorizontalHeaderLabels(("Title", "Item Type", "DOA", "DOM", "Description"))
        self.ui.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tbl_items.horizontalHeader().setStretchLastSection(True)
        my_font = QFont()
        my_font.setBold(True)
        self.ui.tbl_items.horizontalHeader().setFont(my_font)

        self.load_items()

    # Loading all the items
    # This method is run when the view is loaded and when the search button is pressed.
    # Thus, by default, when initially loading the screen, the items shown will be those corresponding to the first
    # value in the combo box
    def load_items(self) -> None:
        for x in reversed(range(self.ui.tbl_items.rowCount())):
            self.ui.tbl_items.removeRow(x)

        Item.load_from_file()
        # After loading all items from file, the program only displays the item if its type matches the type selected in
        # the combo box
        r = 0
        for x in Item.ITEM_LIST:
            if x.item_type == self.ui.cmb_item_type.currentText():
                self.ui.tbl_items.insertRow(r)
                self.ui.tbl_items.setItem(r, 0, QTableWidgetItem(x.title))
                self.ui.tbl_items.setItem(r, 1, QTableWidgetItem(x.item_type))
                self.ui.tbl_items.setItem(r, 2, QTableWidgetItem(x.doa.strftime("%d/%m/%Y")))
                self.ui.tbl_items.setItem(r, 3, QTableWidgetItem(x.dom.strftime("%d/%m/%Y")))
                self.ui.tbl_items.setItem(r, 4, QTableWidgetItem(x.description))
                r += 1


# The TypeWindow class allows the user to add a new type to the list
# The view contains an add button and a clear button
class TypeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("UserInterface/add_types.ui", self)
        self.build_ui()
        self.setGeometry(0, 0, 700, 700)
        self._error_message = ""

    def build_ui(self):
        self.ui.lbl_name.setText(Item.NAME)
        self.ui.btn_add.clicked.connect(self.add_types)
        self.ui.btn_clear.clicked.connect(self.clear_items)

    # Validation check to ensure that the type field is not left empty
    def is_valid_input(self) -> bool:
        is_valid = True
        if not self.ui.txt_type.text():
            self._error_message += "Item type is missing.\n"
            is_valid = False

        return is_valid

    # Method to add a new category for the items
    def add_types(self):

        if not self.is_valid_input():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setGeometry(225, 250, 300, 300)
            msg.setText(self._error_message)
            msg.setWindowTitle("Error in Entry")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self._error_message = ""
            return

        # The entered type is stored in a variable and then added to the Item class variable TYPE_LIST
        # The file type.json is overwritten with the new contents in TYPE_LIST
        type_add = self.ui.txt_type.text()
        Item.TYPE_LIST.append(type_add)
        json_object = jsonpickle.dumps(Item.TYPE_LIST, unpicklable=False)
        with open("UserFiles/type.json", "w") as outfile:
            outfile.write(json_object)
        self.clear_items()

    # Clearing the type field
    def clear_items(self) -> None:
        self.ui.txt_type.clear()


# Function to show the window which allows the user to add new item
def add_items_window() -> None:
    w_add = AddWindow()
    w_add.show()


# Function to show the window which allows the user to add new types
def add_type_window() -> None:
    w_type = TypeWindow()
    w_type.show()


# Function to show the window which allows the user choose which item to edit and to delete items
def edit_items_window() -> None:
    w_edit = EditWindow()
    w_edit.show()


# Function to show the window which allows the user to show items by category
def show_items_window() -> None:
    w_show = ShowWindow()
    w_show.show()


# Function to exit program when exit button is pressed in the main menu
def exit_app() -> None:
    exit()


# Main function that runs the program
def main() -> None:
    app = QApplication(sys.argv)
    w_name = LoginWindow()

    # If statement checks whether the name.json file exists and has content in it
    # If this is false, then this is the first time the program is run and the login window is shown
    # The main menu view is the loaded from the LoginWindow class not the main function
    if (not os.path.isfile("UserFiles/name.json")) or (not os.path.getsize("UserFiles/name.json") > 0):
        w_name.show()
    else:
        # If the name file is found, the name is stored in the class variable NAME and the main menu screen is the first
        # window shown to the user
        Item.load_name()
        w = MenuWindow()
        w.show()

    sys.exit(app.exec_())


# Calling the main function
main()
