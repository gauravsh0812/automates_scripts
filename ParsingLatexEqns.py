 # -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 23:02:49 2020
@author: gauravs
Latex eqns Parsing code
NOTE: Please change the paths as per your system before running the code.
"""

import pandas as pd
import json, os
from subprocess import call
import subprocess
##########################################################################################################################################
# Parsing latex equations
##########################################################################################################################################

# to find inline equations i.e. $(...)$
def inline(length, line):
    pos = [pos for pos, char in enumerate(line) if char == "$"]
    #print(pos, length)
    if length%2 == 0:
        i = 0
        if length > 2:
            while i < length:
                #print(i)
                inline_equation = line[pos[i]+1 : pos[i+1]]
                i = i+2
                return(inline_equation)

        else:
            inline_equation = line[pos[i]+1 : pos[i+1]]
            return(inline_equation)

# to find \[---\] equations
def bracket_equation(line):
    pos_begin = [pos for pos, char in enumerate(line) if char == "\\["]
    pos_end = [pos for pos, char in enumerate(line) if char == "\\]"]

    for i, j in zip(pos_begin, pos_end):
        equation = line[i+1 : j]

        return(equation)

# to find \(---\) equations
def parenthesis_equation(line):
    pos_begin = [pos for pos, char in enumerate(line) if char == "\\("]
    pos_end = [pos for pos, char in enumerate(line) if char == "\\)"]

    for i, j in zip(pos_begin, pos_end):
        parenthesis= line[i+1 : j]

        return(parenthesis)

# dealing with Macros
def Macros(line):    
    # checking the brackets
    open_curly_brac = [char for char in line if char == "{"]
    close_curly_brac = [char for char in line if char == "}"]
    if len(open_curly_brac)!= len(close_curly_brac):
        delta = len(open_curly_brac) - len(close_curly_brac)
        #print(line)
        #print(delta)
        # if delta is positive --> need to close the brac
        if delta>0:
            for i in range(delta):
                line +="}"
        if delta < 0:
            for i in range(abs(delta)):
                line=line[:line.find(max(close_curly_brac))]
        #print(line.replace(" ", ""))

    try:
        # dealing with parameters assiging problem
        hash_flag = False
        line=line.replace(" ", "")
        var = [int(line[p+1]) for p, c in enumerate(line) if c == "#"]
        if len(var) !=0:
           # print(line)
            if line[line.find("}")+1] != "[" and line[line.find("}")+3] != "]":
                #print(line)
                hash_flag = True
                max_var = max(var)
                #print(max_var)
                temp = ""
                temp += line[:line.find("}")+1] + "[" + max_var + "]"+ line[line.find("}")+1:]
        if hash_flag:
            return temp
        else:
            return line
    except:
        pass

# cleaning eqn - part 1 --> removing label, text, intertext
def Clean_eqn_1(eqn_1):

    keywords_tobeCleaned = ["\\label", "\\text", "\\intertext"]
    for KC in keywords_tobeCleaned:
        try:
            if KC in eqn_1:
                p = 0
                while p == 0:
                    b = eqn_1.find(KC)
                    count = 1
                    k = 5
                    while count != 0:
                        if eqn_1[b+k] == "}":
                            count = 0 
                        else: 
                            k+=1
                    eqn_1 = eqn_1.replace(eqn_1[b:b+k+1], '')
                    if KC not in eqn_1:
                        p = 1
        except:
            pass
        
    return eqn_1 

#removing non-essential commands
def Clean_eqn_2(eqn_2):
    to_replace = ["\n", "%", "\r", "\\bm", "&&"]
    for char in to_replace:
        if char in eqn_2:
            try:
                eqn_2 = eqn_2.replace(char, '')
            #except:
                # see if eqn_2 is a tuple
             #   eqn_2 = ' '.join(str(x) for x in eqn_2 if x != char)
            except:
                pass
                #print("some problem with equation")

    # we don't want "&" in the equation as such untill unless it is a matrix
    if "&" in eqn_2:
        indicator_bmc = False
        for mc in matrix_cmds:
            bmc = "\\begin{}".format(mc)
            #print(bmc)
            emc = "\\end{}".format(mc) 
            #print(emc)

            if bmc in eqn_2:
                indicator_bmc = True
                bmc_index = eqn_2.find(bmc)
                emc_index = eqn_2.find(emc)
                len_mc = len(mc)

                #print([bmc_index, emc_index, len_mc])


            # position of "&" in equation
                list_of_and_symbol = [index_ for index_ ,char in enumerate(eqn_2) if char == "&"]     
                #print(list_of_and_symbol)
            # index of the code in between bmc_index to emc_index 
            # don't need to remove "&" from this part eqn
                index_nochange = list(range(bmc_index+ 6+ len_mc+ 1, emc_index))
                #print(index_nochange)

            # anywhere except index_nochange --> replace the "&" with ''   
                eqn_2_array = eqn_2.split("&")
                temp = ""
                for l in range(len(list_of_and_symbol)):
                    if list_of_and_symbol[l] in index_nochange:
                        temp += eqn_2_array[l] +  eqn_2_array[l+1]
                    else:
                        temp += eqn_2_array[l] + "&"+ eqn_2_array[l+1]
                eqn_2 = temp

        if not indicator_bmc:
            eqn_2=eqn_2.replace('&', '')

    return eqn_2

# creating a table having the mathml_output, latex code
latexCode_arr = []
mathml_output_arr = []
def DataSet(mathml_output, latex_code):
    mathml_output_arr.append(mathml_output)
    latexCode_arr.append(latex_code)

def List_to_Str(eqn, encoding):
    if type(eqn) is not list:
        #print(type(eqn))
        return list
    else:
        # initialize an empty string
        s = ""
        for ele in eqn:
            ele = ele.decode(encoding, errors = "ignore")#("utf-8")
            s += ele
        return s

def Cleaning_writing_eqns(total_equations, encoding):
    eq=[]
    for e in total_equations:
        if type(e) is list:
            eq.append(List_to_Str(e, encoding))
        else:
            eq.append(e)
    #print(eq)      
    for i in range(len(eq)):    
        # removing unnecc stuff - label, text, intertext
        par_clean_eq = Clean_eqn_1(eq[i])
        cleaned_eq = Clean_eqn_2(par_clean_eq)

        # sending the output to the dictionaries
        if cleaned_eq not in src_latex:
            src_latex.append(cleaned_eq) 
            with open('/home/gauravs/Automates/results_file/latex_equations/{}/eqn{}_latex_equations.txt'.format(tex_folder, i), 'w') as file:
                file.write(cleaned_eq)
                file.close()
    return(len(src_latex))
    
def main(matrix_cmds, equation_cmds, unknown_iconv, relational_operators, greek_letters):
    # looping through the latex paper directories
    dir_path = '/home/gauravs/Automates/LaTeX_src/single_tex_1401'
    for tex_folder in os.listdir(dir_path):

        tex_folder_path = os.path.join(dir_path, tex_folder)
        os.chdir(tex_folder_path)
        tex_file = [file for file in os.listdir(tex_folder_path)]
        Tex_doc = os.path.join(tex_folder_path, tex_file[0])

        # Finding the type of encoding i.e. utf-8, ISO8859-1, ASCII, etc.   
        encoding = subprocess.check_output(["file", "-i",Tex_doc ]).decode("utf-8").split()[2].split("=")[1]
        #print(encoding)

        unknown_encoding_tex = []
        if encoding not in unknown_iconv:
            file = open(Tex_doc, 'rb')
            lines = file.readlines()

            # initializing the arrays and variables
            src_latex=[]
            #macro_dict = {}
            total_macros = []
            declare_math_operator = []
            total_equations = []
            alpha = 0
            matrix = 0
            dollar = 1
            brac = 1
            Total_Parsed_Eqn = 0

            # creating the paper folder
            paper_dir = '/home/gauravs/Automates/results_file/latex_equations/{}'.format(tex_folder)
            if not os.path.exists(paper_dir):
                call(['mkdir', paper_dir])

            # opening files to write Macros and declare math operator
            MacroFile = open('/home/gauravs/Automates/results_file/latex_equations/{}/Macros_paper.txt'.format(tex_folder), 'w') 
            DMOFile = open('/home/gauravs/Automates/results_file/latex_equations/{}/DeclareMathOperator_paper.txt'.format(tex_folder), 'w') 

            # since lines are in bytes, we need to convert them into str    
            for index, l in enumerate(lines):
                line = l.decode(encoding, errors = 'ignore')

                # extracting MACROS
                if "\\newcommand" in line or "\\renewcommand" in line:
                    L = Macro(line)
                    #var = line[line.find("{")+1 : line.find("}")]
                    #macro_dict[var] = line[line.find("}")+1 : ]
                    MacroFile.write(L)             

                # extract declare math operator
                if "\\DeclareMathOperator" in line:
                    DMOFile.write(line)

                # condition 1.a: if $(....)$ is present
                # condition 1.b: if $$(....)$$ is present --> replace it with $(---)$
                if "$" in line or "$$" in line and alpha == 0:
                    if "$$" in line:
                        line = line.replace("$$", "$")

                    #array of the positions of the "$"
                    length = len([c for c in line if c=="$"])   

                    #length of the above array -- no. of the "$",  if even -- entire equation is in one line. If odd -- equation is going to next line
                    #if instead of $....$, $.... is present, and upto next 5 lines, no closing "$" can be found, then that condition will be rejected.
                    if length % 2 == 0:                          
                        inline_equation = inline(length, line)

                    else:
                        # combine the lines
                        try:
                            dol = 1
                            dol_indicator = False
                            while dol<6: #dollar != 0:
                                line = line + lines[index + dol].decode(encoding, errors = "ignore") 
                                if "$$" in line:
                                    line = line.replace("$$", "$") 

                                length = len([c for c in line if c=="$"])
                                if length%2 != 0:
                                    dol+=1
                                else: 
                                    dol = 6
                                    dol_indicator = True

                            if dol_indicator:
                                inline_equation = inline(length, line)
                                #print("$ : {}".format(index))
                            else:
                                inline_equation = None
                        except:
                             inline_equation = None

                    #check before appending if it is a valid equation
                    if inline_equation is not None:
                        r=[sym for sym in relational_operators if (sym in inline_equation)]
                        if bool(r):# == True:
                            total_equations.append(inline_equation)


                # condition 2: if \[....\] is present
                if "\\[" in line and alpha == 0:
                    length_begin = len([c for c in line if c=="\\["])
                    length_end = len([c for c in line if c=="\\]"])

                    if length_begin == length_end:
                            Bequations = bracket_equation(line)
                    elif length_begin > length_end:
                        # combine the lines 
                        br = 1
                        while brac != 0:
                            line = line + lines[index + br].decode(encoding, errors = "ignore")
                            length_begin = len([c for c in line if c=="\\["])
                            length_end = len([c for c in line if c=="\\]"])
                            if length_begin == length_end:
                                Bequations = bracket_equation(line)

                                #print(Bequations)
                            else:
                                br+=1
                    #check before appending if it is a valid equation
                    if Bequations is not None:
                        r=[sym for sym in relational_operators if (sym in Bequations)]
                        if bool(r):# == True:
                            total_equations.append(Bequations) 


                # condition 3: if \(....\) is present
                if "\\(" in line and alpha == 0:
                    length_begin = len([c for c in line if c=="\\("])
                    length_end = len([c for c in line if c=="\\)"])
                    if length_begin == length_end:
                            Pequations = parenthesis_equation(line)
                    elif length_begin > length_end:
                        # combine the lines 
                        br = 1
                        while brac != 0:
                            line = line + lines[index + br].decode(encoding, errors = "ignore")
                            length_begin = len([c for c in line if c=="\\("])
                            length_end = len([c for c in line if c=="\\)"])
                            if length_begin == length_end:
                                Pequations = parenthesis_equation(line)
                                #print("\\[] : {}".format(index))
                                #print(equations)
                            else:
                                br+=1
                    #check before appending if it is a valid equation
                    if Pequations is not None:
                        r=[sym for sym in relational_operators if (sym in Pequations)]
                        if bool(r):# == True:
                            total_equations.append(Pequations) 

                # condition 4: if \begin{equation(*)} \begin{case or split} --- \end{equation(*)} \begin{case or split}
                # comdition 5: if \begin{equation(*)} --- \end{equation(*)}
                for ec in equation_cmds:
                    if "\\begin{}".format(ec) in line: #or "\\begin{equation*}" in line or "\\begin{align}" in line or "\\begin{align*}" in line or "\\begin{eqnarray}" in line or "\\begin{eqnarray*}" in line or "\\begin{displaymath}" in line:
                        begin_index_alpha = index+1
                        alpha = 1 
                        #print("\\begin eqtn : {}".format(index))

                for ec in equation_cmds:
                    if "\\end{}".format(ec) in line and alpha == 1 : # or "\\end{equation*}" in line or "\\end{align}" in line or "\\end{align*}" in line or "\\end{eqnarray}" in line or "\\end{eqnarray*}" in line or "\\end{displaymath}" in line :
                        end_index_alpha = index
                        alpha =0
                        #print("\\endeqtn : {}".format(index))

                        equation = lines[begin_index_alpha : end_index_alpha]
                        eqn = ''
                        for i in range(len(equation)):
                            eqn = eqn + equation[i].decode(encoding, errors = "ignore")
                        total_equations.append(eqn)

                # condition 6: if '\\begin{..matrix(*)}' but independent under condition 4
                for mc in matrix_cmds:
                    if "\\begin{}".format(mc) in line and alpha == 0:
                        matrix = 1
                        begin_matrix_index = index
                        #print("\\begin mat : {}".format(index))

                    if "\\end{}".format(mc) in line and matrix == 1:
                        end_matrix_index = index
                        matrix =0
                        #print("\\end mat : {}".format(index))

                        # append the array with the recet equation along with the \\begin{} and \\end{} statements
                        equation = lines[begin_matrix_index : end_matrix_index+1]
                        total_equations.append(equation)

            MacroFile.close()
            DMOFile.close()
            #print(total_equations)
            src_latex_length = Cleaning_writing_eqn(total_equations, encoding, tex_folder)

            # Total number eqn parsed 
            Total_Parsed_Eqn += src_latex_length
        
        # if tex has unknown encoding or which can not be converted to some known encoding
        else:
            unknown_encoding_tex.append(tex_folder)
    
    return(Total_Parsed_Eqn, unknown_encoding_tex)

if __name__ == "__main__":
    # possible matrix and equation keyword that can be used in LaTeX source codes
    matrix_cmds   = ['{matrix}', '{matrix*}', '{bmatrix}', '{bmatrix*}', '{Bmatrix}', '{Bmatrix*}', '{vmatrix}', '{vmatrix*}', '{Vmatrix}', '{Vmatrix*}']
    equation_cmds = ['{equation}', '{equation*}', '{align}', '{align*}', '{eqnarray}', '{eqnarray*}', '{displaymath}']
    
    # unknown encoding type
    unknown_iconv = ["unknown-8bit", "binary"]

    # get symbols, greek letter, and encoding list 
    excel_file = '/home/gauravs/Automates/automates_scripts/Latex_symbols.xlsx'
    df = pd.read_excel(excel_file, 'rel_optr')
    relational_operators = df.iloc[:, 1].values.tolist()
    df_greek = pd.read_excel(excel_file, 'greek')
    greek_letters = df_greek.iloc[:, 0].values.tolist()
    
    Total_Parsed_Eqn, unknown_encoding_tex = main(matrix_cmds, equation_cmds, unknown_iconv, relational_operators, greek_letters)
    print("Total number equations succesfully parsed --> %d" %Total_Parsed_Eqn) 
    print("Files with unknown encoding are: ")
    for i in unknown_encoding_tex:
        print(i)