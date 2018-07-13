from easygui import *
from passlib.hash import pbkdf2_sha256
import pendulum, smtplib, sys, pickle
import secrets as s

#Global Variables declared here:
Username = ''
UserMadeOn = ''
NotesList = []

#Class Definitions here:
class stickynote(object):
	def __init__(self, body = '', madeon = pendulum.now(), scheduledate = '', scheduleinterval = 0, alertcount = 0, category = 'none', complete = False):
		self.body = body
		self.scheduledate = scheduledate
		self.scheduleinterval = scheduleinterval
		self.alertcount = alertcount
		self.category = category
		self.madeon = pendulum.now()
		self.complete = complete
	def getbody(self):
		return self.body
	def getscheduledate(self):
		return self.scheduledate
	def getscheduleinterval(self):
		return self.scheduleinterval
	def getalertcount(self):
		return self.alertcount
	def getmadeon(self):
		return self.madeon
	def isitdone(self):
		return self.complete
	
	def addalert(self):			#Increment alertcount
		self.alertcount += 1
	def completed(self):		#Change complete to True
		self.complete = True

		
#Helper functions here:
def rot13(string1):
	intab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	outtab = "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
	trantab = string1.maketrans(intab, outtab)
	transs = string1.translate(trantab)
	#I can't believe I'm using a rot13 as "encryption", but it'll do with the pickle against plaintext reading at least
	#Just meant to stop casual people poking around
	#It'll fall like an airplane doesn't in front of anyone who knows what they're doing, but it's a sticky note program ffs, what encryption do we need really
	return transs
	
def sendemail(from_addr, to_addr_list, cc_addr_list, subject, message, login, password, smtpserver='smtp.gmail.com:587'):
	header  = 'From: {0}\n'.format(from_addr)
	header += 'To: {0}\n'.format(','.join(to_addr_list))
	header += 'Cc: {0}\n'.format(','.join(cc_addr_list))
	header += 'Subject: {0}\n\n'.format(subject)
	message = header + message
	server = smtplib.SMTP(smtpserver)
	server.starttls()
	server.login(login,password)
	problems = server.sendmail(from_addr, to_addr_list, message)
	server.quit()


#Main program functions here:
def readuserinfo():
	try:
		file = open('data.txt', 'r+')
		file.close()
		print('data.txt found')
	except FileNotFoundError:	#Make the file and have user enter in user/pass combo
		print('data.txt not found')
		file = open('data.txt', 'w+')
		#Username input starts here
		username = None
		while username == None:
			username = enterbox('Please enter a username here', 'Username Input')
			if username == None:
				msgbox('Please enter a username to continue', 'Username Input')
		print('username made')
		#Password input starts here
		password = None
		passwordconf = None
		while True:
			password = passwordbox('Please enter a password here', 'Password Input')
			if password == None:
				msgbox('Please enter a password to continue', 'Password Input')
			else:
				passwordconf = passwordbox('Type your password again for confirmation', 'Password Input')
				if passwordconf == None:
					msgbox('Please enter a password to continue', 'Password Input')
				elif passwordconf != password:
					msgbox('Your passwords don\'t match.', 'Password Input')
				else:
					msgbox('Username/Password created', 'StickyNotes')
					break
		print('password made')
		#Recovery email input starts here
		email = None
		emailconf = None
		while True:
			email = enterbox('Please enter your recovery email here', 'Email Input')
			if email == None:
				msgbox('Please enter an email to continue', 'Email Input')
			else:
				emailconf = enterbox('Type your recovery email again for confirmation', 'Email Input')
				if emailconf == None:
					msgbox('Please enter an email to continue', 'Email Input')
				elif emailconf != email:
					msgbox('Your emails don\'t match.', 'Email Input')
				else:
					msgbox('Email verified', 'StickyNotes')
					break
		print('email confirmed')
		hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=64)
		print('password hashed/salted')
		datahere = [rot13(username), rot13(str(pendulum.now())), rot13(hash), rot13(email)]
		file.close()
		with open('data.txt', 'wb') as file:
			pickle.dump(datahere, file)
		print('data dumped into data.txt')
		
	global Username, UserMadeOn
	with open('data.txt', 'rb') as file:
		line1 = pickle.load(file)
	Username = rot13(line1[0])
	UserMadeOn = rot13(line1[1])
	print('username and creation date set')

def matchuserpass():
	print('password verification starting')
	with open('data.txt', 'rb') as file:
		bigdata = pickle.load(file)
	global Username
	hash = rot13(bigdata[2])
	attempts = 0
	while True:
		userinput = passwordbox('Please enter the password for {0}'.format(Username), 'Verification')
		if pbkdf2_sha256.verify(userinput, hash) == True:
			print('password verified')
			break
		else:
			msgbox('Wrong password, try again.', 'Verification')
			print('password not verified, trying again')
			attempts += 1
		if attempts >= 5: #Security protection here
			print('attempt limit reached')
			password1 = s.token_hex(64)
			print('token made')
			hash1 = pbkdf2_sha256.encrypt(password1, rounds=200000, salt_size=64)
			bigdata = [rot13(hash1) if rot13(x) == hash else x for x in bigdata]
			with open('data.txt', 'wb') as file:
				pickle.dump(bigdata, file)
			print('token dumped')
			message = 'Hi {0},\n\n You (or some other malicious agent) has just tried to access your account and failed. For your security, we\'ve locked  your account.\n\n To access your account, paste the following code as your password: {1}\n\nSincerely,\nStickyNotes'.format(Username, password1)
			print('sending email...')
			sendemail('myprogram3000@gmail.com', [rot13(bigdata[3])], [], 'Recover Your StickyNotes Account', message, 'myprogram3000', 'fishdis1')
			print('email sent')
			sys.exit()

