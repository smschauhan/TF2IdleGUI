import Config
from PyQt4 import QtCore, QtGui
from sets import Set
from AccountDialog import Ui_AccountDialog
from SettingsDialog import Ui_SettingsDialog

class curry(object):
	def __init__(self, func, *args, **kwargs):
		self._func = func
		self._pending = args[:]
		self._kwargs = kwargs
	def __call__(self, *args, **kwargs):
		if kwargs and self._kwargs:
			kw = self._kwargs.copy()
			kw.update(kwargs)
		else:
			kw = kwargs or self._kwargs
		return self._func(*(self._pending + args), **kw)

class Ui_MainWindow(object):
	def __init__(self, MainWindow, settings):
		self.settings = settings
	
		# Create MainWindow
		self.MainWindow = MainWindow
		self.MainWindow.setObjectName('MainWindow')
		self.MainWindow.resize(700, 400)
		self.MainWindow.setWindowTitle('TF2Idle')
		
		# Add Tool bar
		self.toolBar = QtGui.QToolBar(self.MainWindow)
		self.toolBar.setObjectName('toolBar')
		self.toolBar.setIconSize(QtCore.QSize(40, 40))
		self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		self.toolBar.setMovable(False)
		
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("tf2logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		
		self.addAccountAction = self.toolBar.addAction(icon, 'Add account')
		QtCore.QObject.connect(self.addAccountAction, QtCore.SIGNAL('triggered()'), self.openAccountDialog)
		
		self.editAccountAction = self.toolBar.addAction(icon, 'Edit account')
		QtCore.QObject.connect(self.editAccountAction, QtCore.SIGNAL('triggered()'), curry(self.openAccountDialog, editAccount=True))
		
		self.deleteAccountsAction = self.toolBar.addAction(icon, 'Delete account')
		QtCore.QObject.connect(self.deleteAccountsAction, QtCore.SIGNAL('triggered()'), self.deleteAccounts)
		
		self.toolBar.addAction(icon, 'Start idling')
		self.toolBar.addAction(icon, 'Start log dropper')
		
		self.MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.toolBar)
		
		# Create layout widget and attach to MainWindow
		self.centralwidget = QtGui.QWidget(self.MainWindow)
		self.centralwidget.setObjectName('centralwidget')
		self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
		self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, self.MainWindow.width()-self.toolBar.width(), self.MainWindow.height()))
		self.verticalLayoutWidget.setObjectName('verticalLayoutWidget')
		self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
		self.verticalLayout.setMargin(0)
		self.verticalLayout.setObjectName('verticalLayout')
		self.MainWindow.setCentralWidget(self.centralwidget)
		
		# Add menu bar
		self.menubar = QtGui.QMenuBar(self.MainWindow)
		self.menubar.setObjectName('menubar')
		self.MainWindow.setMenuBar(self.menubar)
		
		# Add status bar
		#self.statusbar = QtGui.QStatusBar(self.MainWindow)
		#self.statusbar.setObjectName('statusbar')
		#self.MainWindow.setStatusBar(self.statusbar)
		
		# Add File menu
		menu = self.addMenu('File')
		self.addSubMenu(menu, 'Settings', text='Settings', statustip='Open settings', shortcut='Ctrl+S', action={'trigger':'triggered()', 'action':self.openSettings})
		self.addSubMenu(menu, 'Exit', text='Exit', statustip='Exit TF2Idle', shortcut='Ctrl+Q', action={'trigger':'triggered()', 'action':MainWindow.close})
		
		# Add About menu
		self.addMenu('About')
		
		QtCore.QMetaObject.connectSlotsByName(self.MainWindow)
		
		self.accountButtons = []
		self.updateAccountBoxes()

	def updateAccountBoxes(self):
		checkedbuttons = []
		for widget in self.accountButtons:
			if widget.isChecked():
				checkedbuttons.append(str(widget.text()))
			widget.close()
			del widget
		self.accountButtons = []
		row = 0
		column = 0
		numperrow = 4
		buttonheight = self.verticalLayoutWidget.height()/6
		
		for account in list(Set(self.settings.get_sections()) - Set(['Settings'])):
		#for account in self.settings.get_sections():
			self.settings.set_section(account)
			if self.settings.get_option('account_nickname') != '':
				accountname = self.settings.get_option('account_nickname')
			else:
				accountname = self.settings.get_option('steam_username')
			commandLinkButton = QtGui.QCommandLinkButton(self.verticalLayoutWidget)
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap('tf2logo.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
			commandLinkButton.setIcon(icon)
			commandLinkButton.setGeometry(QtCore.QRect(column*self.verticalLayoutWidget.width()/numperrow, row*buttonheight, self.verticalLayoutWidget.width()/numperrow, buttonheight))
			commandLinkButton.setCheckable(True)
			font = QtGui.QFont()
			# See why this doesn't work
			font.setFamily('TF2 Build')
			commandLinkButton.setFont(font)
			commandLinkButton.setChecked(accountname in checkedbuttons)
			commandLinkButton.setObjectName(self.settings.get_option('steam_username'))
			commandLinkButton.setText(accountname)
			self.accountButtons.append(commandLinkButton)
			commandLinkButton.show()
			column += 1
			if column == numperrow:
				row += 1
				column = 0
		

	def addMenu(self, menuname):
		self.menu = QtGui.QMenu(self.menubar)
		self.menu.setObjectName('menu' + menuname)
		self.menu.setTitle(menuname)
		self.menubar.addAction(self.menu.menuAction())
		return self.menu
	
	def addSubMenu(self, menu, menuname, shortcut=None, text=None, tooltip=None, statustip=None, action=None):
		self.action = QtGui.QAction(self.MainWindow)
		if shortcut:
			self.action.setShortcut(shortcut)
		self.action.setObjectName('action' + menuname)
		menu.addAction(self.action)
		if action:
			QtCore.QObject.connect(self.action, QtCore.SIGNAL(action['trigger']), action['action'])
		if text:
			self.action.setText(text)
		if tooltip:
			self.action.setToolTip(tooltip)
		if statustip:
			self.action.setStatusTip(statustip)
	
	def openAccountDialog(self, editAccount=False):
		if editAccount:
			checkedbuttons = []
			for widget in self.accountButtons:
				if widget.isChecked():
					checkedbuttons.append(str(widget.objectName()))
			if len(checkedbuttons) == 0:
				QtGui.QMessageBox.information(self.MainWindow, 'No accounts selected', 'Please select an account to edit')
			elif len(checkedbuttons) > 1:
				QtGui.QMessageBox.information(self.MainWindow, 'More than one account selected', 'Please select a single account to edit')
			else:
				dialogWindow = AccountDialogWindow(self.settings, account='Account-'+checkedbuttons[0])
				dialogWindow.setModal(True)
				dialogWindow.exec_()
				self.updateAccountBoxes()
		else:
			dialogWindow = AccountDialogWindow(self.settings)
			dialogWindow.setModal(True)
			dialogWindow.exec_()
			self.updateAccountBoxes()

	def deleteAccounts(self):
		checkedbuttons = []
		for widget in self.accountButtons:
			if widget.isChecked():
				checkedbuttons.append(str(widget.objectName()))
		if len(checkedbuttons) == 0:
			QtGui.QMessageBox.information(self.MainWindow, 'No accounts selected', 'Please select at least one account to delete')
		else:
			reply = QtGui.QMessageBox.warning(self.MainWindow, 'Warning', 'Are you sure to want to delete these accounts?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				for account in checkedbuttons:
					self.settings.set_section('Account-' + account)
					self.settings.remove_section()
				self.updateAccountBoxes()
	
	def openSettings(self):
		dialogWindow = SettingsDialogWindow(self.settings)
		dialogWindow.setModal(True)
		dialogWindow.exec_()
	
class AccountDialogWindow(QtGui.QDialog):
	def __init__(self, settings, account=None, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.ui = Ui_AccountDialog(self, settings, account)

class SettingsDialogWindow(QtGui.QDialog):
	def __init__(self, settings, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.ui = Ui_SettingsDialog(self, settings)