# -*- coding: utf-8 -*-
"""Multiple Offset
Offset selected elements multiple times at once. Works with lines, walls, doors, windows, furniture, and more!
"""
__title__ = 'Multiple\nOffset'
__author__ = 'Phyo Pyae Zaw'

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import (
    Form, Button, TextBox, Label, RadioButton, GroupBox,
    FormStartPosition, FormBorderStyle, DialogResult
)
from System.Drawing import Point, Size, Color, Font, FontStyle

from pyrevit import revit, script, forms
from pyrevit import DB
from Autodesk.Revit.DB import Transaction, XYZ, ElementTransformUtils
from Autodesk.Revit.UI.Selection import ObjectType

doc = revit.doc
uidoc = revit.uidoc
output = script.get_output()
output.close_others()

class MultipleOffsetForm(Form):
    def __init__(self):
        self.Text = 'Multiple Offset - All Elements'
        self.Size = Size(380, 350)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.MaximizeBox = False
        self.MinimizeBox = False

        self.offset_distance = None
        self.offset_count = None
        self.offset_direction = 'X'  # 'X', 'Y', 'Z', 'Custom'
        self.custom_vector = None

        self.setup_ui()

    def setup_ui(self):
        title = Label()
        title.Text = 'Offset Selected Elements Multiple Times'
        title.Location = Point(10, 10)
        title.Size = Size(350, 20)
        title.Font = Font('Segoe UI', 10, FontStyle.Bold)
        self.Controls.Add(title)

        subtitle = Label()
        subtitle.Text = 'Works with lines, walls, doors, windows, furniture, etc.'
        subtitle.Location = Point(10, 30)
        subtitle.Size = Size(350, 15)
        subtitle.Font = Font('Segoe UI', 8)
        subtitle.ForeColor = Color.Gray
        self.Controls.Add(subtitle)

        dist_label = Label()
        dist_label.Text = 'Offset Distance:'
        dist_label.Location = Point(10, 60)
        dist_label.Size = Size(120, 20)
        dist_label.Font = Font('Segoe UI', 9)
        self.Controls.Add(dist_label)

        self.dist_input = TextBox()
        self.dist_input.Location = Point(140, 57)
        self.dist_input.Size = Size(120, 25)
        self.dist_input.Font = Font('Segoe UI', 10)
        self.dist_input.Text = '1000'  # Default 1000mm
        self.Controls.Add(self.dist_input)

        unit_label = Label()
        unit_label.Text = 'mm'
        unit_label.Location = Point(265, 60)
        unit_label.Size = Size(30, 20)
        unit_label.Font = Font('Segoe UI', 9)
        self.Controls.Add(unit_label)

        count_label = Label()
        count_label.Text = 'Number of Copies:'
        count_label.Location = Point(10, 90)
        count_label.Size = Size(120, 20)
        count_label.Font = Font('Segoe UI', 9)
        self.Controls.Add(count_label)

        self.count_input = TextBox()
        self.count_input.Location = Point(140, 87)
        self.count_input.Size = Size(120, 25)
        self.count_input.Font = Font('Segoe UI', 10)
        self.count_input.Text = '5'  # Default 5 copies
        self.Controls.Add(self.count_input)

        times_label = Label()
        times_label.Text = 'times'
        times_label.Location = Point(265, 90)
        times_label.Size = Size(40, 20)
        times_label.Font = Font('Segoe UI', 9)
        self.Controls.Add(times_label)

        dir_group = GroupBox()
        dir_group.Text = 'Offset Direction'
        dir_group.Location = Point(10, 125)
        dir_group.Size = Size(350, 110)
        dir_group.Font = Font('Segoe UI', 9, FontStyle.Bold)
        self.Controls.Add(dir_group)

        self.radio_x = RadioButton()
        self.radio_x.Text = 'X Direction (Left/Right)'
        self.radio_x.Location = Point(15, 25)
        self.radio_x.Size = Size(160, 20)
        self.radio_x.Font = Font('Segoe UI', 9)
        self.radio_x.Checked = True
        dir_group.Controls.Add(self.radio_x)

        self.radio_y = RadioButton()
        self.radio_y.Text = 'Y Direction (Up/Down)'
        self.radio_y.Location = Point(180, 25)
        self.radio_y.Size = Size(160, 20)
        self.radio_y.Font = Font('Segoe UI', 9)
        dir_group.Controls.Add(self.radio_y)

        self.radio_z = RadioButton()
        self.radio_z.Text = 'Z Direction (Vertical)'
        self.radio_z.Location = Point(15, 50)
        self.radio_z.Size = Size(160, 20)
        self.radio_z.Font = Font('Segoe UI', 9)
        dir_group.Controls.Add(self.radio_z)

        self.radio_custom = RadioButton()
        self.radio_custom.Text = 'Custom Vector (X, Y, Z):'
        self.radio_custom.Location = Point(15, 75)
        self.radio_custom.Size = Size(160, 20)
        self.radio_custom.Font = Font('Segoe UI', 9)
        dir_group.Controls.Add(self.radio_custom)

        self.vector_input = TextBox()
        self.vector_input.Location = Point(180, 73)
        self.vector_input.Size = Size(150, 25)
        self.vector_input.Font = Font('Segoe UI', 9)
        self.vector_input.Text = '1, 1, 0'
        self.vector_input.Enabled = False
        dir_group.Controls.Add(self.vector_input)

        self.radio_custom.CheckedChanged += self.custom_radio_changed

        ok_btn = Button()
        ok_btn.Text = 'Create Copies'
        ok_btn.Location = Point(100, 250)
        ok_btn.Size = Size(130, 40)
        ok_btn.Font = Font('Segoe UI', 10, FontStyle.Bold)
        ok_btn.BackColor = Color.FromArgb(135, 206, 250)
        ok_btn.Click += self.ok_clicked
        self.Controls.Add(ok_btn)

        cancel_btn = Button()
        cancel_btn.Text = 'Cancel'
        cancel_btn.Location = Point(240, 250)
        cancel_btn.Size = Size(100, 40)
        cancel_btn.Font = Font('Segoe UI', 10)
        cancel_btn.Click += self.cancel_clicked
        self.Controls.Add(cancel_btn)

    def custom_radio_changed(self, sender, event):
        self.vector_input.Enabled = self.radio_custom.Checked

    def ok_clicked(self, sender, event):
        try:
            self.offset_distance = float(self.dist_input.Text)
            self.offset_count = int(self.count_input.Text)

            if self.offset_distance == 0:
                forms.alert('Offset distance cannot be 0!', exitscript=False)
                return

            if self.offset_count <= 0:
                forms.alert('Number of copies must be greater than 0!', exitscript=False)
                return

            if self.radio_x.Checked:
                self.offset_direction = 'X'
            elif self.radio_y.Checked:
                self.offset_direction = 'Y'
            elif self.radio_z.Checked:
                self.offset_direction = 'Z'
            else:
                self.offset_direction = 'Custom'
                try:
                    vector_text = self.vector_input.Text.replace(' ', '')
                    parts = vector_text.split(',')
                    if len(parts) != 3:
                        forms.alert('Custom vector must have 3 values: X, Y, Z', exitscript=False)
                        return
                    self.custom_vector = (float(parts[0]), float(parts[1]), float(parts[2]))
                except:
                    forms.alert('Invalid custom vector format! Use: X, Y, Z', exitscript=False)
                    return

            self.DialogResult = DialogResult.OK
            self.Close()

        except ValueError:
            forms.alert('Please enter valid numbers!', exitscript=False)

    def cancel_clicked(self, sender, event):
        self.DialogResult = DialogResult.Cancel
        self.Close()

