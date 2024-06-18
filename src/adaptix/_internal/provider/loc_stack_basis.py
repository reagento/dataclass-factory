from dataclasses import dataclass
from typing import Sequence, Tuple, Type, TypeVar

from .essential import DirectMediator, Provider, Request, RequestChecker, RequestHandler
from .loc_stack_filtering import AnyLocStackChecker, LocStack, LocStackChecker, Pred, create_loc_stack_checker
from .location import AnyLoc
from .methods_provider import MethodsProvider
from .request_checkers import AlwaysTrueRequestChecker

T = TypeVar("T")


@dataclass(frozen=True)
class LocatedRequest(Request[T]):
    loc_stack: LocStack

    @property
    def last_loc(self) -> AnyLoc:
        return self.loc_stack.last


class LocatedRequestChecker(RequestChecker[LocatedRequest]):
    __slots__ = ("loc_stack_checker", )

    def __init__(self, loc_stack_checker: LocStackChecker):
        self.loc_stack_checker = loc_stack_checker

    def check_request(self, mediator: DirectMediator, request: LocatedRequest, /) -> bool:
        return self.loc_stack_checker.check_loc_stack(mediator, request.loc_stack)


class LocatedRequestMethodsProvider(MethodsProvider):
    _loc_stack_checker: LocStackChecker = AnyLocStackChecker()

    @classmethod
    def _validate_request_cls(cls, request_cls: Type[Request]) -> None:
        if not issubclass(request_cls, LocatedRequest):
            raise TypeError(
                f"@method_handler of {LocatedRequestMethodsProvider} can process only child of {LocatedRequest}",
            )

    def _get_request_checker(self) -> RequestChecker:
        return LocatedRequestChecker(self._loc_stack_checker)


def for_predicate(pred: Pred):
    def decorator(cls: Type[LocatedRequestMethodsProvider]):
        if not (isinstance(cls, type) and issubclass(cls, LocatedRequestMethodsProvider)):
            raise TypeError(f"Only {LocatedRequestMethodsProvider} child is allowed")

        cls._loc_stack_checker = create_loc_stack_checker(pred)
        return cls

    return decorator


class LocStackBoundingProvider(Provider):
    def __init__(self, loc_stack_checker: LocStackChecker, provider: Provider):
        self._loc_stack_checker = loc_stack_checker
        self._provider = provider

    def get_request_handlers(self) -> Sequence[Tuple[Type[Request], RequestChecker, RequestHandler]]:
        return [
            (request_cls, self._process_request_checker(request_cls, checker), handler)
            for request_cls, checker, handler in self._provider.get_request_handlers()
        ]

    def _process_request_checker(self, request_cls: Type[Request], checker: RequestChecker) -> RequestChecker:
        if issubclass(request_cls, LocatedRequest):
            if isinstance(checker, AlwaysTrueRequestChecker):
                return LocatedRequestChecker(self._loc_stack_checker)
            if isinstance(checker, LocatedRequestChecker):
                return LocatedRequestChecker(self._loc_stack_checker & checker.loc_stack_checker)
        return checker
