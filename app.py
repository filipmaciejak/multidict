import json, qdarktheme, sys, parser, os
from PyQt6 import QtWidgets, uic

class Ui(QtWidgets.QMainWindow):

    def __init__(self, app):
        super(Ui, self).__init__()

        self.app = app

        uic.loadUi("g.ui", self)
        self.connect_events()
        self.setup()

    def setup(self):
        self.lightStyleSheet = qdarktheme.load_stylesheet("light")
        self.darkStyleSheet = qdarktheme.load_stylesheet()

        self.parser = parser.Parser('english')
        self.parser.word = None

        self.user = None
        self.saved_words = {'english':{},'french':{},'polish':{},'spanish':{}}
        self.saved_file = None
        self.preferences = json.load(open('config.json', 'r', encoding='utf-8'))
        self.f_actionChangeUser(self.preferences['user'])()
        self.favButton.setText('☆')

        self.userActions = {}
        
        for user in self.preferences:
            if user == 'user':
                continue
            action = self.menuUser.addAction(user)
            action.triggered.connect(self.f_actionChangeUser(user))
            self.userActions[user] = action
        
        self.setWindowTitle('Dictionary - ' + self.parser.lang.title() + ' - ' + self.user)
    
    def connect_events(self):
        self.actionHelp.triggered.connect(self.f_actionHelp)
        self.actionNewUser_2.triggered.connect(self.f_actionNewUser)
        self.actionLightMode.triggered.connect(self.f_actionMode('light'))
        self.actionDarkMode.triggered.connect(self.f_actionMode('dark'))
        self.actionAbout.triggered.connect(self.f_actionAbout)
        self.actionChangeName.triggered.connect(self.f_actionChangeName)
        self.actionDeleteUser.triggered.connect(self.f_actionDeleteUser)
        self.searchButton.clicked.connect(self.f_search)
        self.actionChooseLangEn.triggered.connect(self.f_actionChooseLang('english'))
        self.actionChooseLangFr.triggered.connect(self.f_actionChooseLang('french'))
        self.actionChooseLangPl.triggered.connect(self.f_actionChooseLang('polish'))
        self.actionChooseLangEs.triggered.connect(self.f_actionChooseLang('spanish'))
        self.lineEdit.editingFinished.connect(self.f_search)
        self.favButton.clicked.connect(self.f_actionFav)
        self.listWords.itemClicked.connect(self.f_actionItemClicked)

    def f_search(self):
        self.parser.word = self.lineEdit.text()
        if self.parser.word not in self.saved_words[self.parser.lang]:
            text = self.parser.fetch()
            self.textBrowser.setText(text)
            self.favButton.setText('☆')
        else:
            text = self.saved_words[self.parser.lang][self.parser.word]
            self.parser.result = text
            self.textBrowser.setText(text)
            self.favButton.setText('★')
    
    def f_actionFav(self):
        if self.parser.word == None:
            return
        if self.parser.word in self.saved_words[self.parser.lang]:
            self.saved_words[self.parser.lang].pop(self.parser.word)
            self.favButton.setText('☆')
        else:
            self.saved_words[self.parser.lang][self.parser.word] = self.parser.result
            self.favButton.setText('★')
        self.reset_list()
    
    def f_actionItemClicked(self, item):
        self.lineEdit.setText(item.text())
        self.f_search()

    def f_actionHelp(self):
        print('action - Help')
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Help")
        dlg.setText("In the Options you can choose the target language. Type a word and either press Enter or the search button in order to look it up. By using the star icon you can save (or unsave) the current word on your machine for offline access. You can also change between light and dark display mode in the Options. All configurations will be saved between sessions, separately for each user.\n\nEnjoy :)")
        button = dlg.exec()
        if button == QtWidgets.QMessageBox.StandardButton.Ok:
            print("Ok")
    
    def f_actionNewUser(self):
        print('action - NewUser')
        name = 'User ' + str(len(self.preferences))
        self.preferences[name] = dict(self.preferences[self.user])
        self.preferences[name]['file'] = 'storage/' + str(hash(name)) + '.json'
        action = self.menuUser.addAction(name)
        action.triggered.connect(self.f_actionChangeUser(name))
        self.userActions[name] = action
        self.f_actionChangeUser(name)()

    def f_actionMode(self, mode):
        def f_tmp():
            print('action - Mode: ' + str(mode))
            if mode == 'light':
                app.setStyleSheet(self.lightStyleSheet)
            elif mode == 'dark':
                app.setStyleSheet(self.darkStyleSheet)
            if self.user != None:
                self.preferences[self.user]['mode'] = mode
        return f_tmp

    def f_actionAbout(self):
        print('action - About')
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("About")
        dlg.setText("This is a simple dictionary app. It uses data from Wiktionary.\n\nby Filip Maciejak, 2022")
        button = dlg.exec()
        if button == QtWidgets.QMessageBox.StandardButton.Ok:
            print("Ok")
    
    def f_actionChooseLang(self, lang):
        def f_tmp():
            print('action - Choose Language: ' + str(lang))
            self.parser.lang = lang
            self.setWindowTitle('Dictionary - ' + self.parser.lang.title() + ' - ' + self.user)
            if self.user != None:
                self.preferences[self.user]['language'] = lang
            self.reset_list()
        return f_tmp
    
    def f_actionChangeName(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Change Username', 'New Username:')
        if not ok:
            return
        self.preferences[text] = self.preferences[self.user]
        self.preferences.pop(self.user)
        self.menuUser.removeAction(self.userActions[self.user])
        self.userActions.pop(self.user)
        action = self.menuUser.addAction(text)
        action.triggered.connect(self.f_actionChangeUser(text))
        self.userActions[text] = action

        self.user = text
        self.setWindowTitle('Dictionary - ' + self.parser.lang.title() + ' - ' + self.user)

    def f_actionDeleteUser(self):
        if len(self.preferences) <= 2:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Invalid action")
            dlg.setText("You can't remove a user if there's just one!")
            button = dlg.exec()
            if button == QtWidgets.QMessageBox.StandardButton.Ok:
                print("Ok")
            return
        user_to_remove = self.user
        for user in self.preferences:
            if user == 'user' or user == self.user:
                continue
            self.f_actionChangeUser(user)()
            break
        os.remove(self.preferences[user_to_remove]['file'])
        self.preferences.pop(user_to_remove)
        self.menuUser.removeAction(self.userActions[user_to_remove])
    
    def f_actionChangeUser(self, user):
        def f_tmp():
            # save previous
            if self.user != None:
                with open(self.saved_file, 'w', encoding='utf-8') as f:
                    json.dump(self.saved_words, f, ensure_ascii=False, indent=4)
            # setup
            self.user = user
            print('action - Choose User: ' + str(user))
            self.f_actionChooseLang(self.preferences[self.user]['language'])()
            self.f_actionMode(self.preferences[self.user]['mode'])()
            self.setWindowTitle('Dictionary - ' + self.parser.lang.title() + ' - ' + self.user)
            self.saved_file = self.preferences[self.user]['file']
            try:
                self.saved_words = json.load(open(self.saved_file, 'r', encoding='utf-8'))
            except:
                self.saved_words = {'english':{},'french':{},'polish':{},'spanish':{}}
            self.parser.word = ''
            self.favButton.setText('☆')
            self.textBrowser.setText('')
            self.lineEdit.setText('')
            self.reset_list()

        return f_tmp
    
    def reset_list(self):
        self.listWords.clear()
        for s_word in sorted(self.saved_words[self.parser.lang]):
            self.listWords.addItem(s_word)
    
    def closeEvent(self, event):
        with open(self.saved_file, 'w', encoding='utf-8') as f:
            json.dump(self.saved_words, f, ensure_ascii=False, indent=4)
        with open('config.json', 'w', encoding='utf-8') as f:
            self.preferences['user'] = self.user
            json.dump(self.preferences, f, ensure_ascii=False, indent=4)
        event.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Ui(app)
    w.show()
    app.exec()