form = MultipleOffsetForm()
result = form.ShowDialog()

if result == DialogResult.OK:
    offset_distance_mm = form.offset_distance
    offset_count = form.offset_count
    offset_direction = form.offset_direction

    offset_distance_ft = offset_distance_mm / 304.8

    if offset_direction == 'X':
        offset_vector = XYZ(offset_distance_ft, 0, 0)
        direction_name = 'X Direction (Left/Right)'
    elif offset_direction == 'Y':
        offset_vector = XYZ(0, offset_distance_ft, 0)
        direction_name = 'Y Direction (Up/Down)'
    elif offset_direction == 'Z':
        offset_vector = XYZ(0, 0, offset_distance_ft)
        direction_name = 'Z Direction (Vertical)'
    else:
        custom = form.custom_vector
        length = (custom[0]**2 + custom[1]**2 + custom[2]**2) ** 0.5
        if length == 0:
            forms.alert('Custom vector cannot be (0, 0, 0)!', exitscript=True)
        offset_vector = XYZ(
            custom[0] / length * offset_distance_ft,
            custom[1] / length * offset_distance_ft,
            custom[2] / length * offset_distance_ft
        )
        direction_name = 'Custom Vector ({}, {}, {})'.format(custom[0], custom[1], custom[2])

    try:
        selection = uidoc.Selection
        selected_ids = selection.GetElementIds()

        if not selected_ids or selected_ids.Count == 0:
            forms.alert('Please select elements to offset!', exitscript=True)

        selected_id_list = list(selected_ids)

        t = Transaction(doc, 'Multiple Offset')
        t.Start()

        try:
            total_created = 0
            element_types = {}

            for i in range(1, offset_count + 1):
                current_offset = offset_vector * i

                new_ids = ElementTransformUtils.CopyElements(
                    doc,
                    selected_ids,  # Use the original ICollection, not a list
                    current_offset
                )

                total_created += new_ids.Count

                for new_id in new_ids:
                    elem = doc.GetElement(new_id)
                    elem_type = elem.GetType().Name
                    if elem_type in element_types:
                        element_types[elem_type] += 1
                    else:
                        element_types[elem_type] = 1

            t.Commit()

            output.print_md('# Multiple Offset Complete!')
            output.print_md('---')
            output.print_md('**Original elements selected:** {}'.format(selected_ids.Count))
            output.print_md('**Offset distance:** {} mm'.format(offset_distance_mm))
            output.print_md('**Number of copies:** {} times'.format(offset_count))
            output.print_md('**Offset direction:** {}'.format(direction_name))
            output.print_md('**New elements created:** {}'.format(total_created))
            output.print_md('---')
            output.print_md('## Elements Created by Type:')
            for elem_type, count in sorted(element_types.items()):
                output.print_md('- **{}:** {}'.format(elem_type, count))
            output.print_md('---')
            output.print_md('✓ **Total elements now:** {} (original) + {} (copies) = **{}**'.format(
                selected_ids.Count,
                total_created,
                selected_ids.Count + total_created
            ))

        except Exception as e:
            t.RollBack()
            forms.alert('Error creating copies: {}'.format(str(e)), exitscript=True)

    except Exception as e:
        forms.alert('Error: {}'.format(str(e)), exitscript=True)
