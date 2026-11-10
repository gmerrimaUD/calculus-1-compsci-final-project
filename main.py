from dataclasses import dataclass
from drafter import *
from bakery import assert_equal


# Stores each problem the student has attempted
@dataclass
class MyAttempt:
    problem: str
    operation: str
    my_guess: str
    suggested_technique: str


# Stores the current information for the website
@dataclass
class State:
    user_attempts: list[MyAttempt]
    new_problem: str
    differentiation_or_integral: str
    suggested_technique: str


# HELPER FUNCTION
# Looks at the problem and suggests a possible technique
def find_technique(problem: str, operation: str) -> str:
    """
    This function determines what technique should be suggested to the user,
    based on the information input by the user
    """

    has_multiplication = False
    has_division = False
    has_power = False
    has_parentheses = False

    # Look through each character in the problem
    for character in problem:

        if character == "*" or character == "×":
            has_multiplication = True

        if character == "/":
            has_division = True

        if character == "^":
            has_power = True

        if character == "(" or character == ")":
            has_parentheses = True

    # Check for trigonometric functions
    lower_problem = problem.lower()

    has_trig = False
    if "sin" in lower_problem or "cos" in lower_problem or "tan" in lower_problem:
        has_trig = True

    # Check for exponential and logarithmic functions
    has_exp_log = False
    if "ln" in lower_problem or "log" in lower_problem or "e^" in lower_problem:
        has_exp_log = True

    # Check differentiation problems
    if operation == "Differentiation":

        if has_division:
            return "Quotient Rule"

        if has_multiplication:
            return "Product Rule"

        if has_trig and has_parentheses:
            return "Chain Rule"
        
        if has_exp_log:
            return "Exponential and Log Rules"

        if has_power:
            return "Power Rule"

        if has_trig:
            return "Trig Rules"

    # Check integration problems
    if operation == "Integration":

        if has_parentheses and (has_trig or has_exp_log):
            return "U-Substitution"
        
        if has_exp_log:
            return "Exponential and Log Rules"

        if has_power:
            return "Power Rule"

        if has_trig:
            return "Trig Rules"

        return "U-Substitution"

    return "Review the problem manually"
assert_equal(find_technique("x^3", "Differentiation"), "Power Rule")
assert_equal(find_technique("x/2x", "Differentiation"), "Quotient Rule")

# ROUTE 1: HOME PAGE
@route
def index(state: State) -> Page:
    """
    This function dsiplays the home page of the web application.
    It provides information of what the application does,
    and all of the buttons as well to pages of info about the techniques,
    even one for the previous questions they've entered.
    """
    return Page(state, [
        Header("Calculus 1 Technique Helper"),
        "Get help deciding where to start with your calculus problem!",
        "This application suggests techniques without solving the problem for you.",
        "\n",
        Header("Get Started"),
        Button("Enter a New Problem", "select_operation"),
        "\n",
        Header("Learn About Techniques"),
        Button("Power Rule", "power_rule"),
        Button("Chain Rule", "chain_rule"),
        Button("Product Rule", "product_rule"),
        Button("Quotient Rule", "quotient_rule"),
        Button("U-Substitution", "u_sub_rule"),
        Button("Trig Rules", "trig_rules"),
        Button("Exponential and Log Rules", "exponential_log_rules"),
        "\n",
        Button("View My History", "view_history")
    ])

def test_index():
    """
    This is my unit test for the home route
    """
    state = State([], "", "Differentiation", "")
    page = index(state)

    assert_equal(type(page), Page)

