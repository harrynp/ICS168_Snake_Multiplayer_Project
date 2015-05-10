import tkinter

login = tkinter.Tk()
username = tkinter.Label(login, text = "Username:")
userEntry = tkinter.Entry(login)
password = tkinter.Label(login, text = "Password:")
passEntry = tkinter.Entry(login)
connect = tkinter.Button(login, text = "Connect", command = connect)
username.grid(row = 0, column = 0)
userEntry.grid(row = 0, column = 1)
password.grid(row = 1, column = 0)
passEntry.grid(row = 1, column = 1)
connect.grid(row = 2, column = 1)
login.mainloop()