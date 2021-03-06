# -*- coding: utf-8 -*-

"""This module contains the implementation of Linear Temporal Logic on finite traces."""

from abc import abstractmethod, ABC
from typing import Set, Optional, Any
import re

from ltlf2dfa.base import (
    Formula,
    AtomicFormula,
    UnaryOperator,
    BinaryOperator,
    AtomSymbol,
)
from ltlf2dfa.ltlf2dfa import to_dfa
from ltlf2dfa.ltlf2dfa import to_dfa_sm
#from ltlf2dfa.ltlf2dfa import to_dfa_seq
from ltlf2dfa.pl import PLAtomic
from ltlf2dfa.symbols import Symbols, OpSymbol
from ltlf2dfa.helpers import new_var

from sympy import symbols, And, Not, Or, Implies, simplify

class LTLfFormula(Formula, ABC):
    """A class for the LTLf formula."""
    
    def closure(self):
        return set([])


    def delta(self,s,X):
        return None

    def new_var2(f,exv):
        """Compute next variable."""
        v2 = PLAtomic("v" + str(len(exv)))
        exv[f] = v2
        return v2
    
    def assigned_variable(self,f,exv):
        if f in exv:
            return exv[f]
        else:
            return None
        
    def gen_tlp(self):
        exv = {}
        df = set([])
        v = self._to_tlp(exv,df)
        df.add(v)
        return df
        

    def to_nnf(self) -> "LTLfFormula":
        """Convert an LTLf formula in NNF."""
        return self

    @abstractmethod
    def negate(self) -> "LTLfFormula":
        """Negate the formula."""

    def __repr__(self):
        """Get the representation."""
        return self.__str__()

    def to_mona(self, v: Optional[Any] = None) -> str: 
        """
        Tranform the LTLf formula into its encoding in MONA.

        :return: a string.
        """

    def to_mona_s(self, v: Optional[Any] = None) -> str: 
        """
        Tranform the LTLf formula into its encoding in MONA.

        :return: a string.
        """
    
    def _to_tlp(self,v,df):
        """
        transform a formula into a temporal logic program
        :return a (fresh) propositional atom label representing the formula 
        """
    def to_ldlf(self):
        """
        Tranform the formula into an equivalent LDLf formula.

        :return: an LDLf formula.
        """

    def to_dfa(self) -> str:
        """Translate into a DFA."""
        return to_dfa(self)

    def to_dfa_sm(self) -> str:
        """Translate into a DFA."""
        return to_dfa_sm(self)

    #def strongly_equivalent_to(self,f) -> str:
        """Translate into a DFA."""
    #    return to_dfa_seq(self,f)


class LTLfUnaryOperator(UnaryOperator[LTLfFormula], LTLfFormula, ABC):
    """A unary operator for LTLf."""


class LTLfBinaryOperator(BinaryOperator[LTLfFormula], LTLfFormula, ABC):
    """A binary operator for LTLf."""


class LTLfAtomic(AtomicFormula, LTLfFormula):
    """Class for LTLf atomic formulas."""

    name_regex = re.compile(r"[a-z][a-z0-9_]*")
    def delta(self,l,X):
        if self.s in X :
            return True
        else:
            return False

    def closure(self):
        return set([self,LTLfNot(self)])

    def negate(self):
        """Negate the formula."""
        return LTLfNot(self)

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return PLAtomic(self.s).find_labels()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf atomic formula."""
        if v != "0":
            return "({} in {})".format(v, self.s.upper())
        else:
            return "(0 in {})".format(self.s.upper())

    def to_mona_s(self,v="0") -> str:
        if v != "0":
            return "({0} in {1}_p)".format(v, self.s.upper())
        else:
            return "(0 in {}_p)".format(self.s.upper())

    def _to_tlp(self,v,df):
        return self

    # def to_ldlf(self):
    #     """Convert the formula to LDLf."""
    #     return LDLfDiamond(RegExpPropositional(PLAtomic(self.s)), LDLfLogicalTrue())



class LTLfTrue(LTLfAtomic):
    """Class for the LTLf True formula."""

    def delta(self,l,X):
        return True

    def closure(self):
        return set([self])

    def __init__(self):
        """Initialize the formula."""
        super().__init__(Symbols.TRUE.value)

    def negate(self):
        """Negate the formula."""
        return LTLfFalse()

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return set()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding for Top."""
        return Symbols.TRUE.value

    def to_mona_s(self,v="0") -> str:
        return Symbols.TRUE.value

    def _to_tlp(self,v,df):
        return self

    # def to_ldlf(self):
    #     """Convert the formula to LDLf."""
    #     return LDLfDiamond(RegExpPropositional(PLTrue()), LDLfLogicalTrue())