# ROUTE 2: SELECT OPERATION
@route
def select_operation(state: State, operation: str = "") -> Page:
    """
    This function prompts the user to select integration or differentiation,
    for thier calculus problem
    """
    if operation == "":
        return Page(state, [
            Header("Choose Your Operation"),
            "Are you working with differentiation or integration?",
            SelectBox("operation", [
                "Differentiation",
                "Integration"
            ]),
            "\n",
            Button("Continue", "select_operation")
        ])

    state.differentiation_or_integral = operation

    return Page(state, [
        Header("Enter Your Problem"),
        "Your selected operation: " + state.differentiation_or_integral,
        "\n",
        "Enter your calculus problem:",
        TextBox("problem"),
        "\n",
        "Which technique do you think will be used?",
        SelectBox("my_guess", [
            "Power Rule",
            "Chain Rule",
            "Product Rule",
            "Quotient Rule",
            "U-Substitution",
            "Trig Rules",
            "Exponential and Log Rules",
            "Not Sure"
        ]),
        "\n",
        Button("Suggest a Technique", "submit_problem"),
        Button("Home", "index")
    ])

def test_select_operation():
    """
    This is my unit test for the select operation route
    """
    state = State([], "", "Differentiation", "")
    page = select_operation(state, "Integration")

    assert_equal(state.differentiation_or_integral,
                 "Integration")
    assert_equal(type(page), Page)
    
# ROUTE 3: SUBMIT PROBLEM
@route
def submit_problem(state: State, problem: str, my_guess: str) -> Page:
    """
    This function prompts the user to type in their Calculus problem. 
    """

    if problem == "":
        return Page(state, [
            Header("Please Enter a Problem. If multiplication use x or *"),
            "You need to enter an equation before continuing.",
            Button("Try Again", "index")
        ])

    state.new_problem = problem

    # Create a new attempt and add it to the history
    new_attempt = MyAttempt(
        problem,
        state.differentiation_or_integral,
        my_guess,
        ""
    )

    state.user_attempts.append(new_attempt)

    return suggest_technique(state)

def test_submit_problem():
    """
    This is my unit test for the submit problem route
    """
    state = State([], "", "Differentiation", "")
    page = submit_problem(state, "x^2", "Power Rule")

    assert_equal(state.new_problem, "x^2")
    assert_equal(len(state.user_attempts), 1)
    assert_equal(type(page), Page)

# ROUTE 4: SUGGEST TECHNIQUE
@route
def suggest_technique(state: State) -> Page:
    """
    This function takes the input the user gave about their calculus problem,
    and then suggests a technique for the user to use on the problem based on that.
    """

    state.suggested_technique = find_technique(
        state.new_problem,
        state.differentiation_or_integral
    )

    # If the integration problem has bounds, remind the student
    if state.differentiation_or_integral == "Integration":
        if "[" in state.new_problem and "]" in state.new_problem:
            state.suggested_technique += " (Remember the bounds!)"

    # Save the suggestion in the most recent history entry
    state.user_attempts[-1].suggested_technique = state.suggested_technique

    content = [
        Header("Your Technique Suggestion"),
        "Your problem: " + state.new_problem,
        "Your operation: " + state.differentiation_or_integral,
        "Your guess: " + state.user_attempts[-1].my_guess,
        "\n",
        "Suggested technique: " + state.suggested_technique,
        "\n",
        "Remember: This is a suggestion to help you get started, not a solved answer."
    ]

    # Take the student to the appropriate technique page
    if "Power Rule" in state.suggested_technique:
        content.append(Button("Learn About Power Rule", "power_rule"))

    elif "Chain Rule" in state.suggested_technique:
        content.append(Button("Learn About Chain Rule", "chain_rule"))

    elif "Product Rule" in state.suggested_technique:
        content.append(Button("Learn About Product Rule", "product_rule"))

    elif "Quotient Rule" in state.suggested_technique:
        content.append(Button("Learn About Quotient Rule", "quotient_rule"))

    elif "U-Substitution" in state.suggested_technique:
        content.append(Button("Learn About U-Substitution", "u_sub_rule"))

    elif "Trig Rules" in state.suggested_technique:
        content.append(Button("Learn About Trig Rules", "trig_rules"))

    elif "Exponential and Log Rules" in state.suggested_technique:
        content.append(Button("Learn About Exponential and Log Rules", "exponential_log_rules"))

    content.append(Button("Try Another Problem", "index"))
    content.append(Button("View History", "view_history"))

    return Page(state, content)

