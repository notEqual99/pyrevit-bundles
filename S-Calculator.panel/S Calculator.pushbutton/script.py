# -*- coding: utf-8 -*-
"""Scientific Calculator
"""
__title__ = 'Scientific\nCalculator'
__author__ = 'Phyo Pyae Zaw'

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import (
    Form, Button, TextBox, Label,
    FormStartPosition, FormBorderStyle,
    HorizontalAlignment
)
from System.Drawing import Point, Size, Color, Font, FontStyle, ContentAlignment
import math

class CalculatorForm(Form):
    def __init__(self):
        self.Text = 'Scientific Calculator'
        self.Size = Size(400, 600)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.MaximizeBox = False

        self.expression = ''
        self.memory = 0
        self.angle_mode = 'deg'
        self.inverse_mode = False

        self.setup_ui()

    def setup_ui(self):
        self.display = TextBox()
        self.display.Location = Point(10, 10)
        self.display.Size = Size(360, 40)
        self.display.Font = Font('Segoe UI', 14)
        self.display.TextAlign = HorizontalAlignment.Right
        self.display.Text = ''
        self.display.BackColor = Color.White
        self.Controls.Add(self.display)

        self.mode_label = Label()
        self.mode_label.Location = Point(10, 55)
        self.mode_label.Size = Size(360, 20)
        self.mode_label.Font = Font('Segoe UI', 9)
        self.mode_label.TextAlign = ContentAlignment.MiddleRight
        self.mode_label.Text = 'Mode: Degrees'
        self.mode_label.ForeColor = Color.Red
        self.Controls.Add(self.mode_label)

        buttons = [
            [('MC', 'MC'), ('MR', 'MR'), ('M+', 'M+'), ('M-', 'M-'), ('C', 'C')],
            # Row 2 - Scientific functions (will change with INV)
            [('sin', 'sin'), ('cos', 'cos'), ('tan', 'tan'), ('√', 'sqrt'), ('x²', '^2')],
            # Row 3 - Scientific functions
            [('ln', 'ln'), ('log', 'log'), ('π', 'pi'), ('e', 'e'), ('x^y', '^')],
            # Row 4 - Inverse and mode buttons
            [('INV', 'INV'), ('DEG', 'DEG'), ('(', '('), (')', ')'), ('←', 'BS')],
            # Row 5 - Numbers and operators
            [('7', '7'), ('8', '8'), ('9', '9'), ('÷', '/'), ('Ans', 'Ans')],
            # Row 6
            [('4', '4'), ('5', '5'), ('6', '6'), ('×', '*'), ('1/x', '1/x')],
            # Row 7
            [('1', '1'), ('2', '2'), ('3', '3'), ('-', '-'), ('+/-', 'NEG')],
            # Row 8
            [('0', '0'), ('.', '.'), ('=', '='), ('+', '+'), ('EXP', 'EXP')]
        ]

        y_offset = 85
        button_width = 70
        button_height = 50
        spacing = 5

        self.trig_buttons = {}

        for row in buttons:
            x_offset = 10
            for label, action in row:
                btn = Button()
                btn.Text = label
                btn.Location = Point(x_offset, y_offset)
                btn.Size = Size(button_width, button_height)
                btn.Font = Font('Segoe UI', 11, FontStyle.Bold)
                btn.Tag = action

                if action in ['sin', 'cos', 'tan']:
                    self.trig_buttons[action] = btn

                # Color coding
                if action in ['C', 'BS']:
                    btn.BackColor = Color.FromArgb(255, 200, 200)
                elif action == '=':
                    btn.BackColor = Color.FromArgb(135, 206, 250)
                elif action in ['+', '-', '*', '/', '^']:
                    btn.BackColor = Color.FromArgb(255, 228, 181)
                elif action in ['sin', 'cos', 'tan', 'sqrt', 'ln', 'log']:
                    btn.BackColor = Color.FromArgb(216, 191, 216)
                elif action in ['MC', 'MR', 'M+', 'M-']:
                    btn.BackColor = Color.FromArgb(173, 216, 230)
                elif action in ['DEG', 'INV']:
                    btn.BackColor = Color.FromArgb(144, 238, 144)
                    if action == 'DEG':
                        self.deg_button = btn
                    elif action == 'INV':
                        self.inv_button = btn
                else:
                    btn.BackColor = Color.WhiteSmoke

                btn.Click += self.button_click
                self.Controls.Add(btn)

                x_offset += button_width + spacing

            y_offset += button_height + spacing

        self.last_answer = '0'

    def button_click(self, sender, event):
        action = sender.Tag

        try:
            if action == 'C':
                self.expression = ''
                self.display.Text = ''

            elif action == 'BS':
                if len(self.expression) > 0:
                    self.expression = self.expression[:-1]
                    self.display.Text = self.expression

            elif action == '=':
                if self.expression:
                    result = self.evaluate_expression(self.expression)
                    self.last_answer = str(result)
                    self.display.Text = str(result)
                    self.expression = str(result)

            elif action == 'MC':
                self.memory = 0

            elif action == 'MR':
                self.expression += str(self.memory)
                self.display.Text = self.expression

            elif action == 'M+':
                if self.expression:
                    result = self.evaluate_expression(self.expression)
                    self.memory += float(result)

            elif action == 'M-':
                if self.expression:
                    result = self.evaluate_expression(self.expression)
                    self.memory -= float(result)

            elif action == 'DEG':
                self.angle_mode = 'rad' if self.angle_mode == 'deg' else 'deg'
                sender.Text = 'RAD' if self.angle_mode == 'rad' else 'DEG'
                self.mode_label.Text = 'Mode: ' + ('Radians' if self.angle_mode == 'rad' else 'Degrees')
                if self.inverse_mode:
                    self.mode_label.Text += ' [INV]'

            elif action == 'INV':
                self.inverse_mode = not self.inverse_mode

                if self.inverse_mode:
                    sender.BackColor = Color.FromArgb(255, 200, 100)
                    self.trig_buttons['sin'].Text = 'asin'
                    self.trig_buttons['cos'].Text = 'acos'
                    self.trig_buttons['tan'].Text = 'atan'
                    self.mode_label.Text = 'Mode: ' + ('Radians' if self.angle_mode == 'rad' else 'Degrees') + ' [INV]'
                else:
                    sender.BackColor = Color.FromArgb(144, 238, 144)
                    self.trig_buttons['sin'].Text = 'sin'
                    self.trig_buttons['cos'].Text = 'cos'
                    self.trig_buttons['tan'].Text = 'tan'
                    self.mode_label.Text = 'Mode: ' + ('Radians' if self.angle_mode == 'rad' else 'Degrees')

            elif action == 'NEG':
                if self.expression:
                    if self.expression.startswith('-'):
                        self.expression = self.expression[1:]
                    else:
                        self.expression = '-' + self.expression
                    self.display.Text = self.expression

            elif action == 'Ans':
                self.expression += self.last_answer
                self.display.Text = self.expression

            elif action == 'pi':
                self.expression += str(math.pi)
                self.display.Text = self.expression

            elif action == 'e':
                self.expression += str(math.e)
                self.display.Text = self.expression

            elif action == '^2':
                self.expression += '**2'
                self.display.Text = self.expression

            elif action == '1/x':
                self.expression += '**(- 1)'
                self.display.Text = self.expression

            elif action == 'EXP':
                self.expression += 'e'
                self.display.Text = self.expression

            elif action == 'sqrt':
                self.expression += 'sqrt('
                self.display.Text = self.expression

            elif action == 'ln':
                self.expression += 'ln('
                self.display.Text = self.expression

            elif action == 'log':
                self.expression += 'log('
                self.display.Text = self.expression

            elif action in ['sin', 'cos', 'tan']:
                if self.inverse_mode:
                    self.expression += 'a' + action + '('
                else:
                    self.expression += action + '('
                self.display.Text = self.expression

            else:
                self.expression += action
                self.display.Text = self.expression

        except Exception as e:
            self.display.Text = 'Error: ' + str(e)
            self.expression = ''

    def evaluate_expression(self, expr):
        """Evaluate the mathematical expression"""
        try:
            expr = expr.replace('×', '*')
            expr = expr.replace('÷', '/')

            expr = self.process_functions(expr)

            result = eval(expr)

            if abs(result) < 1e-10:
                result = 0.0
            elif abs(result - round(result)) < 1e-10:
                result = round(result)
            else:
                result = round(result, 10)

            return result

        except Exception as e:
            raise Exception(str(e))

    def process_functions(self, expr):
        """Process mathematical functions in the expression"""
        expr = expr.replace('ln(', '__LN__(')
        expr = expr.replace('log(', '__LOG__(')
        expr = expr.replace('sqrt(', '__SQRT__(')

        if self.angle_mode == 'deg':
            if 'asin(' in expr:
                expr = expr.replace('asin(', '__ASIN__(')

            if 'acos(' in expr:
                expr = expr.replace('acos(', '__ACOS__(')

            if 'atan(' in expr:
                expr = expr.replace('atan(', '__ATAN__(')
        else:
            expr = expr.replace('asin(', '__ASIN_RAD__(')
            expr = expr.replace('acos(', '__ACOS_RAD__(')
            expr = expr.replace('atan(', '__ATAN_RAD__(')

        if self.angle_mode == 'deg':
            expr = expr.replace('sin(', '__SIN__(')
            expr = expr.replace('cos(', '__COS__(')
            expr = expr.replace('tan(', '__TAN__(')
        else:
            expr = expr.replace('sin(', '__SIN_RAD__(')
            expr = expr.replace('cos(', '__COS_RAD__(')
            expr = expr.replace('tan(', '__TAN_RAD__(')

        expr = expr.replace('__LN__(', 'math.log(')
        expr = expr.replace('__LOG__(', 'math.log10(')
        expr = expr.replace('__SQRT__(', 'math.sqrt(')

        expr = expr.replace('__ASIN__(', 'math.degrees(math.asin(')
        expr = expr.replace('__ACOS__(', 'math.degrees(math.acos(')
        expr = expr.replace('__ATAN__(', 'math.degrees(math.atan(')

        expr = expr.replace('__ASIN_RAD__(', 'math.asin(')
        expr = expr.replace('__ACOS_RAD__(', 'math.acos(')
        expr = expr.replace('__ATAN_RAD__(', 'math.atan(')

        expr = expr.replace('__SIN__(', 'math.sin(math.radians(')
        expr = expr.replace('__COS__(', 'math.cos(math.radians(')
        expr = expr.replace('__TAN__(', 'math.tan(math.radians(')

        expr = expr.replace('__SIN_RAD__(', 'math.sin(')
        expr = expr.replace('__COS_RAD__(', 'math.cos(')
        expr = expr.replace('__TAN_RAD__(', 'math.tan(')

        open_count = expr.count('(')
        close_count = expr.count(')')
        if open_count > close_count:
            expr += ')' * (open_count - close_count)

        return expr

    def replace_function(self, expr, func_name, func):
        """Helper function - not used in current implementation"""
        return expr

calculator = CalculatorForm()
calculator.ShowDialog()