class LTLfFalse(LTLfAtomic):
    """Class for the LTLf False formula."""

    def delta(self,l,X):
        return False

    def closure(self):
        return set([self])

    def __init__(self):
        """Initialize the formula."""
        super().__init__(Symbols.FALSE.value)

    def negate(self):
        """Negate the formula."""
        return LTLfTrue()

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return set()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding for False."""
        return Symbols.FALSE.value

    def to_mona_s(self,v="0") -> str:
        return Symbols.FALSE.value

    def _to_tlp(self,v,df):
        return self


class LTLfNot(LTLfUnaryOperator):
    """Class for the LTLf not formula."""

    def delta(self,l,X):
        return Not(self.f.delta(l,X))

    def closure(self):
        return set([self,self.f]).union(self.f.closure())

    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.NOT.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        if not isinstance(self.f, AtomicFormula):
            return self.f.negate().to_nnf()
        else:
            return self

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.f

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Not formula."""
        return "~({})".format(self.f.to_mona(v))

    def to_mona_s(self,v="0") -> str:
        return "(~{} & ~{})".format(self.f.to_mona_s(v), self.f.to_mona(v))
    # def to_ldlf(self):
    #     """Convert the formula to LDLf."""
    #     return LDLfNot(self.f.to_ldlf())

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self, v)
        if nv != None:
            return nv
        nv = self.new_var2(v)
        sf = self.assigned_variable(self.f,v)
        if sf == None:
            sf = self.f._to_tlp(v,df)
        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfNot(sf)])))
        return nv

class LTLfAnd(LTLfBinaryOperator):
    """Class for the LTLf And formula."""

    def delta(self,l,X):
        v = True
        for i in self.formulas:
            v = And(v,i.delta(l,X))
        return v


    def closure(self):
        s = set([self,LTLfNot(self)])
        for i in self.formulas:
            s=s.union(i.closure())
        return s
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.AND.value

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfOr([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf And formula."""
        return "({})".format(" & ".join([f.to_mona(v) for f in self.formulas]))

    def to_mona_s(self,v="0") -> str:
        return "({})".format(" & ".join([f.to_mona_s(v) for f in self.formulas]))
    # def to_ldlf(self):
    #     """Convert the formula to LDLf."""
    #     return LDLfAnd([f.to_ldlf() for f in self.formulas])

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        sf = []
        for i in self.formulas:
            cf = self.assigned_variable(i,v)
            if cf == None:
                cf = i._to_tlp(v,df)
            sf.append(cf)
        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfAnd(sf)])))
        return nv

class LTLfOr(LTLfBinaryOperator):
    """Class for the LTLf Or formula."""
    
    def delta(self,l,X):
        v = False
        for i in self.formulas:
            v = Or(v,i.delta(l,X))
        return v


    def closure(self):
        s = set([self,LTLfNot(self)])
        for i in self.formulas:
            s=s.union(i.closure())
        return s

    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.OR.value

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfAnd([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Or formula."""
        return "({})".format(" | ".join([f.to_mona(v) for f in self.formulas]))

    def to_mona_s(self,v="0") -> str:
        return "({})".format(" | ".join([f.to_mona_s(v) for f in self.formulas]))
    # def to_ldlf(self):
    #     """Convert LTLf formula to LDLf."""
    #     return LDLfOr([f.to_ldlf() for f in self.formulas])

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        sf = []
        for i in self.formulas:
            cf = self.assigned_variable(i,v)
            if cf == None:
                cf = i._to_tlp(v,df)
            sf.append(cf)
        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfOr(sf)])))
        return nv

