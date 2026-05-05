# INTEGRANTES:
    EYDEN SU DIAZ

# Logical Propositions

## Problem 1: Smart Building

The OIJ building has an advanced security system that controls access to different areas.

Last Monday, an incident was reported that caused a suspected hack in the company's internal systems. The alarms were activated, the system entered intruder alert mode, and after a security analysis, the main suspect is Ana, the employee on duty closest to the restricted access area.

The goal is to verify whether, given the incident that occurred, Ana gained unauthorized access to the servers, strengthening the theory of a larger plan that exploited a vulnerability in the system design.

### System Rules

- To enter the server room, you need an employee card and a PIN code.
- To enter the meeting room, you need an employee card or to be a registered visitor.
- If you are a registered visitor, then you cannot access the server room.
- If the system is in emergency mode, then all doors open without restriction.
- If there is an intruder alert, then emergency mode is not activated.

### Task

Model the system rules as logical propositions, evaluate the known facts, and corroborate the investigators' hypothesis.

### Facts

- Ana has an employee card.
- Ana does not have a PIN code.
- The system is not in emergency mode.

### Questions

- Can Ana enter the server room?
- Can Ana enter the meeting room?

### Event to Corroborate

If an intruder alert is now activated, does Ana's access to the server room change?