def test_suggest_technique():
    """
    This is my unit test for the suggest technique route
    """
    attempt = MyAttempt("x^2", "Differentiation",
                        "Power Rule", "")
    state = State([attempt], "x^2", "Differentiation", "")

    page = suggest_technique(state)

    assert_equal(state.suggested_technique, "Power Rule")
    assert_equal(state.user_attempts[0].suggested_technique,
                 "Power Rule")
    assert_equal(type(page), Page)

# ROUTE 5: POWER RULE PAGE
@route
def power_rule(state: State) -> Page:
    """
    This page displays information of the power rule, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Power Rule"),
        "Power Rule is one of the first Calculus techniques taught!",
        "\n",
        "It is used for both differentiation and integration.",
        "\n",
        "Differentiation:",
        "Multiply by the current exponent and subtract one from the exponent.",
        "Example: d/dx (x^3) = 3x^2",
        "\n",
        "Integration:",
        "Add one to the exponent and divide by the new exponent.",
        "Example: Integral of x^2 = x^3/3 + C",
        "\n",
        "Tip: Look for variables raised to a power.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_power_rule():
    """
    This is my unit test for the power rule page
    """
    state = State([], "", "Differentiation", "")
    page = power_rule(state)

    assert_equal(type(page), Page)


# ROUTE 6: CHAIN RULE PAGE
@route
def chain_rule(state: State) -> Page:
    """
    This page displays ifnromation of the chain rule, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Chain Rule"),
        "The Chain Rule is used for differentiation.",
        "\n",
        "This is the technique you used when you see soemthing composite, or a power to a power!",
        "\n",
        "It is useful when one function is inside another function.",
        "Example: (3x + 2)^4",
        "\n",
        "Tip: Look for parentheses, a function inside another function.",
        "\n",
        "Even a power to a power. Not to be confused with the product rule, be careful.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_chain_rule():
    """
    This is my unit test for the chain rule page
    """
    state = State([], "", "Differentiation", "")
    page = chain_rule(state)

    assert_equal(type(page), Page)

# ROUTE 7: PRODUCT RULE PAGE
@route
def product_rule(state: State) -> Page:
    """
    This page displays information of the product rule, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Product Rule"),
        "The Product Rule is used for differentiation.",
        "\n",
        "It is used when multiplying two functions together.",
        "\n",
        "Formula: f'(x)g(x) + f(x)g'(x)",
        "\n",
        "This reads as prime f of x multiplied by g of x, plus f of x multiplied by g of x.",
        "\n",
        "Tip: Look for two functions being multiplied.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_product_rule():
    """
    This is my unit test for the product rule page
    """
    state = State([], "", "Differentiation", "")
    page = product_rule(state)

    assert_equal(type(page), Page)

# ROUTE 8: QUOTIENT RULE PAGE
@route
def quotient_rule(state: State) -> Page:
    """
    This page displays information of quotient rule, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Quotient Rule"),
        "The Quotient Rule is used for differentiation.",
        "\n",
        "It is used when one function is divided by another.",
        "\n",
        "Formula: (g(x)f'(x) - f(x)g'(x)) / (g(x))^2",
        "\n",
        "This reads as g of x multiplied by prime f of x",
        "\n",
        "subtracted from f of x multipled by prime g of x",
        "\n",
        "all divided by g of x squared",
        "Tip: Look for one function divided by another function.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_quotient_rule():
    """
    This is my unit test for the quotient rule page
    """
    state = State([], "", "Differentiation", "")
    page = quotient_rule(state)

    assert_equal(type(page), Page)

