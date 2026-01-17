# -*- coding: utf-8 -*-
"""Reset View Overrides by Category
Resets graphic overrides (VV/VG) for selected categories in the active view,
including coarse scale fill colors.
"""
__title__ = 'Reset\nOverrides'
__author__ = 'Phyo Pyae Zaw'

from pyrevit import revit, script, forms
from pyrevit import DB

doc = revit.doc
uidoc = revit.uidoc
output = script.get_output()
output.close_others()

# Get active view
active_view = doc.ActiveView

# Check if view supports overrides
if not hasattr(active_view, 'SetElementOverrides'):
    output.print_md('# Cannot Reset Overrides')
    output.print_md('The active view type does not support graphic overrides.')
else:
    # Collect all elements in view to find which categories exist
    all_elements = (
        DB.FilteredElementCollector(doc, active_view.Id)
        .WhereElementIsNotElementType()
        .ToElements()
    )

    # Get unique categories present in the view
    categories_in_view = {}
    for element in all_elements:
        try:
            cat = element.Category
            if cat and cat.Name:
                if cat.Id.IntegerValue not in categories_in_view:
                    categories_in_view[cat.Id.IntegerValue] = cat.Name
        except:
            continue

    # Sort categories alphabetically
    sorted_categories = sorted(categories_in_view.items(), key=lambda x: x[1])

    if not sorted_categories:
        output.print_md('# No Categories Found')
        output.print_md('No elements with categories found in the current view.')
    else:
        # Add "All Categories" option at the beginning
        category_options = ['** All Categories **'] + [cat_name for cat_id, cat_name in sorted_categories]

        # Show selection dialog
        selected_categories = forms.SelectFromList.show(
            category_options,
            title='Select Categories to Reset',
            width=500,
            height=600,
            button_name='Reset Selected',
            multiselect=True
        )

        if selected_categories:
            # Start transaction
            t = DB.Transaction(doc, 'Reset Category Overrides')
            t.Start()

            try:
                element_count = 0
                category_count = 0
                filter_count = 0

                # Create default override settings (empty)
                default_override = DB.OverrideGraphicSettings()

                # Check if "All Categories" was selected
                reset_all = '** All Categories **' in selected_categories

                if reset_all:
                    # Reset all elements
                    for element in all_elements:
                        try:
                            current_override = active_view.GetElementOverrides(element.Id)
                            if not current_override.Equals(default_override):
                                active_view.SetElementOverrides(element.Id, default_override)
                                element_count += 1
                        except:
                            continue

                    # Reset all category overrides
                    for cat in doc.Settings.Categories:
                        try:
                            cat_override = active_view.GetCategoryOverrides(cat.Id)
                            if not cat_override.Equals(default_override):
                                active_view.SetCategoryOverrides(cat.Id, default_override)
                                category_count += 1
                        except:
                            continue

                    # Remove all filters
                    filters = active_view.GetFilters()
                    filter_count = len(filters)
                    for filter_id in filters:
                        try:
                            active_view.RemoveFilter(filter_id)
                        except:
                            continue

                else:
                    # Get selected category IDs
                    selected_cat_ids = []
                    for cat_id, cat_name in sorted_categories:
                        if cat_name in selected_categories:
                            selected_cat_ids.append(cat_id)

                    # Reset only elements in selected categories
                    for element in all_elements:
                        try:
                            cat = element.Category
                            if cat and cat.Id.IntegerValue in selected_cat_ids:
                                current_override = active_view.GetElementOverrides(element.Id)
                                if not current_override.Equals(default_override):
                                    active_view.SetElementOverrides(element.Id, default_override)
                                    element_count += 1
                        except:
                            continue

                    # Reset category-level overrides for selected categories
                    for cat_id in selected_cat_ids:
                        try:
                            db_cat_id = DB.ElementId(cat_id)
                            cat_override = active_view.GetCategoryOverrides(db_cat_id)
                            if not cat_override.Equals(default_override):
                                active_view.SetCategoryOverrides(db_cat_id, default_override)
                                category_count += 1
                        except:
                            continue

                t.Commit()

                output.print_md('# Reset Complete!')
                output.print_md('**View:** {}'.format(active_view.Name))
                output.print_md('---')

                if reset_all:
                    output.print_md('**Reset Mode:** All Categories')
                else:
                    output.print_md('**Reset Mode:** Selected Categories')
                    output.print_md('**Categories:** {}'.format(', '.join(selected_categories)))

                output.print_md('---')
                output.print_md('- **Element overrides reset:** {}'.format(element_count))
                output.print_md('- **Category overrides reset:** {}'.format(category_count))
                output.print_md('  *(includes coarse scale fill colors)*')

                if reset_all:
                    output.print_md('- **View filters removed:** {}'.format(filter_count))

                output.print_md('---')
                output.print_md('**Cleared overrides include:**')
                output.print_md('- Line colors and weights')
                output.print_md('- Surface patterns and fill colors')
                output.print_md('- Coarse scale fill colors')
                output.print_md('- Transparency settings')

            except Exception as e:
                t.RollBack()
                output.print_md('# Error')
                output.print_md('Failed to reset overrides: {}'.format(str(e)))
        else:
            output.print_md('# Cancelled')
            output.print_md('No categories selected.')
