from flask import Blueprint, render_template, redirect, request
from db import get_connection
from werkzeug.security import generate_password_hash
