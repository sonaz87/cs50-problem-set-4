import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

# written by me

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()     
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
            
        to_remove = []    
        for i in self.domains:
            for element in self.domains[i]:
                if len(element) != i.length:
                    to_remove.append([i, element])
                    
        for element in to_remove:
            self.domains[element[0]].remove(element[1])

            
            
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

    
        # find the point of connection:
        crossing_point = tuple()
        revised = False
        if x.direction == 'across':
            for x_pos in range(x.length):
                for y_pos in range(y.length):

                    if (x.i, x.j + x_pos) == (y.i + y_pos, y.j):
                        crossing_point = (x_pos, y_pos)                
        else:
            for x_pos in range(x.length):
                for y_pos in range(y.length):
                    if (x.i + x_pos, x.j) == (y.i, y.j + y_pos):
                        crossing_point = (x_pos, y_pos)
        for x_word in self.domains[x]:
            words_to_remove = []
            to_be_removed = True
            for y_word in self.domains[y]:
                if x_word[crossing_point[0]] == y_word[crossing_point[1]]:
                    to_be_removed = False
            if to_be_removed == True:
                words_to_remove.append(x_word)
                
        for word in words_to_remove:
            self.domains[x].remove(word)
            revised = True
        

        return revised




    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = list()
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    if (x, y) not in arcs:
                        arcs.append((x,y))
        
        for i in arcs:     
            if self.revise(i[0], i[1]) == True:
                for x in self.crossword.neighbors(i[0]):
                    arcs.append((x, i[0]))
        
        for i in self.domains:
            if len(self.domains[i]) == 0:
                return False
            
        return True
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """


        if len(assignment) == len(self.domains):
            for i in assignment:
                for j in assignment:
                    if i == j:
                        continue
                    if assignment[i] == assignment[j]:
                        return False
            return True        
        else:
            return False

        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        cons = True
        if len(assignment) < 2:
            return True
        
        for var1 in assignment:
            if type(assignment[var1]) == list and len(assignment[var1]) != 1:
                cons = False
                break
            for var2 in assignment:  
                if var1 == var2:
                    continue
                else:
                    if assignment[var1] == assignment[var2]:
                        cons = False
                        break
                    if var2 in self.crossword.neighbors(var1):
                        if var1.direction == 'across':
                            for x_pos in range(var1.length):
                                for y_pos in range(var2.length):
                
                                    if (var1.i, var1.j + x_pos) == (var2.i + y_pos, var2.j):
                                        crossing_point = (x_pos, y_pos)                
                        else:
                            for x_pos in range(var1.length):
                                for y_pos in range(var2.length):
                                    if (var1.i + x_pos, var1.j) == (var2.i, var2.j + y_pos):
                                        crossing_point = (x_pos, y_pos)

                        if assignment[var1][crossing_point[0]] != assignment[var2][crossing_point[1]]:                        
                            cons = False

        return cons
                        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        result = []
        

        for word1 in assignment[var]:
            counter = 0
            for neighbor in self.crossword.neighbors(var):
            
                # find crossing point for words
                if var.direction == 'across':
                    for x_pos in range(var.length):
                        for y_pos in range(neighbor.length):
        
                            if (var.i, var.j + x_pos) == (neighbor.i + y_pos, neighbor.j):
                                crossing_point = (x_pos, y_pos)                
                else:
                    for x_pos in range(var.length):
                        for y_pos in range(neighbor.length):
                            if (var.i + x_pos, var.j) == (neighbor.i, neighbor.j + y_pos):
                                crossing_point = (x_pos, y_pos)
               
                # if neighbor word is not valid, add 1 to counter
                for word2 in assignment[neighbor]:
                    try:
                        if word1[crossing_point[0]] != word2[crossing_point[1]]:
                            counter += 1
                    except IndexError:
                        continue
                
            # append word and counter to result
            result.append([word1, counter])
            
        # sort result by counter, low, to high
        result.sort(key=lambda x: x[1])


        # create new list with words only        
        answer = []
        for i in result:
            answer.append(i[0])
        return answer
        


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        count = 1000000000000000000
        result = None
        for i in self.domains:
            if i not in assignment:
                if len(self.domains[i]) < count:    
                    result = i
                    count = len(self.domains[i])
                    
                if len(self.domains[i]) == count:
                    if len(self.crossword.neighbors(i)) > len(self.crossword.neighbors(result)):
                        result = i

        return result


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, self.domains):
            new_var = {var : value}
            assignment.update(new_var)
            if self.consistent(assignment):
        
                 for i in self.crossword.neighbors(var) :
                     self.revise(i, var)
                 result = self.backtrack(assignment)
                 if result != False:
                     return result
                 del assignment[var]
            else:
                 del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


from time import time
start = time()

if __name__ == "__main__":
    main()

print("run time: ", time() - start)