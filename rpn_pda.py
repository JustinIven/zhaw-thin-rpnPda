from manim import *


# Uniform box parameters used everywhere (tape, stack, computation)
BOX_W = 0.8
BOX_H = 0.7
BOX_R = 0.12
BOX_STROKE = 2
FONT_SIZE = 26


def make_cell(label: str, fill_color=DARK_GREY, fill_opacity=0.3) -> VGroup:
    """Create a uniform rounded-rectangle cell with a centred label."""
    rect = RoundedRectangle(
        width=BOX_W, height=BOX_H, corner_radius=BOX_R,
        fill_color=fill_color, fill_opacity=fill_opacity,
        stroke_width=BOX_STROKE,
    )
    txt = Text(label, font_size=FONT_SIZE)
    txt.move_to(rect)
    return VGroup(rect, txt)


class RPNPushdownAutomaton(Scene):
    """Visualize a PDA that evaluates an RPN expression step by step."""

    def construct(self):
        # --- Configuration ---
        expression = ["3", "4", "+"]
        expression = ["3", "1", "+", "7", "9", "2", "*", "+", "1", "+", "+"]
        operators = {"+", "-", "*", "/"}

        # --- Title ---
        title = Text("PDA – RPN Simulation", font_size=40, weight=BOLD)
        subtitle = Text(
            f"Expression: {' '.join(expression)}", font_size=28, color=YELLOW,
        )
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # --- Header ---
        header = Text("Step-by-Step Simulation", font_size=36, weight=BOLD)
        header.scale(0.7).to_edge(UP)

        # --- Input tape (uniform cells) ---
        tape_cells: list[VGroup] = []
        for tok in expression:
            tape_cells.append(make_cell(tok))
        tape_group = VGroup(*tape_cells).arrange(RIGHT, buff=0.08)
        tape_group.next_to(header, DOWN, buff=0.6)
        tape_label = Text("Input Tape", font_size=22, color=GREY_B).next_to(
            tape_group, LEFT, buff=0.4,
        )

        # Read-head arrow
        head = Triangle(fill_opacity=1, fill_color=RED, stroke_width=0).scale(0.15)
        head.next_to(tape_cells[0], DOWN, buff=0.1)
        head_label = Text("head", font_size=16, color=RED).next_to(
            head, DOWN, buff=0.05,
        )

        # --- Stack (right side) ---
        stack_label = Text("Stack", font_size=24, color=GREY_B)
        stack_base = Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE, stroke_width=3)
        stack_anchor = RIGHT * 4.2 + DOWN * 1.5
        stack_base.move_to(stack_anchor)
        stack_label.next_to(stack_base, DOWN, buff=0.2)

        # --- State indicator (left side) ---
        state_box = RoundedRectangle(
            width=2.5, height=0.7, corner_radius=0.15,
            fill_color=BLUE_E, fill_opacity=0.6,
        ).shift(LEFT * 4.5 + DOWN * 1.0)
        state_text = Text("q_read", font_size=22, color=WHITE).move_to(state_box)
        state_lbl = Text("State", font_size=20, color=GREY_B).next_to(
            state_box, UP, buff=0.15,
        )

        # Computation area anchor
        comp_anchor = DOWN * 1.0

        # Action description (placeholder)
        action_text: Mobject = VMobject()

        self.play(
            Write(header),
            FadeIn(tape_group), Write(tape_label),
            FadeIn(head), FadeIn(head_label),
            FadeIn(stack_base), Write(stack_label),
            FadeIn(VGroup(state_box, state_text)), Write(state_lbl),
        )
        self.wait(0.6)

        # --- Simulation ---
        stack_mobs: list[VGroup] = []   # cell VGroups currently on the stack
        stack_vals: list[str] = []

        def stack_pos(index: int):
            """Target centre for the `index`-th stack element."""
            return stack_base.get_top() + UP * (BOX_H / 2 + 0.1 + index * (BOX_H + 0.06))

        for i, token in enumerate(expression):
            # Advance read head
            if i > 0:
                self.play(
                    head.animate.next_to(tape_cells[i], DOWN, buff=0.1),
                    head_label.animate.next_to(tape_cells[i], DOWN, buff=0.35),
                    run_time=0.4,
                )

            # Highlight current tape cell
            self.play(
                tape_cells[i][0].animate.set_fill(YELLOW, opacity=0.4),
                run_time=0.3,
            )

            if token not in operators:
                # ---- PUSH: clone the tape cell and slide it into the stack ----
                new_action = Text(
                    f"Read '{token}' → PUSH {token}", font_size=24, color=TEAL_B,
                ).shift(DOWN * 2.8)
                self.play(FadeOut(action_text), FadeIn(new_action), run_time=0.35)
                action_text = new_action

                # Create a copy that will become the stack element
                cell_copy = make_cell(token, fill_color=TEAL, fill_opacity=0.35)
                cell_copy.move_to(tape_cells[i])   # start at tape position
                self.add(cell_copy)

                target = stack_pos(len(stack_mobs))
                self.play(cell_copy.animate.move_to(target), run_time=0.55)

                stack_mobs.append(cell_copy)
                stack_vals.append(token)

            else:
                # ---- OPERATOR: pop two, show operator table, push result ----
                b_val = stack_vals.pop()
                a_val = stack_vals.pop()
                b_mob = stack_mobs.pop()
                a_mob = stack_mobs.pop()

                result_val = str(int(self._apply_op(token, int(a_val), int(b_val))))

                new_action = Text(
                    f"Read '{token}' → POP {b_val}, POP {a_val}",
                    font_size=22, color=ORANGE,
                ).shift(DOWN * 2.8)
                self.play(FadeOut(action_text), FadeIn(new_action), run_time=0.35)
                action_text = new_action

                # -- Build the target layout:  [ a ]  [ op ]  [ b ]  =  [ res ] --
                op_cell = make_cell(token, fill_color=ORANGE, fill_opacity=0.35)
                eq_sign = Text("=", font_size=FONT_SIZE, color=WHITE)
                res_cell = make_cell(result_val, fill_color=GREEN_E, fill_opacity=0.35)

                # Arrange a dummy row to get target positions
                layout = VGroup(
                    a_mob.copy(), op_cell, b_mob.copy(), eq_sign, res_cell,
                ).arrange(RIGHT, buff=0.18)
                layout.move_to(comp_anchor)
                # Grab final positions from the layout
                a_target = layout[0].get_center()
                op_target = layout[1].get_center()
                b_target = layout[2].get_center()
                eq_target = layout[3].get_center()
                res_target = layout[4].get_center()

                # Place op_cell at the tape and eq/res offscreen
                op_cell.move_to(tape_cells[i])
                eq_sign.move_to(eq_target).set_opacity(0)
                res_cell.move_to(res_target).set_opacity(0)
                self.add(op_cell, eq_sign, res_cell)

                # 1) Slide operator down from tape, slide stack items into position
                self.play(
                    a_mob.animate.move_to(a_target),
                    op_cell.animate.move_to(op_target),
                    b_mob.animate.move_to(b_target),
                    run_time=0.6,
                )

                # 2) Draw surrounding box + show "="
                expr_group = VGroup(a_mob, op_cell, b_mob, eq_sign, res_cell)
                table_box = SurroundingRectangle(
                    expr_group, buff=0.18, corner_radius=BOX_R,
                    color=ORANGE, stroke_width=2,
                )
                self.play(
                    Create(table_box),
                    eq_sign.animate.set_opacity(1),
                    run_time=0.4,
                )

                # 3) Reveal result
                self.play(res_cell.animate.set_opacity(1), run_time=0.45)
                self.wait(0.5)

                # 4) Push result into stack; fade out computation
                result_action = Text(
                    f"PUSH {result_val}", font_size=24, color=GREEN_A,
                ).shift(DOWN * 2.8)
                self.play(FadeOut(action_text), FadeIn(result_action), run_time=0.3)
                action_text = result_action

                stack_target = stack_pos(len(stack_mobs))
                self.play(
                    res_cell.animate.move_to(stack_target),
                    FadeOut(table_box), FadeOut(a_mob), FadeOut(op_cell),
                    FadeOut(b_mob), FadeOut(eq_sign),
                    run_time=0.6,
                )

                stack_mobs.append(res_cell)
                stack_vals.append(result_val)

            # Un-highlight tape cell
            self.play(
                tape_cells[i][0].animate.set_fill(DARK_GREY, opacity=0.3),
                run_time=0.2,
            )
            self.wait(0.25)

        # --- Accept ---
        self.play(FadeOut(action_text))
        new_state = Text("q_acc", font_size=22, color=WHITE).move_to(state_box)
        state_box_new = state_box.copy().set_fill(GREEN_E, opacity=0.6)
        self.play(
            Transform(state_box, state_box_new),
            Transform(state_text, new_state),
            run_time=0.6,
        )

        accept_msg = Text(
            f"✓ Accepted – Result = {stack_vals[0]}",
            font_size=32, color=GREEN_A, weight=BOLD,
        ).shift(DOWN * 2.8)
        self.play(Write(accept_msg))

        self.wait(2)

    # -----------------------------------------------------------------
    @staticmethod
    def _apply_op(op: str, a: int, b: int) -> int:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return a // b
        raise ValueError(f"Unknown operator: {op}")
