import sys
import os
from LogicPuzzle import LogicPuzzle
from RuleParser import InvalidTokenException, UnexpectedTokenException, MissingTokenException

from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)
from PyQt5.uic import loadUi

from GUI.Solver import Ui_MainWindow

class Window(Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        loadUi("GUI/Solver.ui", self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.solve_button.clicked.connect(self.solve)
        self.clear_button.clicked.connect(self.clear)
        self.reset_button.clicked.connect(self.reset)
    
    def solve(self):
        cat_f_name = os.path.join("GUI","categories.txt")
        rule_f_name = os.path.join("GUI","rules.txt")
        with open( cat_f_name, 'w' ) as f:
            f.write( self.category_text.toPlainText() )
        with open( rule_f_name, 'w' ) as f:
            f.write( self.rule_text.toPlainText() )

        # TODO : Put this in a try and output error results

        try:
            puzzle = LogicPuzzle(cat_f_name, rule_f_name)
            os.remove(cat_f_name)
            os.remove(rule_f_name)
            solved, loops, grid = puzzle.solve(True, False, True)

            self.result_text.setText( grid.get_string() )
            msg = "Ran {} loops\n".format(loops)
            if solved:
                msg += "Solved!"
            else:
                msg += "Could not fully solve..."
            
            if puzzle.contains_empty_sets():
                msg += "\nEmpty sets in puzzle. Double-check rules"

            self.output_text.setPlainText(msg)
        except InvalidTokenException as e:
            self.output_text.setPlainText( "Invalid Token\n{}".format( str(e) ) )
        except UnexpectedTokenException as e:
            self.output_text.setPlainText( "Unexpected Token\n{}".format( str(e) ) )
        except MissingTokenException as e:
            self.output_text.setPlainText( "Missing Token\n{}".format( str(e) ) )
        except Exception as e:
            self.output_text.setPlainText( "Unexpected Error\n{}".format( str(e) ) )
        
        self.write(puzzle)
        
    def clear(self):
        self.output_text.setPlainText("")

    def reset(self):
        self.clear()
        self.result_text.setPlainText("")
        self.rule_text.setPlainText("")
        self.category_text.setPlainText("")

    def write(self, puzzle):
        f = open("temp.txt","w")
        for key in puzzle.full_sets:
            f.write(str(key))
            f.write(" -> ")
            f.write(str(puzzle.full_sets[key]))
            f.write("\n")
        f.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())