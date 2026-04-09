#!/usr/bin/env python3
"""Deterministic Pushdown Automaton (PDA) that evaluates RPN expressions.

Supports single-digit numbers (0-9) and operators + and *.
Intermediate results on the stack may be multi-digit.

Two modes:
  step: prints the stack after every step, pausing ~1 s between steps
  run:  prints only the final result
"""

import sys
import time


class Stack:
    def __init__(self):
        self._data: list[int] = []

    def push(self, value: int) -> None:
        self._data.append(value)

    def pop(self) -> int:
        if self.is_empty():
            raise RuntimeError("Stack underflow")
        val = self._data[-1]
        self._data = self._data[:-1]
        return val

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return "[" + ", ".join(str(v) for v in self._data) + "]"


# states
STATE_READ = "q_read"
STATE_ACCEPT = "q_accept"
STATE_REJECT = "q_reject"

OPERATORS = {
    "+": lambda a, b: a + b,
    "*": lambda a, b: a * b
}



def run_pda(expression: str, step_mode: bool = False) -> None:
    """Run the deterministic PDA on *expression* (tokens separated by spaces)."""

    tokens = expression.strip().split()
    stack = Stack()
    state = STATE_READ

    if step_mode:
        print(f"Input: {expression}")
        print(f"State: {state}\n")

    for token in tokens:
        if state == STATE_REJECT:
            break

        # transition function
        if token.isdigit() and len(token) == 1:
            # δ(q_read, digit, ε) → (q_read, push digit)
            stack.push(int(token))
            action = f"Read '{token}' → PUSH {token}"

        elif token in OPERATORS:
            # δ(q_read, op, top2·top1) → (q_read, push result)
            if stack.size() < 2:
                state = STATE_REJECT
                action = f"Read '{token}' → REJECT (not enough operands)"
            else:
                b = stack.pop()
                a = stack.pop()
                result = OPERATORS[token](a, b)
                stack.push(result)
                action = f"Read '{token}' → POP {b}, POP {a}, PUSH {a}{token}{b}={result}"
        else:
            state = STATE_REJECT
            action = f"Read '{token}' → REJECT (invalid token)"

        if step_mode:
            print(f"  {action}")
            print(f"  Stack: {stack}")
            print()
            time.sleep(1)

    # After processing all tokens, check if we are in an accepting configuration
    if state != STATE_REJECT and stack.size() == 1:
        state = STATE_ACCEPT
        result = stack.pop()
        if step_mode:
            print(f"State: {state}")
        print(f"Result: {result}")
    else:
        state = STATE_REJECT
        if step_mode:
            print(f"State: {state}")
        print("Error: input rejected (invalid RPN expression)")
        sys.exit(1)


# CLI entry point
def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in ("step", "run"):
        prog = sys.argv[0]
        print(f"Usage: python {prog} <step|run> \"<RPN expression>\"")
        print(f"  Example: python {prog} step \"3 4 +\"")
        print(f"  Example: python {prog} run  \"3 1 + 7 9 2 * + 1 + +\"")
        sys.exit(2)

    mode = sys.argv[1]
    expression = sys.argv[2]
    run_pda(expression, step_mode=(mode == "step"))


if __name__ == "__main__":
    main()
