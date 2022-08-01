# - ************************************************************************
# -- WRITTEN AND OWNED BY OWOEYE, OLUWATOMILAYO INIOLUWA, APRIL, 2022.
# -- All rights (whichever they might be) reserved!
# **************************************************************************

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# THE GENERAL RENDERING OF DATA ON THE SCREEN OF THE GUI
# AND EXPORTING THE OUTPUT TO PDF

from fpdf import FPDF

# layout ('P', 'L')
# unit ('mm', 'cm', 'in')
# format ('A3', 'A4' (default), 'A5', 'Letter', 'Legal', custom (100,200))


# Create fpdf object
def generate_report(paper_size='Letter', orientation = "P", dimension='mm'):
    
    pdf = FPDF(orientation,dimension,paper_size)

    # Add a page
    pdf.add_page()

    # specify font
    # fonts ('times', 'courier', 'helvetica', 'symbol', 'zpfdingbats')
    # 'B' (bold), 'U' underline, 'I' italics, '' regular, combination (e.g. ('BU'))
    pdf.set_font('helvetica', '', 16)

    # Add text
    # width
    # height
    pdf.cell(40,10, 'Hello world!', ln=True)
    pdf.cell(80, 10, 'Goodbye world')

    pdf.output("Tt_pdf.pdf")




# print(topic_contents)
# print("_"*50)
# print(topic_contents["DEFINITION OF TERMS"])

