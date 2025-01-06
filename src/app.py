import re
from os import getlogin
from platform import system, version, processor
from socket import gethostname
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from send_reminder import send_payment_reminder
from supabase_client import supabase
from layout_config import *
from paymentapp import PaymentApp

root = tk.Tk()
app = PaymentApp(root)
root.mainloop()
