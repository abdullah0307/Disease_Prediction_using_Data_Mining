import csv
import re

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets

import About
import Register
import Warning
from GUI import Ui_MainWindow


class Main:

    def __init__(self):
        # load the data
        self.dataset = pd.read_csv("data/disease_dataset.csv")
        self.user_database = pd.read_csv("data/users.csv")
        # clean the data
        self.dataset = self.clean_data(self.dataset)
        # Make a copy of the dataset
        self.test = self.dataset.copy()
        # Symptoms will choose by the user
        self.options_selected = []
        # Counter of the column number
        self.column = 1

        # todo main_window
        self.main_window = QtWidgets.QMainWindow()
        self.main_obj = Ui_MainWindow()
        self.main_obj.setupUi(self.main_window)

        # todo Register Window
        self.register_window = QtWidgets.QDialog()
        self.register_obj = Register.Ui_Dialog()
        self.register_obj.setupUi(self.register_window)

        # todo warning window
        self.warning_window = QtWidgets.QDialog()
        self.warning_obj = Warning.Ui_Dialog()
        self.warning_obj.setupUi(self.warning_window)

        # todo about window
        self.about_window = QtWidgets.QDialog()
        self.about_obj = About.Ui_Dialog()
        self.about_obj.setupUi(self.about_window)

        # todo disable input frames
        self.main_obj.frame_7.setVisible(False)

        # todo buttons on click listener
        self.main_obj.pushButton.clicked.connect(
            lambda: self.main_obj.stackedWidget.setCurrentWidget(self.main_obj.page_2))
        self.main_obj.listWidget.itemDoubleClicked.connect(self.list_item_clicked)
        self.main_obj.pushButton_5.clicked.connect(self.list_item_clicked)
        self.main_obj.pushButton_3.clicked.connect(self.predict_disease)
        self.main_obj.pushButton_7.clicked.connect(self.register_link)
        self.register_obj.pushButton.clicked.connect(self.register)
        self.main_obj.pushButton_2.clicked.connect(self.show_about)
        self.about_obj.pushButton.clicked.connect(lambda: self.about_window.destroy())
        self.main_obj.pushButton_4.clicked.connect(self.input_again)

        # todo update the list of the symptoms options
        self.update_list_symptoms()

        # todo empty the dataset
        self.dataset = pd.DataFrame(index=[], columns=self.dataset.columns)

        # todo set the page to first page
        self.main_obj.stackedWidget.setCurrentWidget(self.main_obj.page)

        # todo login button
        self.main_obj.pushButton_6.clicked.connect(self.login)

    def input_again(self):
        # clear the symptoms list
        self.main_obj.listWidget_2.clear()
        # load the disease data
        self.dataset = pd.read_csv("data/disease_dataset.csv")
        # load the users data
        self.user_database = pd.read_csv("data/users.csv")
        # clean the data
        self.dataset = self.clean_data(self.dataset)
        # Make a copy of the dataset
        self.test = self.dataset.copy()
        # Symptoms will choose by the user
        self.options_selected = []
        # Counter of the column number
        self.column = 1

        # todo update the list of the symptoms options
        self.update_list_symptoms()

        # todo empty the dataset
        self.dataset = pd.DataFrame(index=[], columns=self.dataset.columns)

        # todo set the page to first page
        self.main_obj.stackedWidget.setCurrentWidget(self.main_obj.page)

    def reload(self):
        self.user_database = pd.read_csv("data/users.csv")

    def encode(self, password):
        encode = ""
        for i in password:
            encode = encode + chr(ord(i) + 18)
        return encode

    def decode(self, password):
        decode = ""
        for i in password:
            decode = decode + chr(ord(i) - 18)
        return decode

    def show_about(self):
        self.about_window.show()

    def check_valid(self, email):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # pass the regular expression
        # and the string in search() method
        if re.search(regex, email):
            return True
        else:
            return False

    def register_link(self):
        self.register_window.show()

    def register(self):
        email = self.register_obj.lineEdit.text()
        password = self.register_obj.lineEdit_2.text()
        password_confirm = self.register_obj.lineEdit_3.text()

        # to check that the fields are empty or not
        if email is "" or password is "" or password_confirm is "":
            self.warning_obj.label_2.setText("Fields are empty")
            self.warning_window.show()
            return
        # to check that the inputted email is valid or not
        elif not self.check_valid(email):
            self.warning_obj.label_2.setText("email is invalid")
            self.warning_window.show()
            return
        # To check that the email is already taken or not
        elif self.user_exists(email):
            self.warning_obj.label_2.setText("email already exists")
            self.warning_window.show()
            return
        # To check that the password matches or not
        elif not password == password_confirm:
            self.warning_obj.label_2.setText("Passwords not match")
            self.warning_window.show()
            return

        # encoding the password
        password = self.encode(password)

        # create a new user entry
        row = [email, password]
        with open("data/users.csv", "a") as f:
            wo = csv.writer(f, lineterminator='\n')
            wo.writerow(row)

        # reload the user database
        self.user_database = pd.read_csv("data/users.csv")

        # After this destroy the window
        self.register_window.destroy()

    def check_user(self, email, password):
        # reload the user database
        self.reload()

        for i in self.user_database['email']:
            if i == email:
                key = self.user_database[self.user_database['email'] == i]['password'].values[0]
                # decoding the password
                key = self.decode(key)
                if str(key) == str(password):
                    return True
        return False

    def user_exists(self, email):
        for i in self.user_database['email']:
            if i == email:
                return True
        return False

    def login(self):
        input_email = self.main_obj.lineEdit.text()
        input_password = self.main_obj.lineEdit_2.text()

        if self.check_user(input_email, input_password):
            self.main_obj.frame_8.setVisible(False)
            self.main_obj.frame_7.setVisible(True)
        else:
            self.warning_obj.label_2.setText("Wrong email or password")
            self.warning_window.show()

    def clean_data(self, dataset):
        cols = dataset.columns
        data = dataset[cols].values.flatten()

        s = pd.Series(data)
        s = s.str.strip()
        s = s.values.reshape(dataset.shape)

        dataset = pd.DataFrame(s, columns=dataset.columns)

        return dataset

    def update_list_symptoms(self):
        # return if column ends
        if len(self.dataset.columns) == self.column:
            return

        # clear all the list
        self.main_obj.listWidget.clear()

        options = []

        # Extract the options from the column
        for i in self.dataset.iloc[:, self.column].unique():
            if not i in self.options_selected and i != np.nan:
                options.append(i)

        # if options are ended then predict the disease
        if not options:
            self.main_obj.stackedWidget.setCurrentWidget(self.main_obj.page_3)
            self.main_obj.label_5.setText("You may have " + str([i for i in self.dataset.iloc[:, 0].unique()]))

        # update the list with the column number
        for i in options:
            if str(i) == 'nan':
                continue
            self.main_obj.listWidget.addItem(i)

    def predict_disease(self):
        self.main_obj.stackedWidget.setCurrentWidget(self.main_obj.page_3)
        for i in self.dataset.iloc[:, 0].unique():
            self.main_obj.listWidget_3.addItem(i)

    def list_item_clicked(self):
        # add the item to symptoms list
        r = self.main_obj.listWidget.currentRow()
        sy = self.main_obj.listWidget.item(r).text()
        self.main_obj.listWidget_2.addItem(sy)
        self.options_selected.append(sy)

        # Reduce the test df according to the symptoms
        for i in self.dataset.columns[1:]:
            if self.test[self.test[i] == sy].empty:
                continue
            self.test = self.test[self.test[i] == sy]
            self.dataset = pd.concat([self.dataset, self.test], ignore_index=True)

        # move to next column
        self.column += 1

        # update the list widget
        self.update_list_symptoms()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    obj = Main()
    obj.main_window.show()
    sys.exit((app.exec_()))
