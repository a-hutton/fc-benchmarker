import nbformat
import pandoc


def read_notebook(filename: str):
    with open(filename) as f:
        return nbformat.read(f, nbformat.NO_CONVERT)


def convert_file(filename: str):
    nb = read_notebook(filename)
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            md_to_latex(cell.source)
        elif cell.cell_type == "code":
            print(code_snippet_to_latex(cell.source, cell.outputs))
            pass
        else:
            print(f"Skipping unknown cell type '{cell.cell_type}'")


def code_snippet_to_latex(src: str, output: str, collapsed=True):
    return f"""
\\begin{{minted}}{{python}}
{src}
\\end{{minted}}{{python}}
"""


def md_to_latex(src: str):
    doc = pandoc.read(src)
    return pandoc.write(doc, format="latex", options=[])


convert_file("./Report.ipynb")
