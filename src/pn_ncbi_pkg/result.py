"""Python implementation of the Rust std::result to produce Ok/Err wrapped outputs

Not the full functionality, but just a named class to wrap the outputs and indicate
whether the result is a pass or fail. Intended for use in a match-case pattern matching
situation like this e.g.,

def test(x):
    if x < 5:
        return Err(f"{x} is too small")
    else:
        return Ok(f"{x} is big enough")

match test(1):
    case Ok(thing):
        print(f"result was {thing}")
    case Err(thing):
        print(f"error was {thing}")

# result:
# error was 1 is too small
"""

from dataclasses import dataclass
from typing import Generic, Literal, Never, TypeAlias, TypeVar, final

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


@final
@dataclass(frozen=True)
class Ok(Generic[T]):
    """Contains the result on success"""
    value: T

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value


@final
@dataclass(frozen=True)
class Err(Generic[E]):
    """Contains the error message on failure"""
    error: E

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def unwrap(self) -> Never:
        raise RuntimeError(f"called unwrap() on Err: {self.error}")

    def unwrap_or(self, default: U) -> U:
        return default


Result: TypeAlias = Ok[T] | Err[E]