def loadnotes():
	print('note loading starting')
	global NotesList
	try: #Look for the file. If it exists, pass.
		file = open('data2.txt', 'r+')
		file.close()
		print('data2.txt found')
	except FileNotFoundError: #Make the file
		print('data2.txt not found')
		file = open('data2.txt', 'w+')
		print('data2.txt made')
		file.close()
	#Loads the stickynote list into the NotesList global variable.
	with open('data2.txt', 'rb') as file:
		try:
			NotesList = pickle.load(file)
			print('noteslist loaded')
		except: #If data2.txt is empty, NotesList is kept empty
			print('noteslist is empty')
			
def viewuserinfo():
	print('user info displayed')
	year = UserMadeOn[:4]
	month = UserMadeOn[5:7]
	day = UserMadeOn[8:10]
	while True:
		contents = 'Username: {0}\nUser created on {1}/{2}/{3}'.format(Username, day, month, year)
		reply = buttonbox(contents, choices = ['Change password', 'Return to main menu'])
		if reply == 'Change password':
			print('change password selected')
			with open('data.txt', 'rb') as file:
				bigdata = pickle.load(file)
			print('data loaded')
			originalhash = rot13(bigdata[2])
			userinput = passwordbox('Enter your current password', 'Change Password')
			try:
				if pbkdf2_sha256.verify(userinput, originalhash) == True:
					print('original password verified')
					userinput2 = passwordbox('Enter your new password', 'Change Password')
					if userinput2 != None:
						userinput3 = passwordbox('Re-enter your new password', 'Change Password')
						if userinput2 == userinput3:
							print('new password verified')
							hash = pbkdf2_sha256.encrypt(userinput3, rounds=200000, salt_size=64)
							print('new password hashed/salted')
							bigdata = [rot13(hash) if rot13(x) == originalhash else x for x in bigdata]
							with open('data.txt', 'wb') as file:
								pickle.dump(bigdata, file)
							print('data dumped')
							msgbox('Your password was successfully changed', 'Password Change Success', 'Return to user info')
						else:
							print('new password did not match')
							msgbox('Your password verification did not match, try again', 'Change Password')
				else:
					msgbox('Incorrect password', 'Change Password')
					print('wrong password')
			except TypeError:
				msgbox('Please enter a password', 'Change Password')
				print('password change cancelled by user')
		else:
			break

def viewprograminfo():
	print('program info displayed')
	global Username
	credits = 'Version 0.4 (login complete)\nThis was made on a whim, so don\'t expect much\n\nCurrently, this program:\n-Salts and hashes passwords, never stores plaintext\n-Can email a recovery key\n-Has a GUI (harder than you may think)\n\nMade by Michael Nakai\nContact the guy who made this at mnakai.zj9@gmail.com'
	while True:
		p = buttonbox(credits, choices = ['Report a bug', 'Return to main menu'])
		if p == 'Report a bug':
			print('bug reporting selected')
			contents = enterbox('Describe the bug below', 'Bug Reporting')
			if contents != None:
				print('sending email...')
				sendemail('myprogram3000@gmail.com', ['mnakai.zj9@gmail.com'], [], 'Bug Report from {0}'.format(Username), 'On {0}, {1} reported:\n\n{2}'.format(pendulum.now(),Username,contents), 'myprogram3000', 'fishdis1')
				print('email sent')
			else:
				print('bug reporting cancelled by user')
		else:
			break

def viewnotes():
	print('notes viewer opened')
	#	//TODO Add note viewer/add note code here
	pass
			
def mainwindow():
	print('main window displayed')
	choices = ['Show active notes', 'View or change user info', 'Info/Bug Reporting', 'Exit']
	return buttonbox('What would you like to do?', choices = choices)
	
######Main execution here######
if __name__ == '__main__':
	readuserinfo() #Looks for data.txt and updates Username. If txt doesn't exist, it makes it with info.
	matchuserpass() #Asks for userpass. If wrong pass, keeps asking and user will get stuck here. After 5 wrong guesses, program closes and shoots a recovery email.
	loadnotes() #Loads any notes in data2.txt into 
	while True:
		choice = mainwindow() #Shows the user the main choices (notes, user info, program info, exit)
		if choice == None or choice == 'Exit': #User wants out, now
			break
		if choice == 'Info/Bug Reporting':
			viewprograminfo()
		elif choice == 'View or change user info':
			viewuserinfo()
		elif choice == 'Show active notes':
			viewnotes()
			
	print('exiting program...')
	sys.exit()