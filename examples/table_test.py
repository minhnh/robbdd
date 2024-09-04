from textx import metamodel_from_str

# Define the corrected grammar
grammar = '''
Model: rows+=Row;
Row: WS* '|' WS* cells+=Cell WS* '|' (WS* '|' WS* cells+=Cell WS* '|' )*;
Cell: '<' cell_content=ID '.' cell_name=ID '>';
WS: /\s*/;
'''

# Create the metamodel from the grammar
meta_model = metamodel_from_str(grammar)

# The table-like text structure
text = '''
| <tmpl_pickplace.var_target_object> | <tmpl_pickplace.var_pick_ws> | <tmpl_pickplace.var_place_ws> | <tmpl_pickplace.var_robot> |
| <lab_scene.box> | <lab_scene.dining_table> | <lab_scene.shelf> | <lab_scene.freddy> |
| <lab_scene.ball> | <lab_scene.shelf> | <lab_scene.dining_table> | <lab_scene.lucy> |
| <lab_scene.bottle> | <lab_scene.dining_table> | <lab_scene.shelf> | <lab_scene.freddy> |
'''

# Parse the text
model = meta_model.model_from_str(text)

# Access and print the parsed data
for row in model.rows:
    row_data = []
    for cell in row.cells:
        row_data.append(f"{cell.cell_content}.{cell.cell_name}")
    print(row_data)