class LTLfImplies(LTLfBinaryOperator):
    """Class for the LTLf Implication formula."""
    def delta(self,l,X):
        first, second = self.formulas[0:2]
        return Or(Not(first.delta(l,X)),second.delta(l,X))

    def closure(self):
        first, second = self.formulas[0:2]
        return LTLfOr([LTLfNot(first),second]).closure()

    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.IMPLIES.value

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        first, second = self.formulas[0:2]
        final_formula = LTLfOr([LTLfNot(first).to_nnf(), second.to_nnf()])
        for subformula in self.formulas[2:]:
            final_formula = LTLfOr(
                [LTLfNot(final_formula).to_nnf(), subformula.to_nnf()]
            )
        return final_formula

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Implication formula."""
        f,g = self.formulas[0:2]
        return "({} => {})".format(f.to_mona(v),g.to_mona(v))


    def to_mona_s(self,v="0") -> str:
        f,g = self.formulas[0:2]
        return "(({} => {}) & ({} => {}))".format(f.to_mona(v), g.to_mona(v), f.to_mona_s(v), g.to_mona_s(v))

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)


        f1 = self.assigned_variable(self.formulas[0],v)
        if f1 == None:
            f1 = self.formulas[0]._to_tlp(v,df)
        f2 = self.assigned_variable(self.formulas[1],v)
        if f2 == None:
           f2 = self.formulas[1]._to_tlp(v,df)
        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfImplies([f1,f2])])))
        return nv

class LTLfEquivalence(LTLfBinaryOperator):
    """Class for the LTLf Equivalente formula."""

    def delta(self,l,X):
        f,g = self.formulas[0:2]
        f,g = f.delta(l,X), g.delta(l,X)
        return Or(And(f,g),And(Not(f),Not(g)))

    def closure(self):
        f,g = self.formulas[0:2]
        return set([LTLfNot(self),self]).union(f.closure()).union(g.closure())
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.EQUIVALENCE.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        fs = self.formulas
        pos = LTLfAnd(fs)
        neg = LTLfAnd([LTLfNot(f) for f in fs])
        res = LTLfOr([pos, neg]).to_nnf()
        return res

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_mona(self, v="0") -> str:
        f,g = self.formulas[0:2]
        return "({} <=> {})".format(f.to_mona(v),g.to_mona(v))

    def to_mona_s(self,v="0") -> str:
        f,g = self.formulas[0:2]
        return "({} <=> {}) &  ({} <=> {})".format(f.to_mona(v),g.to_mona(v), f.to_mona_s(v), g.to_mona_s(v))

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)


        f1 = self.assigned_variable(self.formulas[0],v)
        if f1 == None:
            f1 = self.formulas[0]._to_tlp(v,df)
        f2 = self.assigned_variable(self.formulas[1],v)
        if f2 == None:
            f2 = self.formulas[1]._to_tlp(v,df)
        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfEquivalence([f1,f2])])))
        return nv


class LTLfNext(LTLfUnaryOperator):
    """Class for the LTLf Next formula."""

    def delta(self,l,X):
        if 'last' in X:
            return False
        else:
            return symbols("s" + str(l.index(self.f)))


    def closure(self):
        return set([self, LTLfNot(self)]).union(self.f.closure())
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.NEXT.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfNext(self.f.to_nnf())

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfWeakNext(self.f.negate())

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Next formula."""
        ex_var = new_var(v)
        if v != "0":
            return "(ex1 {0}: {0}={1}+1 & {2})".format(ex_var, v, self.f.to_mona(ex_var))
        else:
            return "(ex1 {0}: {0}=1 & {1})".format(ex_var, self.f.to_mona(ex_var))

    # def to_ldlf(self):
    #     """Convert the formula to LDLf."""
    #     return LDLfDiamond(
    #         RegExpPropositional(PLTrue()),
    #         LDLfAnd([self.f.to_ldlf(), LDLfNot(LDLfEnd())]),
    #     )

    def to_mona_s(self,v="0") -> str:
        ex_var = new_var(v)
        if v != "0":
            return "(ex1 {0}: {0}={1}+1 & {2})".format(ex_var, v, self.f.to_mona_s(ex_var))
        else:
            return "(ex1 {0}: {0}=1 & {1})".format(ex_var, self.f.to_mona_s(ex_var))

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.f,v)
        if f1 == None:
            f1 = self.f._to_tlp(v,df)

        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfNext(f1)])))
        df.add(LTLfAlways(LTLfImplies([LTLfLast(),LTLfNot(nv)])))
        return nv



