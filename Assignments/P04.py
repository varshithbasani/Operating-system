import requests
import json
registers = {
    'R1': 0,
    'R2': 0,
    'R3': 0,
    'R4': 0,
    'R5': 0,
    'R6': 0
}

def perform_operations(instruction):
    
    global registers
    if isinstance(instruction, list):
        for instr in instruction:
            perform_operations(instr)
    else:
        parts = instruction.split()

        if parts[0] == 'LOAD':
            register = parts[1]
            value = int(parts[2])
            registers[register] = value

        elif parts[0] == 'ADD':
            dest_register = parts[1]
            source_register = parts[2]
            registers[dest_register] += registers[source_register]

        elif parts[0] == 'DIV':
            dest_register = parts[1]
            source_register = parts[2]
            registers[dest_register] //= registers[source_register]

        elif parts[0] == 'STORE':
            rgb_values = (registers['R3'], registers['R3'], registers['R3'])
            xy_values = (registers['R1'], registers['R2'])
            # Prepare data to be sent back via API or further processing
            processed_data = {
                "rgb": list(rgb_values),
                "xy": list(xy_values)
            }
            print(processed_data)

# Function to handle the received instructions
def handle_instructions(instructions):
    processed_data = [] 
    for instructions in instructions:
        perform_operations(instructions)
        processed_data.append(processed_data)
    


def get_instructions(num_instructions):
    api_url = f'http://sendmessage.live:8001/grayscale?num={num_instructions}'
    response = requests.get(api_url)
    if response.status_code == 200:
        instructions = response.json()
        return instructions
    else:
        print("Error fetching instructions")
        return []


def main():
    num_instructions = 10  
    instructions = get_instructions(num_instructions)
    # print(f"Retrieved Instructions: {json.dumps(instructions, indent=2)}")
    
    processed_data = handle_instructions(instructions)
    print(processed_data)                           
   
    #send_data_to_api(processed_data)

if _name_ == "_main_":
    main()
# Function to send data back via the API
# def send_data_to_api(data):
#     url = 'http://sendmessage.live:8001/store'  # Replace with the actual endpoint
#     # Send processed data back to the API
#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         print("Data sent successfully")
#     else:
#         print("Error sending data")



# def perform_operations(instructions):
#     result = []
#     for instr_set in instructions:
#         registers = {'R1': 0, 'R2': 0, 'R3': 0, 'R4': 0, 'R5': 0, 'R6': 0, 'R7': 0, 'R8': 0, 'R9': 0, 'R10': 0}
#         for instruction in instr_set:
#             parts = instruction.split()
#             op = parts[0]
#             if op == 'LOAD':
#                 if len(parts) == 3:
#                     registers[parts[1]] = int(parts[2])
#                 else:
#                     print(f"Invalid LOAD instruction: {instruction}")
#             elif op in {'ADD', 'SUB', 'MUL', 'DIV'}:
#                 if len(parts) == 4:
#                     dest_reg = parts[1]
#                     src_reg = parts[2]
#                     try:
#                         value = int(parts[3])
#                         if op == 'ADD':
#                             registers[dest_reg] += registers[src_reg] + value
#                         elif op == 'SUB':
#                             registers[dest_reg] -= registers[src_reg] - value
#                         elif op == 'MUL':
#                             registers[dest_reg] *= registers[src_reg] * value
#                         elif op == 'DIV':
#                             if registers[src_reg] != 0 and value != 0:  # Corrected division operation
#                                 registers[dest_reg] //= registers[src_reg] // value
#                             else:
#                                 print(f"Division by zero error in {instruction}")
#                     except (ValueError, KeyError) as e:
#                         print(f"Error processing {op} instruction: {instruction} - {e}")
#                 else:
#                     print(f"Invalid {op} instruction: {instruction}")
#             elif op == 'STORE':
#                 if len(parts) == 7 and parts[1].startswith('(') and parts[1].endswith(')') and parts[3].startswith('(') and parts[3].endswith(')'):
#                     rgb = [registers[reg] for reg in parts[1][1:-1].split(',')]
#                     xy = [registers[reg] for reg in parts[3][1:-1].split(',')]
#                     result.append({'rgb': rgb, 'xy': xy})
#                 else:
#                     print(f"Invalid STORE instruction: {instruction}")
#             else:
#                 print(f"Unknown instruction: {instruction}")

#             print(registers)  # For debugging purposes, print registers after each instruction

#     print(result)  # For debugging purposes
