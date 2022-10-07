import numpy as np

# function to evaluate boolean experssions
def evaluate_bool(expr):
    # turning the string (immutable) into a list (mutable)
    expr = list(expr)
    
    # parsing the expression: remove spaces
    while(True):
        try:
            expr.remove(' ')
        except:
            break

    # parsing the expression: separating node names and logical symbols
    parsed_expr = []
    i = 0
    while(i<len(expr)):
        j = i
        while(j<=len(expr)):
            if(j==len(expr)):
                parsed_expr.append(''.join(expr[i:j]))
                i = j+1
                break
            elif(expr[j]=='~' or expr[j]=='&' or expr[j]=='|'):
                if(len(expr[i:j])):
                    parsed_expr.append(''.join(expr[i:j]))
                parsed_expr.append(expr[j])
                i = j+1
                break
            else:
                j += 1

    #print(parsed_expr)

    # evaluating the expression: replace names with str(values)
    for i in range(len(parsed_expr)):
        if(parsed_expr[i] in curr_state):
            parsed_expr[i] = curr_state[parsed_expr[i]]

    #print(parsed_expr)
    # evaluating the expression: solve ~
    while(True):
        try:
            i = parsed_expr.index('~')
        except:
            break

        parsed_expr[i] = not_table[''.join(parsed_expr[i:i+2])]
        del parsed_expr[i+1]

    #print(parsed_expr)

    # evaluating the expression: solve &
    while(True):
        try:
            i = parsed_expr.index('&')
        except:
            break

        parsed_expr[i-1] = and_table[''.join(parsed_expr[i-1:i+2])]
        del parsed_expr[i:i+2]

    #print(parsed_expr)

    # evaluating the expression: solve |
    while(True):
        try:
            i = parsed_expr.index('|')
        except:
            break

        parsed_expr[i-1] = or_table[''.join(parsed_expr[i-1:i+2])]
        del parsed_expr[i:i+2]

    #print(parsed_expr)

    return parsed_expr                
    
# basic truth tables
not_table = {'~0':'1', '~1':'0'}
and_table = {'0&0':'0', '0&1':'0', '1&0':'0', '1&1':'1'}
or_table = {'0|0':'0', '0|1':'1', '1|0':'1', '1|1':'1'}

# loading the node name and equation files
#f_node = open(r'sample_data_files\ABA_CO2_data_files\Stomata2-1\Node_Name_and_their_initial_state_Stomata2-1.txt', 'r')
#f_eqn = open(r'sample_data_files\ABA_CO2_data_files\Stomata2-1\Boolean_Equations_in_words_Stomata2-1.txt', 'r')

f_node = open(r'Node Name and their initial state.txt', 'r')
f_eqn = open(r'Word Boolean Equations File.txt', 'r')

# importing node names and states
base_state = {}
for line in f_node:
    # there are no spaces within a node name
    # identify spaces and parse the lines
    if(' ' in line):
        # a space exists
        i = line.index(' ')
        #base_state[line[:i]] = ''
        init_state = line[i+1:]
        if(' ' in init_state):
            # a space exists. initial state and the colour of the node
            j = init_state.index(' ')
            base_state[line[:i]] = init_state[:j]
        elif('\n' in init_state):
            # no space in init_state. only the initial state
            j = init_state.index('\n')
            base_state[line[:i]] = init_state[:j]
        else:
            # no \n and/or no space in line. copy as is
            base_state[line[:i]] = init_state
    elif('\n' in line):
        # no space, only \n. so no initial state value
        i = line.index('\n')
        base_state[line[:i]] = ''
    else:
        # no \n or space in line. copy as is
        base_state[line] = ''

f_node.close()
#print(base_state)

# importing equations
update_eqns = {}
for line in f_eqn:
    # remove the spaces
    line_foo = list(line)
    while(True):
        try:
            line_foo.remove(' ')
        except:
            break

    # convert the list back to a string after removing the spaces
    # avoid the last character (\n) as well
    if(line_foo[-1] == '\n'):
        line = ''.join(line_foo[:-1])
    else:
        line = ''.join(line_foo)
    
    # parse the equations 
    i = line.index('=')
    update_eqns[line[:i]] = line[i+1:]

f_eqn.close()
#print(update_eqns)    

# input the number of time steps
#time_steps = int(input('Number of time steps\n'))
f_time_steps = open(r'Time Steps Setting.txt', 'r')
for line in f_time_steps:
    if(line[-1]=='\n'):
        time_steps = int(line[:-1])
    else:
        time_steps = int(line)

f_time_steps.close()
#print(time_steps)        

# input the number of initial conditions
#init_cond = int(input('Number of initial conditions\n'))
f_init_cond = open(r'Initialization Setting.txt', 'r')
for line in f_init_cond:
    if(line[-1]=='\n'):
        init_cond = int(line[:-1])
    else:
        init_cond = int(line)

f_init_cond.close()
#print(init_cond)
## simulation

network_states = np.zeros((init_cond, time_steps+1, len(base_state)), dtype='int')
#print(network_states[0,0], network_states.dtype)
node_list = list(base_state.keys())

for ic in range(init_cond):
    print('Starting synchronous initialization {}'.format(ic+1))
    curr_state = base_state.copy()
    # randomise the initial state if it's not set
    for x in curr_state:
        if(curr_state[x]==''):
            curr_state[x] = str(np.random.randint(0,2))

    # store the initial state for this run at t=0
    for n, name in enumerate(node_list):        
        network_states[ic, 0, n] = int(curr_state[name])

    for t in range(time_steps):
        new_state = {x:'' for x in curr_state}
        # computing the future states of each node
        # output of the function is a list with one element, so I extract it with [0]
        for i in curr_state:
            new_state[i] = evaluate_bool(update_eqns[i])[0]

        # updating all nodes at once: synchronous update
        for i in curr_state:
            curr_state[i] = new_state[i]

        for n, name in enumerate(node_list):        
            network_states[ic, t+1, n] = int(curr_state[name])

        #print(network_states[ic,t,:])

# saving the array
np.save('sync_update_array.npy', network_states)          