class LTLfWeakNext(LTLfUnaryOperator):
    """Class for the LTLf Weak Next formula."""

    def delta(self,l,X):
        if 'last' in X:
            return True
        else:
            return symbols("s" + str(l.index(self.f)))

    def closure(self):
        return set([self, LTLfNot(self)]).union(self.f.closure())
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.WEAK_NEXT.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfWeakNext(self.f.to_nnf())

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfNext(self.f.negate())

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf WeakNext formula."""
        ex_var = new_var(v)
        if v != "0":
            return "(({1} = max($)) | (ex1 {0}: {0}={1}+1 & {2}))".format(
                ex_var, v, self.f.to_mona(ex_var)
            )
        else:
            return "((0 = max($)) | (ex1 {0}: {0}=1 & {1}))".format(
                ex_var, self.f.to_mona(ex_var)
            )

    def to_mona_s(self,v="0") -> str:
        """Return the MONA encoding of an LTLf WeakNext formula."""
        ex_var = new_var(v)
        if v != "0":
            return "(({1} = max($)) | (ex1 {0}: {0}={1}+1 & {2}))".format(
                ex_var, v, self.f.to_mona_s(ex_var)
            )
        else:
            return "((0 = max($)) | (ex1 {0}: {0}=1 & {1}))".format(
                ex_var, self.f.to_mona_s(ex_var)
            )

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.f,v)
        if f1 == None:
            f1 = self.f._to_tlp(v,df)

        df.add(LTLfAlways(LTLfEquivalence([nv,LTLfWeakNext(f1)])))
        df.add(LTLfAlways(LTLfImplies([LTLfLast(),nv])))
        return nv


class LTLfUntil(LTLfBinaryOperator):
    """Class for the LTLf Until formula."""


    def delta(self,l,X): #we should be able to manage the ords regarding last      
        f1 = self.formulas[0].delta(l,X)
        f2 = self.formulas[1].delta(l,X)
        if 'last' in X:
            return f2
        else: 
            return Or(f2,And(f1,symbols("s" + str(l.index(self)))))


    def closure(self):
        s = set([self, LTLfNot(self)])
        s = s.union(self.formulas[0].closure())
        s = s.union(self.formulas[1].closure())
        return s


    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.UNTIL.value

    def to_nnf(self):
        """Transform to NNF."""
        return LTLfUntil([f.to_nnf() for f in self.formulas])

    def negate(self):
        """Negate the formula."""
        return LTLfRelease([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Until formula."""
        ex_var = new_var(v)
        all_var = new_var(ex_var)
        f1 = self.formulas[0].to_mona(v=all_var)
        f2 = self.formulas[1].to_mona(v=ex_var)
        return "(ex1 {0}: {1}<={0}&{0}<=max($) & {2} & (all1 {3}: {1}<={3}&{3}<{0} => {4}))".format(ex_var, v, f2, all_var, f1)

    def to_mona_s(self,v="0") -> str:
        """Return the MONA encoding of an LTLf Until formula."""
        ex_var = new_var(v)
        all_var = new_var(ex_var)
        f1 = self.formulas[0].to_mona_s(v=all_var)
        f2 = self.formulas[1].to_mona_s(v=ex_var)
        return "(ex1 {0}: {1}<={0}&{0}<=max($) & {2} & (all1 {3}: {1}<={3}&{3}<{0} => {4}))".format(ex_var, v, f2, all_var, f1)


    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.formulas[0],v)
        if f1 == None:
            f1 = self.formulas[0]._to_tlp(v,df)

        f2 = self.assigned_variable(self.formulas[1],v)
        if f2 == None:
            f2 = self.formulas[1]._to_tlp(v,df)

        f3 = self.assigned_variable(LTLfNext(self),v)
        if f3 == None:
            f3 = LTLfNext(self)._to_tlp(v,df)

        df.add(LTLfAlways(LTLfEquivalence([nv, LTLfOr([f2,LTLfAnd([f1,f3])])])))
        return nv

