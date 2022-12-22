from __future__ import annotations
from beartype.typing import *
from typing import TypeAlias
if TYPE_CHECKING:
    pass

from rich import inspect
from enum import Enum
import re


class LexItem(Enum):
    INTEGER = 1
    SYMBOL = 2
    OPERATOR = 3
            

expr = "b = 2 + a * 10"

any_digit: str = r"(\d+)"
any_word: str = r"(\w+)"
any_char: str = r"(.)"

expression = rf"\s*(?:{any_digit}|{any_word}|{any_char})"
regex = re.compile(expression)

for m in regex.finditer(expr):
    print(
        LexItem(m.lastindex),
        repr(m.group(cast(str, m.lastindex)))
    )


class Operation(Protocol):

    def __call__(self, lhs: RegexElement, rhs: RegexElement) -> None:
        ...


class Test(Protocol):

    def __call__(self, lhs: str, rhs: str) -> Relation | None:
        ...


class Relation(str, Enum):
    SUPERSET = "superset"
    SUBSET = "subset"
    INTERSECT = "intersect"
    DISJOINT = "disjoint"
    EQUAL = "equal"


T = TypeVar("T")

class u_set(set[T], Generic[T]):

    def __add__(self, other: u_set[T]) -> u_set[T]:
        return self.__class__(self.union(other))

    def copy(self) -> u_set[T]:
        return cast(u_set, super().copy())


class RegexElement:

    def __init__(self, expression: str) -> None:
        self.expression = expression

        self.supersets: u_set[RegexElement] = u_set()
        self.subsets: u_set[RegexElement] = u_set()
        self.disjoints: u_set[RegexElement] = u_set()
        self.intersects: u_set[RegexElement] = u_set()
        self.maybes: list[RegexElement] = []
        self.precompilation = {}
        
        self.compiled = re.compile(expression, re.IGNORECASE)

    def __hash__(self) -> int:
        return hash(self.expression)

    