# ROUTE 9: U-SUBSTITUTION PAGE
@route
def u_sub_rule(state: State) -> Page:
    """
    This page displays information of u-sub, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("U-Substitution"),
        "U-Substitution is used for integration.",
        "\n",
        "It helps simplify integrals that contain an inner function and its derivative.",
        "\n",
        "The basic idea is to replace part of the integral with u.",
        "\n",
        "Tip: Look for an inside function and something related to its derivative.",
        "\n",
        "This technique is usually used when",
        "\n"
        "you cannot 'easily' use another technique.",
        "\n",
        "When choosing your u, do so by choosing the 'difficult' section.",
        "\n",
        "If that doesn't work try again!",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_u_sub_rule():
    """
    This is my unit test for the u-sub rule page
    """
    state = State([], "", "Integration", "")
    page = u_sub_rule(state)

    assert_equal(type(page), Page)

# ROUTE 10: TRIG RULES PAGE
@route
def trig_rules(state: State) -> Page:
    """
    This page displays infromation of trig rules, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Trigonometric Rules"),
        "These rules are useful when working with sine, cosine, and tangent.",
        "\n",
        "Typically for Calculus 1 you won't be using other trig identities as much"
        "\n",
        "so they are not included.",
        "\n",
        "If you need more I suggested looking up more resources on YouTube, as it is out of this sections scope.",
        "\n",
        "Differentiation examples:",
        "Derivative of sin(x) = cos(x)",
        "Derivative of cos(x) = -sin(x)",
        "Derivative of tan(x) = sec(x)^2",
        "\n",
        "Integration examples:",
        "Integral of cos(x) = sin(x) + C",
        "Integral of sin(x) = -cos(x) + C",
        "\n",
        "Tip: Identify which trigonometric function appears in your problem.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_trig_rules():
    """
    This is my unit test for the trig rules page
    """
    state = State([], "", "Differentiation", "")
    page = trig_rules(state)

    assert_equal(type(page), Page)

# ROUTE 11: EXPONENTIAL AND LOG RULES PAGE
@route
def exponential_log_rules(state: State) -> Page:
    """
    This page displays exponential log rules, the tips, and advice for Calculus 1
    """
    return Page(state, [
        Header("Exponential and Logarithmic Rules"),
        "These rules are used when problems contain exponential or logarithmic functions.",
        "\n",
        "Differentiation examples:",
        "Derivative of e^x = e^x",
        "Derivative of ln(x) = 1/x",
        "\n",
        "Integration examples:",
        "Integral of e^x = e^x + C",
        "Integral of 1/x = ln|x| + C",
        "\n",
        "Tip: Look for e, ln, or log in your problem.",
        "\n",
        "Remember: Practice is key! You've got this and don't give up!",
        Button("Home", "index")
    ])

def test_exponential_log_rules():
    """
    This is my unit test for the
    eponential log rules page
    """
    state = State([], "", "Differentiation", "")
    page = exponential_log_rules(state)

    assert_equal(type(page), Page)

# ROUTE 12: HISTORY PAGE
@route
def view_history(state: State) -> Page:
    """
    This function allows the user to see the previous Calculus problems they have input,
    what technique they assumed, and the actual suggested technique. It is displayed in order of oldest to newest.
    """

    content = [
        Header("Problem History"),
        "Here are the problems you have entered previously. In order from the oldest to newest!",
        "\n"
    ]

    if len(state.user_attempts) == 0:
        content.append("You haven't entered any problems yet.")

    else:
        # Go through every MyAttempt instance in the list
        for attempt in state.user_attempts:

            content.append("Problem: " + attempt.problem)
            content.append("Operation: " + attempt.operation)
            content.append("Your guess: " + attempt.my_guess)
            content.append("Suggested technique: " + attempt.suggested_technique)
            content.append("\n")

    content.append(Button("Home", "index"))

    return Page(state, content)

def test_view_history():
    """
    This is my unit test for the view history page
    """
    attempt = MyAttempt("x^2", "Differentiation",
                        "Power Rule", "Power Rule")
    state = State([attempt], "", "Differentiation", "")

    page = view_history(state)

    assert_equal(type(page), Page)
test_index()
test_select_operation()
test_submit_problem()
test_suggest_technique()
test_power_rule()
test_chain_rule()
test_product_rule()
test_quotient_rule()
test_u_sub_rule()
test_trig_rules()
test_exponential_log_rules()
test_view_history()


# START THE WEBSITE
start_server(State(
    [],
    "",
    "Differentiation",
    ""
))
