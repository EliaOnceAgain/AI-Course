import logic
from datetime import datetime

# #Original Code
# if __name__ == '__main__':
#     wumpus_kb = logic.PropKB()
#
#     P11, P12, P21, P22, P31, B11, B21 = logic.expr('P11, P12, P21, P22, P31, B11, B21')
#     wumpus_kb.tell(~P11)
#     wumpus_kb.tell(B11 | '<=>' | ((P12 | P21)))
#     wumpus_kb.tell(B21 | '<=>' | ((P11 | P22 | P31)))
#     wumpus_kb.tell(~B11)
#     wumpus_kb.tell(B21)
#
#     result = logic.dpll_satisfiable(logic.to_cnf(logic.associate('&', wumpus_kb.clauses + [logic.expr(P22, printme=True)])))
#     print(result)
#
#     result = logic.dpll_satisfiable(logic.to_cnf(logic.associate('&', wumpus_kb.clauses + [logic.expr(B11, printme=True)])))
#     print(result)

if __name__ == '__main__':
    wumpus_kb = logic.PropKB()

    P11, P12, P21, P22, P31, B11, B21 = logic.expr('P11, P12, P21, P22, P31, B11, B21')
    wumpus_kb.tell(~P11)
    wumpus_kb.tell(B11 | '<=>' | ((P12 | P21)))
    wumpus_kb.tell(B21 | '<=>' | ((P11 | P22 | P31)))
    wumpus_kb.tell(~B11)
    wumpus_kb.tell(B21)

    datetime_result = datetime.now()
    result = logic.dpll_satisfiable(
        logic.to_cnf(logic.associate('&', wumpus_kb.clauses + [logic.expr(P22, printme=True)])))
    datetime_result = datetime.now() - datetime_result

    print(result)
    print(datetime_result)
    print()

    datetime_result = datetime.now()
    result = logic.dpll_satisfiable(
        logic.to_cnf(logic.associate('&', wumpus_kb.clauses + [logic.expr(B11, printme=True)])))
    datetime_result = datetime.now() - datetime_result
    print(result)
    print(datetime_result)