class SubsetGraph:

    def __init__(self, tests: list[Test]) -> None:
        self.tests = tests
        self.elements: list[RegexElement] = []
        self._roots: list[RegexElement] = []
        self._dirty: bool = True

    @property
    def roots(self) -> list[RegexElement]:
        if self._dirty:
            self._roots = [i for i in self.elements if not i.supersets]
        return self._roots

    def add_expression(self, expression: str) -> None:
        new_element = RegexElement(expression)
        for root in self.roots:
            self.process(new_element, root)
        self.elements.append(new_element)
    
    def process(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        relationship = self.compare(new_element, root_element)
        if relationship:
            func: Operation = getattr(self, 'add_' + relationship)
            func(new_element, root_element)

    def add_superset(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        for item in root_element.subsets:
            item.supersets.add(new_element)
            new_element.subsets.add(root_element)

        root_element.supersets.add(new_element)
        new_element.subsets.add(root_element)

    def add_subset(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        for item in root_element.subsets:
            self.process(new_element, item)
        root_element.subsets.add(new_element)
        new_element.supersets.add(root_element)

    def add_disjoint(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        for item in root_element.subsets:
            item.disjoints.add(new_element)
            new_element.disjoints.add(root_element)

        new_element.disjoints.add(root_element)
        root_element.disjoints.add(new_element)

    def add_intersect(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        for item in root_element.subsets:
            item.disjoints.add(new_element)
            new_element.disjoints.add(item)

        new_element.disjoints.add(root_element)
        root_element.disjoints.add(new_element)

    def add_equal(
        self, 
        new_element: RegexElement, 
        root_element: RegexElement
    ) -> None:
        new_element.supersets = root_element.supersets.copy()
        new_element.subsets = root_element.subsets.copy()
        new_element.disjoints = root_element.disjoints.copy()
        new_element.intersects = root_element.intersects.copy()

    def compare(self, a: RegexElement, b: RegexElement) -> str | None:
        for test in self.tests:
            result = test(a.expression, b.expression)
            if result:
                return result
            
    def match(self, text: str, strict: bool = True) -> list[RegexElement]:
        matches = set()
        self._match(text, self.roots, matches)
        
        out: list[RegexElement] = []
        for element in matches:
            for subset in element.subsets:
                if subset in matches:
                    break
            else:
                out.append(element)

        if strict and len(out) > 1:
            for i in out:
                print(i.expression)
            raise Exception(f"Multiple equally specific matches found for {text}")
        
        return out

    def _match(
        self, 
        text: str, 
        elements: list[RegexElement], 
        matches: set[RegexElement]
    ) -> None:
        new_elements = []
        for element in elements:
            m = element.compiled.match(text)
            if m:
                matches.add(element)
                new_elements.extend(element.subsets)
        if new_elements:
            self._match(text, new_elements, matches)


def _exapnd_regex(a, p, out_strings):
    one = False
    last = 0
    d = p.finditer(a)
    for e in d:
        one = True
        grp = e.group()
        if grp.startswith('(') and '){' in grp:
            grp = grp[1:]
            pattern, iter_name = grp.split('){')
        else:
            pattern, iter_name = grp.split('{')
        if iter_name.endswith('}'):
            iter_name = iter_name[:-1]
        min_iter, max_iter = iter_name.split(',')
        min_iter = int(min_iter)
        max_iter = int(max_iter)
        if min_iter == max_iter:
            pattern *= max_iter
            for i, s in enumerate(out_strings):
                out_strings[i] = s + a[last:e.start()] + pattern
        else:
            if min_iter > max_iter:
                raise Exception("Cannot expand regex: " + a)
            else:
                old_out_strings = out_strings[:]
                out_strings.clear()
                for z in range(min_iter, max_iter + 1):
                    for i in old_out_strings:
                        out_strings.append(i + a[last:e.start()] + pattern * z)
        last = e.end()
    return one, last


def expand_regex(a):
    out_strings = ['']
    b = re.compile(r'.\{[0-9]*,[0-9]*\}')
    c = re.compile(r'\(.*?\)\{[0-9]*,[0-9]*\}')
    one, last = _exapnd_regex(a, c, out_strings)
    if one:
        for i in range(len(out_strings)):
            out_strings[i] += a[last:]
    else:
        one, last = _exapnd_regex(a, b, out_strings)
        if one:
            for i in range(len(out_strings)):
                out_strings[i] += a[last:]
        else:
            yield a
            return
    for i in out_strings:
        yield from expand_regex(i)


def check_equal(lhs: str, rhs: str) -> Relation | None:
    if lhs == rhs:
        return Relation.EQUAL


def check_prefixes(lhs: str, rhs: str) -> Relation | None:
    for idx in range(len(lhs)):
        if idx == len(rhs):
            break
        if lhs[idx] in '(.[' or rhs[idx] in '(.[)':
            break
        if lhs[idx] != rhs[idx]:
            return Relation.DISJOINT

  
def check_suffixes(a, b):
    for i in range(len(a)):
        if i == len(b):
            break
        if a[-i - 1] in ").]*+}?":
            try:
                if a[-i - 2] == "\\":
                    continue
            except IndexError:
                pass
            break
        elif b[-i - 1] in ").]*+}?":
            try:
                if b[-i - 2] == "\\":
                    continue
            except IndexError:
                pass
            break
        elif a[-i - 1] != b[-i - 1]:
            return Relation.DISJOINT


def check_dotstar(a, b):
    astar = False
    bstar = False

    if a.endswith(".*"):
        a = a[:-2]
        astar = True
    elif a.endswith("(/.*)?"):
        a = a[:-6]
        astar = True

    if b.endswith(".*"):
        b = b[:-2]
        bstar = True
    elif b.endswith("(/.*)?"):
        b = b[:-6]
        bstar = True

    if astar and bstar:
        if a.startswith(b):
            return Relation.SUBSET
        elif b.startswith(a):
            return Relation.SUPERSET
    elif bstar and a.startswith(b):
        return Relation.SUBSET
    elif astar and b.startswith(a):
        return Relation.SUPERSET


def check_fixed(a, b):
    a_fixed = True
    b_fixed = True

    i = 0
    while i < len(a):
        if a[i] == "\\":
            i += 1
        if a[i] in r"([.*{?+":
            a_fixed = False
        i += 1

    i = 0
    while i < len(b):
        if b[i] == "\\":
            i += 1
        if b[i] in r"([.*{?+":
            b_fixed = False
        i += 1

    if a_fixed and not b_fixed:
        if re.match(b, a):
            return Relation.SUBSET
    elif b_fixed and not a_fixed:
        if re.match(a, b):
            return Relation.SUPERSET


def check_match(a, b):
    if re.compile(a).match(b.rstrip('$').lstrip('^')):
        return Relation.SUPERSET
    if re.compile(b).match(a.rstrip('$').lstrip('^')):
        return Relation.SUBSET


def check_expand(a, b):
    c = list(expand_regex(a))
    d = list(expand_regex(b))
    bina = False
    ainb = False
    allainb = True
    allbina = True
    for i in c:
        if i in d:
            ainb = True
        else:
            allainb = False
    for i in d:
        if i in c:
            bina = True
        else:
            allbina = False
    if allainb and allbina:
        return Relation.EQUAL
    if allainb and not allbina:
        return Relation.SUBSET
    if allbina and not allainb:
        return Relation.SUPERSET
    if ainb or bina:
        return Relation.INTERSECT


if __name__ == '__main__':
    tests = [
        check_expand, 
        check_prefixes, 
        check_fixed, 
        check_dotstar, 
        check_suffixes, 
        check_equal, 
        check_match,
    ]
    
    sg = SubsetGraph(tests)

    any_digit: str = r"(\d+)"
    any_word: str = r"(\w+)"
    any_char: str = r"(.)"

    sg.add_expression(any_digit)
    sg.add_expression(any_word)
    sg.add_expression(any_char)

    print([i.expression for i in sg.match(rf'\s*(?:{any_digit}|{any_word}|{any_char})', strict=False)])
    
    # sg.add_expression('..:..:..:..:..:..')
    # sg.add_expression('^00:11:22:..:..:..')
    # sg.add_expression('..:..:..:33:44:55$')
    # print([i.expression for i in sg.match('00:11:22:33:44:55', False)])
    # sg.add_expression('^00:11:22:33:44:55$')
    # print([i.expression for i in sg.match('00:11:22:33:44:55', True)])
    