class LTLfRelease(LTLfBinaryOperator):
    """Class for the LTLf Release formula."""



    def delta(self,l,X): #we should be able to manage the ords regarding last      
        f1 = self.formulas[0].delta(l,X)
        f2 = self.formulas[1].delta(l,X)
        if 'last' in X:
            return f2
        else: 
            return And(f2,Or(f1,symbols("s" + str(l.index(self)))))



    
    def closure(self):
        s = set([self, LTLfNot(self)])
        s = s.union(self.formulas[0].closure())
        s = s.union(self.formulas[1].closure())
        return s


    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.RELEASE.value

    def to_nnf(self):
        """Transform to NNF."""
        return LTLfRelease([f.to_nnf() for f in self.formulas])

    def negate(self):
        """Negate the formula."""
        return LTLfUntil([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Release formula."""
        all_var = new_var(v)
        ex_var = new_var(all_var)
        f1 = self.formulas[0].to_mona(v=ex_var)
        f2 = self.formulas[1].to_mona(v=all_var)
        return "(all1 {0}: ({1}<={0}&{0}<=max($)) => (({2}) | (ex1 {3}: {1} <= {3} & {3} < {0} & {4})))".format(all_var,v,f2,ex_var,f1)

    def to_mona_s(self,v="0") -> str:
        """Return the MONA encoding of an LTLf Release formula."""
        all_var = new_var(v)
        ex_var = new_var(all_var)
        f1 = self.formulas[0].to_mona_s(v=ex_var)
        f2 = self.formulas[1].to_mona_s(v=all_var)
        return "(all1 {0}: ({1}<={0}&{0}<=max($)) => ({2} | (ex1 {3}: {1} <= {3} & {3} < {0} & {4})))".format(all_var,v,f2,ex_var,f1)


    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.formulas[0],v)
        if f1 == None:
            f1 = self.formulas[0]._to_tlp(v,df)

        f2 = self.assigned_variable(self.formulas[1],v)
        if f2 == None:
            f2 = self.formulas[1]._to_tlp(v,df)

        f3 = self.assigned_variable(LTLfWeakNext(self),v)
        if f3 == None:
            f3 = LTLfWeakNext(self)._to_tlp(v,df)

        df.add(LTLfAlways(LTLfEquivalence([nv, LTLfAnd([f2,LTLfOr([f1,f3])])])))
        return nv


class LTLfEventually(LTLfUnaryOperator):
    """Class for the LTLf Eventually formula."""
    

    def delta(self,l,X): #we should be able to manage the ords regarding last      
        f1 = self.f.delta(l,X)
        if 'last' in X:
            return f1
        else: 
            return Or(f1,symbols("s" + str(l.index(self))))

    def closure(self):
        s = set([self, LTLfNot(self)])
        s = s.union(self.f.closure())
        return s

    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.EVENTUALLY.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfUntil([LTLfTrue(), self.f])

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Eventually formula."""
        ex_var = new_var(v)
        return "(ex1 {0}: {1}<={0}&{0}<=max($) & {2})".format(ex_var, v, self.f.to_mona(v=ex_var))

    def to_mona_s(self,v="0") -> str:
        ex_var = new_var(v)
        return "(ex1 {0}: {1}<={0}&{0}<=max($) & {2})".format(ex_var, v, self.f.to_mona_s(v=ex_var))

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.f,v)
        if f1 == None:
            f1 = self.f.to_tlp(v,df)

        f2 = self.assigned_variable(LTLfNext(self),v)
        if f2 == None:
            f2 = LTLfNext(self)._to_tlp(v,df)
        
        df.add(LTLfAlways(LTLfEquivalence([nv, LTLfOr([f1,f2])])))
        return nv

class LTLfAlways(LTLfUnaryOperator):
    """Class for the LTLf Always formula."""


    def delta(self,l,X): #we should be able to manage the ords regarding last      
        f1 = self.f.delta(l,X)
        if 'last' in X:
            return f1
        else: 
            return And(f1,symbols("s" + str(l.index(self))))



    def closure(self):
        s = set([self, LTLfNot(self)])
        s = s.union(self.f.closure())
        return s

    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.ALWAYS.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfRelease([LTLfFalse(), self.f.to_nnf()])

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf Always formula."""
        all_var = new_var(v)
        return "(all1 {0}: {1}<={0}&{0}<=max($) => {2})".format(all_var, v, self.f.to_mona(v=all_var))

    def to_mona_s(self,v="0") -> str:
        all_var = new_var(v)
        return "(all1 {0}: {1}<={0}&{0}<=max($) => {2})".format(all_var, v, self.f.to_mona_s(v=all_var))

    def _to_tlp(self,v,df):
        nv = self.assigned_variable(self,v)
        if nv != None:
            return nv
        nv = self.new_var2(v)

        f1 = self.assigned_variable(self.f,v)
        if f1 == None:
            f1 = self.f._to_tlp(v,df)

        f2 = self.assigned_variable(LTLfWeakNext(self),v)
        if f2 == None:
            f2 = LTLfWeakNext(self)._to_tlp(v,df)

        df.add(LTLfAlways(LTLfEquivalence([nv, LTLfAnd([f1,f2])])))
        return nv


class LTLfLast(LTLfFormula):
    """Class for the LTLf Last formula."""

    def delta(self,l,X): # How do we handle the final
        if 'last' in X:
            return True;
        else:
            return False;

    def closure(self):
        return set([])

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfAnd([LTLfWeakNext(LTLfFalse()), LTLfNot(LTLfEnd())]).to_nnf()

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return set()

    def _members(self):
        return (Symbols.LAST.value,)

    def __str__(self):
        """Get the string representation."""
        return Symbols.LAST.value

    def _to_tlp(self,v,df):
        return self

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf atomic formula."""
        if v == "0":
            return "(0 = max($))"
        else:
            return "({} = max($))".format(v)

    def to_mona_s(self,v="0") -> str:
        if v == "0":
            return "(0 = max($))"
        else:
            return "({} = max($))".format(v)

class LTLfEnd(LTLfFormula):
    """Class for the LTLf End formula."""

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return set()

    def _members(self):
        return (Symbols.END.value,)

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfAlways(LTLfFalse()).to_nnf()

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def __str__(self):
        """Get the string representation."""
        return "_".join(map(str, self._members()))

    def _to_tlp(self,v,df):
        return self


class LTLfBefore(LTLfUnaryOperator):
    """Class for the PLTLf Before formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.BEFORE.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfBefore(self.f.to_nnf())

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfNot(self.f.negate())

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Before formula."""
        ex_var = new_var(v)
        if v == "0":
            #return "(ex1 {0}: {0}={1}-1 & {0}>=0 & {2})".format( ex_var, v, self.f.to_mona(ex_var))
            return "(false)"
        elif v == "max($)":
            return "(ex1 {0}: {0}=max($)-1 & max($)>0 & {1})".format(ex_var, self.f.to_mona(ex_var))
        else:
            return "(ex1 {0}: {0}={1}-1 & {0}>=0 & {2})".format( ex_var, v, self.f.to_mona(ex_var))


    def to_mona_s(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Before formula."""
        ex_var = new_var(v)
        if v == "0":
            return "(false)"
        elif v == "max($)":
            return "(ex1 {0}: {0}=max($)-1 & max($)>0 & {1})".format(ex_var, self.f.to_mona_s(ex_var))
        else:
            return "(ex1 {0}: {0}={1}-1 & {0}>=0 & {2})".format( ex_var, v, self.f.to_mona_s(ex_var))


    # def to_ldlf(self):
    #     return LDLfDiamond(
    #         RegExpPropositional(PLTrue()),
    #         LDLfAnd([self.f.to_ldlf(), LDLfNot(LDLfEnd())]),
    #     )



class LTLfWBefore(LTLfUnaryOperator):
    """Class for the PLTLf Before formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.WBEFORE.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return None #LTLfBefore(self.f.to_nnf())

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return LTLfNot(self.f.negate())

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Before formula."""
        ex_var = new_var(v)
        if v == "0":
            #return "(ex1 {0}: {0}={1}-1 & {0}>=0 & {2})".format( ex_var, v, self.f.to_mona(ex_var))
            return "(true)"
        elif v == "max($)":
            return "(({2} = 0) | (ex1 {0}: {0}=max($)-1 & max($)>0 & {1}))".format(ex_var, self.f.to_mona(ex_var),v)
        else:
            return "(({1} = 0) | (ex1 {0}: {0}={1}-1 & {0}>=0 & {2}))".format( ex_var, v, self.f.to_mona(ex_var))


    def to_mona_s(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Before formula."""
        ex_var = new_var(v)
        if v == "0":
            return "(true)"
        elif v == "max($)":
            return "(({2} = 0) | (ex1 {0}: {0}=max($)-1 & max($)>0 & {1}))".format(ex_var, self.f.to_mona_s(ex_var),v)
        else:
            return "(({1} = 0)|(ex1 {0}: {0}={1}-1 & {0}>=0 & {2}))".format( ex_var, v, self.f.to_mona_s(ex_var))


    # def to_ldlf(self):
    #     return LDLfDiamond(
    #         RegExpPropositional(PLTrue()),
    #         LDLfAnd([self.f.to_ldlf(), LDLfNot(LDLfEnd())]),
    #     )



class LTLfSince(LTLfBinaryOperator):
    """Class for the PLTLf Since formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.SINCE.value

    def to_nnf(self):
        """Transform to NNF."""
        return LTLfSince([f.to_nnf() for f in self.formulas])

    def negate(self):
        """Negate the formula."""
        return LTLfNot([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Since formula."""
        if v != "0":
            ex_var = new_var(v)
            all_var = new_var(ex_var)
            f1 = self.formulas[0].to_mona(v=all_var)
            f2 = self.formulas[1].to_mona(v=ex_var)
       #return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
            return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
        else:
            return self.formulas[1].to_mona(v)

    def to_mona_s(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Since formula."""
        if v != "0":
            ex_var = new_var(v)
            all_var = new_var(ex_var)
            f1 = self.formulas[0].to_mona_s(v=all_var)
            f2 = self.formulas[1].to_mona_s(v=ex_var)
       #return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
            return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
        else:
            return self.formulas[1].to_mona_s(v)

    # def to_ldlf(self):
    #     f1 = self.formulas[0].to_ldlf()
    #     f2 = (
    #         PLTLfSince(self.formulas[1:]).to_ldlf()
    #         if len(self.formulas) > 2
    #         else self.formulas[1].to_ldlf()
    #     )
    #     return LDLfDiamond(
    #         RegExpStar(RegExpSequence([RegExpTest(f1), RegExpPropositional(PLTrue())])),
    #         LDLfAnd([f2, LDLfNot(LDLfEnd())]),
    #     )





class LTLfTrigger(LTLfBinaryOperator):
    """Class for the PLTLf Since formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.TRIGGER.value

    def to_nnf(self):
        """Transform to NNF."""
        return LTLfTrigger([f.to_nnf() for f in self.formulas])

    def negate(self):
        """Negate the formula."""
        return LTLfNot([f.negate() for f in self.formulas])

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Since formula."""
        if v != "0":
            all_var = new_var(v)
            ex_var = new_var(all_var)
            f1 = self.formulas[0].to_mona(v=all_var)
            f2 = self.formulas[1].to_mona(v=ex_var)
       #return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
            return "(all1 {0}: 0<={0}&{0}<={1} => ({2} | (ex1 {3}: ({0}<{3}&{3}<={1}) &  {4})))".format( ex_var, v, f2, all_var, f1)
        else:
            return self.formulas[1].to_mona(v)

    def to_mona_s(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Since formula."""
        if v != "0":
            ex_var = new_var(v)
            all_var = new_var(ex_var)
            f1 = self.formulas[0].to_mona_s(v=all_var)
            f2 = self.formulas[1].to_mona_s(v=ex_var)
       #return "(ex1 {0}: 0<={0}&{0}<={1} & {2} & (all1 {3}: ({0}<{3}&{3}<={1}) => {4}))".format( ex_var, v, f2, all_var, f1)
            return "(all1 {0}: 0<={0}&{0}<={1} => ({2} | (ex1 {3}: ({0}<{3}&{3}<={1}) &  {4})))".format( ex_var, v, f2, all_var, f1)
        else:
            return self.formulas[1].to_mona_s(v)

    # def to_ldlf(self):
    #     f1 = self.formulas[0].to_ldlf()
    #     f2 = (
    #         PLTLfSince(self.formulas[1:]).to_ldlf()
    #         if len(self.formulas) > 2
    #         else self.formulas[1].to_ldlf()
    #     )
    #     return LDLfDiamond(
    #         RegExpStar(RegExpSequence([RegExpTest(f1), RegExpPropositional(PLTrue())])),
    #         LDLfAnd([f2, LDLfNot(LDLfEnd())]),
    #     )





class LTLfOnce(LTLfUnaryOperator):
    """Class for the PLTLf Once formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.ONCE.value

    def to_nnf(self) -> LTLfFormula:
        """Transform to NNF."""
        return LTLfSince([LTLfTrue(), self.f])

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Once formula."""
        if v != "0":
            ex_var = new_var(v)
            return "(ex1 {0}: 0<={0}&{0}<={1} & {2})".format(ex_var,v,self.f.to_mona(ex_var))
        else:
            return self.f.to_mona("0")

    def to_mona_s(self, v="0") -> str:
        if v != "0":
            ex_var = new_var(v)
            return "(ex1 {0}: 0<={0}&{0}<={1} & {2})".format(ex_var,v,self.f.to_mona_s(ex_var))
        else:
            return self.f.to_mona_s(v)

    # def to_ldlf(self):
    #     return LDLfDiamond(
    #         RegExpStar(RegExpPropositional(PLTrue())),
    #         LDLfAnd([self.f.to_ldlf(), LDLfNot(LDLfEnd())]),
    #     )




class LTLfHistorically(LTLfUnaryOperator):
    """Class for the PLTLf Historically formula."""

    def closure(self):
        raise Exception('not implemented')
    @property
    def operator_symbol(self) -> OpSymbol:
        """Get the operator symbol."""
        return Symbols.HISTORICALLY.value

    # def to_nnf(self) -> PLTLfFormula:
    #     """Transform to NNF."""
    #     return PLTLfRelease([PLTLfFalse(), self.f.to_nnf()])

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of a PLTLf Historically formula."""
        all_var = new_var(v)
        if v != "0":
            return "(all1 {0}: (0<={0}&{0}<={1}) => {2})".format(ex_var,v,self.f.to_mona(all_var))
        else:
            return self.f.to_mona_s(v)


class LTLfInit(LTLfFormula):
    """Class for the PLTLf Last formula."""

    def closure(self):
        raise Exception('not implemented')
    # def to_nnf(self) -> PLTLfFormula:
    #     """Transform to NNF."""
    #     return PLTLfAnd([PLTLfWeakBefore(PLTLfFalse()), PLTLfNot(PLTLfEnd())]).to_nnf()

    def negate(self) -> LTLfFormula:
        """Negate the formula."""
        return self.to_nnf().negate()

    def find_labels(self) -> Set[AtomSymbol]:
        """Find the labels."""
        return set()

    def _members(self):
        return (Symbols.LAST.value,)

    def __str__(self):
        """Get the string representation."""
        return Symbols.LAST.value

    def to_mona(self, v="0") -> str:
        """Return the MONA encoding of an LTLf atomic formula."""
        if v == "max($)":
            return "(0 = max($))"
        else:
            return "({} = 0)".format(v)

    def to_mona_s(self,v="0") -> str:
        if v == "max($)":
            return "(0 = max($))"
        else:
            return "({} = 0)".format(v)


