from flask import Flask, render_template, request, redirect, url_for, session, abort
import pymysql
from flask_mysqldb import MySQL
from flask_cors import CORS
import re
from datetime import timedelta

app = Flask(__name__)
# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

