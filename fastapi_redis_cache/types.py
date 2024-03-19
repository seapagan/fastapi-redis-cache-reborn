"""Define some helpful type aliases."""

from collections.abc import Mapping
from inspect import Parameter

ArgType = type[object]
SigParameters = Mapping[str, Parameter]
