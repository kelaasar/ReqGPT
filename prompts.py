#list of prompts

FRETISH_CONVERT ='''A FRET requirement is a "FRETish" sentence, which is an English sentence containing 
standard boolean expressions. Three fields are mandatory: component, shall, response. 

Given an input requirement, generate thoughts about how to convert the requirement to comply with FRETish using
the given fields, then an output complying with the FRETish standard.

Input: The car should be painted red.

Thoughts: 
Component: car
Response: color = red

Output: Car shall always satisfy (color = red)

Input: The Inner Loop Roll Regulator shall not command angular roll accelerations greater than the 
capability of the system (50 deg/sec2) for durations exceeding 100 frames.

Thoughts:
Component: regulator
Response: (count_roll_output_exceeding_50 <= 100)

Output: Regulator shall always satisfy (count_roll_output_exceeding_50 <= 100)

Input: The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting 
support (not request) and limits are not exceeded (not limits)

Thoughts:
Component: sensor
Response: (senstate = sen_fault_state & !request & !limits) => (senstate = sen_transition_state)

Output: Sensor shall always satisfy (senstate = sen_fault_state & !request & !limits) => (senstate = sen_transition_state)
'''

INCONSISTENCY_CHECK = '''TODO'''