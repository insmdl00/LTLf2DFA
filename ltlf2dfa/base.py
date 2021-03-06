# -*- coding: utf-8 -*-

"""Base classes for the implementation of a generic syntax tree."""

from abc import abstractmethod, ABC
from typing import Sequence, Set, Tuple, TypeVar, Generic, cast, Union, Optional, Any
import re

from ltlf2dfa.symbols import Symbols, OpSymbol
from ltlf2dfa.helpers import Hashable, Wrapper

AtomSymbol = Union["QuotedFormula", str]


class Formula(Hashable, ABC):
    """Abstract class for a formula."""

    @abstractmethod
    def find_labels(self) -> Set[AtomSymbol]:
        """Return the set of symbols."""

    def to_nnf(self) -> "Formula":
        """Transform the formula in NNF."""
        return self

    @abstractmethod
    def negate(self) -> "Formula":
        """Negate the formula. Used by 'to_nnf'."""

    @abstractmethod
    def to_mona(self, v: Optional[Any] = None) -> str:
        """Transform the formula in MONA."""


class AtomicFormula(Formula, ABC):
    """An abstract atomic formula.

    Both formulas and names can be used as atomic symbols.
    A name must be a string made of letters, numbers, underscores, or it must
    be a quoted string.
    """

    name_regex = re.compile(r'(\w+)|(".*")')

    def __init__(self, s: Union[AtomSymbol, Formula]):
        """Inintializes the atomic formula.

        :param s: the atomic symbol. Formulas are implicitly converted to
            quoted formulas.
        """
        super().__init__()

        # If formula
        if isinstance(s, Formula):
            self.s = QuotedFormula(s)  # type: AtomSymbol

        # If name
        else:
            self.s = str(s)
            if not self.name_regex.fullmatch(self.s):
                raise ValueError(
                    "The symbol name does not respect the naming convention."
                )

    def _members(self):
        return self.s

    def __str__(self):
        """Get the string representation."""
        return str(self.s)

    def find_labels(self) -> Set[AtomSymbol]:
        """Return the set of symbols."""
        return {self.s}


class QuotedFormula(Wrapper):
    """This object is a constant representation of a formula.

    This can be used as a normal formula. Quoted formulas can also be used as
    hashable objects and for atomic symbols.
    """

    def __init__(self, f: Formula):
        """Initialize.

        :param f: formula to represent.
        """
        super().__init__(f)
        self.__dict__["_QuotedFormula__str"] = '"' + str(f) + '"'

    def __str__(self):
        """Cache str."""
        return self.__str

    def __repr__(self):
        """Nice representation."""
        return str(self)


class MonaProgram:
    """Implements a MONA program."""

    header = "m2l-str"
    vars: Set[str] = set()

    def __init__(self, f: Formula):
        """Initialize.

        :param f: formula to encode.
        :param i: instant of evaluation in the trace.
        """
        self.formula = f
        self._set_vars()

    def _set_vars(self):
        """Set MONA vars."""
        self.vars = set([v.upper() for v in self.formula.find_labels()])

    def __repr__(self):
        """Nice representation."""
        return str(self)

    def mona_program(self) -> str:
        """Construct the MONA program."""
        if self.vars:
            return "#{};\n{};\nvar2 {};\n{};\n".format(
                str(self.formula),
                self.header,
                ", ".join(self.vars),
                self.formula.to_mona("0"),
            )
        else:
            return "#{};\n{};\n{};\n".format(
                str(self.formula), self.header, self.formula.to_mona("0")
            )



class MonaSM:
    """Implements a MONA SM program."""

    header = "m2l-str"
    vars: Set[str] = set()

    def __init__(self, f: Formula):
        """Initialize.

        :param f: formula to encode.
        :param i: instant of evaluation in the trace.
        """
        self.formula = f
        self._set_vars()

    def _set_vars(self):
        """Set MONA vars."""
        self.vars = set([v.upper() for v in self.formula.find_labels()])

    def __repr__(self):
        """Nice representation."""
        return str(self)

    def mona_program(self) -> str:
        """Construct the MONA program."""
        if self.vars:

            return "#{0};\n{1};\nvar2 {2};\n{3} & ~(ex2 {4}: ({5} & ({6})&({7})));\n".format(
                str(self.formula),
                self.header,
                ", ".join(self.vars),
                self.formula.to_mona("0"),
                ",".join(["{0}_p".format(v) for v in self.vars]),
                "&".join(["{0}_p sub {0}".format(v) for v in self.vars]),
                "|".join(["{0}_p ~= {0}".format(v) for v in self.vars]),
                self.formula.to_mona_s("0")
            )
        else:
            return "#{};\n{};\n{};\n".format(
                str(self.formula), self.header, self.formula.to_mona("0")
            )





