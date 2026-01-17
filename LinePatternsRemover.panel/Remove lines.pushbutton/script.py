# -*- coding: utf-8 -*-
"""Batch Delete Line Patterns
Select and delete multiple line patterns at once, including arc line patterns.
"""
__title__ = 'Delete Line\nPatterns'
__author__ = 'Phyo Pyae Zaw'

from pyrevit import revit, script, forms
from pyrevit import DB

doc = revit.doc
output = script.get_output()
output.close_others()

# Collect all line pattern elements
line_patterns = (
    DB.FilteredElementCollector(doc)
    .OfClass(DB.LinePatternElement)
    .ToElements()
)

if not line_patterns:
    output.print_md('# No Line Patterns Found')
    output.print_md('No line patterns found in the project.')
else:
    # Create dictionary of line patterns
    pattern_dict = {}
    for pattern in line_patterns:
        pattern_name = pattern.Name
        pattern_dict[pattern.Id.IntegerValue] = pattern_name
    
    # Sort patterns alphabetically
    sorted_patterns = sorted(pattern_dict.items(), key=lambda x: x[1])
    pattern_names = [name for pat_id, name in sorted_patterns]
    
    # Show selection dialog
    selected_patterns = forms.SelectFromList.show(
        pattern_names,
        title='Select Line Patterns to Delete',
        width=500,
        height=600,
        button_name='Delete Selected',
        multiselect=True
    )
    
    if selected_patterns:
        # Get IDs of selected patterns
        selected_ids = []
        for pat_id, pat_name in sorted_patterns:
            if pat_name in selected_patterns:
                selected_ids.append(DB.ElementId(pat_id))
        
        # Confirm deletion
        result = forms.alert(
            'Delete {} line pattern(s)?'.format(len(selected_patterns)),
            title='Confirm Deletion',
            yes=True,
            no=True
        )
        
        if result:
            # Start transaction
            t = DB.Transaction(doc, 'Delete Line Patterns')
            t.Start()
            
            try:
                deleted = []
                failed = []
                
                for pattern_id in selected_ids:
                    try:
                        pattern = doc.GetElement(pattern_id)
                        pattern_name = pattern.Name
                        doc.Delete(pattern_id)
                        deleted.append(pattern_name)
                    except Exception as e:
                        failed.append((pattern_name, str(e)))
                
                t.Commit()
                
                output.print_md('# Deletion Complete!')
                output.print_md('---')
                
                if deleted:
                    output.print_md('## Successfully Deleted ({})'.format(len(deleted)))
                    for name in deleted:
                        output.print_md('- ✓ {}'.format(name))
                
                if failed:
                    output.print_md('---')
                    output.print_md('## Failed to Delete ({})'.format(len(failed)))
                    output.print_md('*These patterns may be in use or system-protected*')
                    output.print_md('')
                    for name, error in failed:
                        output.print_md('- ✗ **{}**'.format(name))
                        output.print_md('  *Error: {}*'.format(error))
                
                output.print_md('---')
                output.print_md('**Total selected:** {}'.format(len(selected_patterns)))
                output.print_md('**Successfully deleted:** {}'.format(len(deleted)))
                output.print_md('**Failed:** {}'.format(len(failed)))
                
            except Exception as e:
                t.RollBack()
                output.print_md('# Error')
                output.print_md('Transaction failed: {}'.format(str(e)))
        else:
            output.print_md('# Cancelled')
            output.print_md('Deletion cancelled by user.')
    else:
        output.print_md('# Cancelled')
        output.print_md('No line patterns selected.')