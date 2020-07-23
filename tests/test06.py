# Standard imports
import os

# PyPI imports
import numpy as np
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat
from pylatex.utils import italic

# Set input and output paths
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_inputs')
data_dir_output = os.path.join(project_dir, 'mount')
image_filename = os.path.join(data_dir_input, 'thousand_degree_dog.jpg')


print('Started testing PyLaTex package.')

geometry_options = {"tmargin": "1cm", "lmargin": "3cm"}
doc = Document(geometry_options=geometry_options, default_filepath=data_dir_output)

with doc.create(Section('The simple stuff')):
    doc.append('Some regular text and some')
    doc.append(italic('italic text. '))
    doc.append('\nAlso some crazy characters: $&#{}')
    with doc.create(Subsection('Math that is incorrect')):
        doc.append(Math(data=['2*3', '=', 9]))

    with doc.create(Subsection('Table of something')):
        with doc.create(Tabular('rc|cl')) as table:
            table.add_hline()
            table.add_row((1, 2, 3, 4))
            table.add_hline(1, 2)
            table.add_empty_row()
            table.add_row((4, 5, 6, 7))

a = np.array([[100, 10, 20]]).T
M = np.matrix([[2, 3, 4],
               [0, 0, 1],
               [0, 0, 2]])

with doc.create(Section('The fancy stuff')):
    with doc.create(Subsection('Correct matrix equations')):
        doc.append(Math(data=[Matrix(M), Matrix(a), '=', Matrix(M * a)]))

    with doc.create(Subsection('Alignat math environment')):
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.append(r'\frac{a}{b} &= 0 \\')
            agn.extend([Matrix(M), Matrix(a), '&=', Matrix(M * a)])

    with doc.create(Subsection('Beautiful graphs')):
        with doc.create(TikZ()):
            plot_options = 'height=8cm, width=12cm, grid=major'
            with doc.create(Axis(options=plot_options)) as plot:
                plot.append(Plot(name='model', func='-x^5 - 242'))

                coordinates = [
                    (-4.77778, 2027.60977),
                    (-3.55556, 347.84069),
                    (-2.33333, 22.58953),
                    (-1.11111, -493.50066),
                    (0.11111, 46.66082),
                    (1.33333, -205.56286),
                    (2.55556, -341.40638),
                    (3.77778, -1169.24780),
                    (5.00000, -3269.56775),
                ]

                plot.append(Plot(name='estimate', coordinates=coordinates))

    with doc.create(Subsection('Thousand degree picture')):
        with doc.create(Figure(position='h!')) as kitten_pic:
            kitten_pic.add_image(image_filename, width='300px')
            kitten_pic.add_caption('This is the thousand degree big dog.')

outfile_name = 'report_test06'
doc.generate_pdf(os.path.join(data_dir_output, outfile_name), clean_tex=False)
print('Generated', os.path.join(data_dir_output, outfile_name) + '.pdf')

print('Finished testing PyLaTex package.')