class MonaPSE:
    vars: Set[str] = set()

    def __init__(self, f1: Formula, f2: Formula):
        """Initialize.
        :param f1: formula to encode.
        :param f2: formula to encode.
        """
        self.f1,self.f2 = f1,f2
        self.vars = set([v.upper() for v in f1.find_labels()]).union(set([v.upper() for v in f2.find_labels()]))

    def _set_vars(self):
        """Set MONA vars."""
        self.vars = set([v.upper() for v in self.f.find_labels()])

    def __repr__(self):
        """Nice representation."""
        return "({})<->({})".formatstr(self)

    def mona_program(self) -> str:
        """Construct the MONA program."""
        monaOutput = None
        v1 = set([v.upper() for v in self.f1.find_labels()])
        v2 = set([v.upper() for v in self.f2.find_labels()])
        if v1.issubset(v2) and v2.issubset(v1): # strong equivalence on the same signature
            if len(v1) == 0 and len(v2) == 0:
                monaOutput = "#{0} <-> {1} in THTf;\n{2};\n ~((({3}) <=> ({4})) & (({5}) <=>({6})));\n".format(
                    self.f1,
                    self.f2, 
                    self.header,
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    self.f2.to_mona_s("0")
            )
            else:
                monaOutput = "#{0} <-> {1} in THTf;\n{2};\nvar2 {3};\n  ~(({4}) => ((({5}) <=> ({6})) & (({7}) <=>({8}))));\n".format(
                    self.f1,
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in self.vars]),
                    "&".join(["{0}_p sub {0}".format(v) for v in self.vars]),
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    self.f2.to_mona_s("0")
            )
        elif v1.issubset(v2): # f2 must be existentially quantified  
            exv2 = v2.difference(v1)
            print(exv2)


            monaOutput = "#({0}) <->(ex2 {1}: ({2})) ;\n{3};\n".format(self.f1,
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2,
                    self.header,
                    )
            if len(v1) != 0:
                monaOutput += "var2 {0};\n".format(",".join(["{0},{0}_p".format(v) for v in v1])) 
                monaOutput += "~(({0} <=> (ex2 {1}: {2})) & (({3} & {4}) <=> (ex2 {5}: ({6} & {7})))) ;\n".format(
                    self.f1.to_mona("0"),
                     ",".join(["{0}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
                    )
            else:
                #monaOutput += "var2 {0};\n".format(",".join(["{0},{0}_p".format(v) for v in v1])) 
                monaOutput += "~(({0} <=> (ex2 {1}: {2})) & (({3}) <=> (ex2 {4}: ({5} & {6})))) ;\n".format(
                    self.f1.to_mona("0"),
                     ",".join(["{0}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
                    )

        elif v2.issubset(v1): # f1 must be existentially quantified  
            exv1 = v1.difference(v2)

            monaOutput = "#(ex2 {0} : ({1})) <->({2}) ;\n{3};\nvar2 {4};\n ~(((ex2 {5}: {6}) <=> ({7})) & ((ex2 {8}: {9} & {10}) <=> ({11} & {12}))) ;\n".format(
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1,
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in v2]),
                    ",".join(["{0}".format(v) for v in exv1]),
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv1]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
            )
        
        else:
            fv = v1.intersection(v2) # free variables
            exv1,exv2 = v1.difference(fv), v2.difference(fv)
            monaOutput = "#(ex2 {0}:{1}) <->(ex2 {2}: ({3})) ;\n{4};\nvar2 {5};\n ~( ( (ex2 {6}: {7} )<=> (ex2 {8} : {9})) &  ( (ex2 {10}: {11} &  {12} )<=> (ex2 {13} : {14} & {15}))) ;\n".format(
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1,
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in fv]),
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1.to_mona("0"),
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv1]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0"),
            )
        return monaOutput


























