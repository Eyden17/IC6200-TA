from logic import And, Not, Implication, Or, Symbol, Biconditional, model_check

server_room = Symbol("Server Room")
meeting_room = Symbol("Meeting Room")

employee_card = Symbol("Employee Card")
pin_code = Symbol("Pin Code")

registered_visitor = Symbol("Visitor")

emergency_mode = Symbol("Emergency Mode")

intruder_alert = Symbol("Intruder Alert")



knowledge = And()


knowledge.add(
    Implication(
        And(
            employee_card, pin_code
        ),
        server_room
    )
)

knowledge.add(
    Implication(
        Or(
            employee_card, registered_visitor
        ),
        meeting_room
    )
)

knowledge.add(
    Implication(
        Not(registered_visitor),
        server_room
    )
)

knowledge.add(
    Implication(
        emergency_mode,
        server_room
    )
)

knowledge.add(
    Implication(
        emergency_mode,
        And(meeting_room, server_room)
    )
)

knowledge.add(
    Implication(
        intruder_alert,
        Not(emergency_mode)
    )
)

knowledge.add(
    employee_card
)

knowledge.add(
    Not(pin_code)
)

knowledge.add(
    Not(emergency_mode)
)

print(f"\nAnswers:")
print(f"Ana entered the server room: {model_check(knowledge, server_room)}")
print(f"Ana entered the meeting room: {model_check(knowledge, meeting_room)}")


print(f"\n\nCase: Intruder Alert is now activated!!!!!")

knowledge.add(
    intruder_alert
)

print(f"Does Ana have access to enter the server room?: {model_check(knowledge, server_room)}")