class MonaSF:
    """Implements a MONA SM program."""

    header = "m2l-str"
    vars: Set[str] = set()

    def __init__(self, f1: Formula, f2: Formula):
        """Initialize.

        :param f: formula to encode.
        :param i: instant of evaluation in the trace.
        """
        self.f1,self.f2 = f1,f2
        self.vars = set([v.upper() for v in f1.find_labels()]).union(set([v.upper() for v in f2.find_labels()]))
        print(self.vars)

    def _set_vars(self):
        """Set MONA vars."""
        self.vars = set([v.upper() for v in self.f.find_labels()])

    def __repr__(self):
        """Nice representation."""
        return "({})<->({})".formatstr(self)

    def mona_program(self) -> str:
        """Construct the MONA program."""
        monaOutput = None
        v1 = set([v.upper() for v in self.f1.find_labels()])
        v2 = set([v.upper() for v in self.f2.find_labels()])
        if v1.issubset(v2) and v2.issubset(v1): # strong equivalence on the same signature
            print('normal strong equivalence')
            if len(v1) == 0 and len(v2) == 0:
                monaOutput = "#{0} <-> {1} in THTf;\n{2};\n ~((({3}) <=> ({4})) & (({5}) <=>({6})));\n".format(
                    self.f1,
                    self.f2, 
                    self.header,
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    self.f2.to_mona_s("0")
            )
            else:
                monaOutput = "#{0} <-> {1} in THTf;\n{2};\nvar2 {3};\n  ~(({4}) => ((({5}) <=> ({6})) & (({7}) <=>({8}))));\n".format(
                    self.f1,
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in self.vars]),
                    "&".join(["{0}_p sub {0}".format(v) for v in self.vars]),
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    self.f2.to_mona_s("0")
            )
        elif v1.issubset(v2): # f2 must be existentially quantified  
            exv2 = v2.difference(v1)
            print(exv2)


            monaOutput = "#({0}) <->(ex2 {1}: ({2})) ;\n{3};\n".format(self.f1,
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2,
                    self.header,
                    )
            if len(v1) != 0:
                monaOutput += "var2 {0};\n".format(",".join(["{0},{0}_p".format(v) for v in v1])) 
                monaOutput += "~(({0} <=> (ex2 {1}: {2})) & (({3} & {4}) <=> (ex2 {5}: ({6} & {7})))) ;\n".format(
                    self.f1.to_mona("0"),
                     ",".join(["{0}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
                    )
            else:
                #monaOutput += "var2 {0};\n".format(",".join(["{0},{0}_p".format(v) for v in v1])) 
                monaOutput += "~(({0} <=> (ex2 {1}: {2})) & (({3}) <=> (ex2 {4}: ({5} & {6})))) ;\n".format(
                    self.f1.to_mona("0"),
                     ",".join(["{0}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
                    )

        elif v2.issubset(v1): # f1 must be existentially quantified  
            exv1 = v1.difference(v2)

            monaOutput = "#(ex2 {0} : ({1})) <->({2}) ;\n{3};\nvar2 {4};\n ~(((ex2 {5}: {6}) <=> ({7})) & ((ex2 {8}: {9} & {10}) <=> ({11} & {12}))) ;\n".format(
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1,
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in v2]),
                    ",".join(["{0}".format(v) for v in exv1]),
                    self.f1.to_mona("0"),
                    self.f2.to_mona("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv1]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0")
            )
        
        else:
            fv = v1.intersection(v2) # free variables
            exv1,exv2 = v1.difference(fv), v2.difference(fv)
            monaOutput = "#(ex2 {0}:{1}) <->(ex2 {2}: ({3})) ;\n{4};\nvar2 {5};\n ~( ( (ex2 {6}: {7} )<=> (ex2 {8} : {9})) &  ( (ex2 {10}: {11} &  {12} )<=> (ex2 {13} : {14} & {15}))) ;\n".format(
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1,
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2, 
                    self.header,
                    ",".join(["{0},{0}_p".format(v) for v in fv]),
                    ",".join(["{}".format(v) for v in exv1]),
                    self.f1.to_mona("0"),
                    ",".join(["{}".format(v) for v in exv2]),
                    self.f2.to_mona("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv1]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v1]),
                    self.f1.to_mona_s("0"),
                    ",".join(["{0},{0}_p".format(v) for v in exv2]),
                    "&".join(["{0}_p sub {0}".format(v) for v in v2]),
                    self.f2.to_mona_s("0"),
            )
        return monaOutput




class Operator(Formula, ABC):
    """Implements an operator."""

    base_expression = (
        Symbols.ROUND_BRACKET_LEFT.value + "%s" + Symbols.ROUND_BRACKET_RIGHT.value
    )

    @property
    @abstractmethod
    def operator_symbol(self) -> OpSymbol:
        """Get the symbol of the operator."""


T = TypeVar("T")
OperatorChildren = Sequence[T]


class UnaryOperator(Generic[T], Operator, ABC):
    """A class to represent unary operator."""

    def __init__(self, f: T):
        """
        Instantiate the unary operator over a formula.

        :param f: the formula on which the operator is applied.
        """
        super().__init__()
        self.f = f

    def __str__(self):
        """Get the string representation."""
        return (
            str(self.operator_symbol)
            + Symbols.ROUND_BRACKET_LEFT.value
            + str(self.f)
            + Symbols.ROUND_BRACKET_RIGHT.value
        )

    def _members(self):
        return self.operator_symbol, self.f

    def __lt__(self, other):
        """Compare the formula with another formula."""
        return self.f.__lt__(other.f)

    def find_labels(self) -> Set[AtomSymbol]:
        """Return the set of symbols."""
        return cast(Formula, self.f).find_labels()


class BinaryOperator(Generic[T], Operator, ABC):
    """A generic binary formula."""

    def __init__(self, formulas: OperatorChildren):
        """
        Initialize the binary operator.

        :param formulas: the children formulas of the operator.
        """
        super().__init__()
        assert len(formulas) >= 2
        self.formulas = tuple(formulas)  # type: OperatorChildren

    def __str__(self):
        """Return the string representation."""
        return (
            "("
            + (" " + str(self.operator_symbol) + " ").join(map(str, self.formulas))
            + ")"
        )

    def _members(self) -> Tuple[OpSymbol, OperatorChildren]:
        return self.operator_symbol, self.formulas

    def find_labels(self) -> Set[AtomSymbol]:
        """Return the set of symbols."""
        return set.union(*map(lambda f: f.find_labels(), self.formulas))

    def to_nnf(self):
        """Transform in NNF."""
        return type(self)([f.to_nnf() for f in self.formulas])
