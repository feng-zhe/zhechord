# ece578_final
The final report for ece 578 advance operating system.
It is to implement the Chord Ring and test it with docker.

## Container Prefix
Because docker containers must have names starting with alphabets. So The prefix will be 'CR_' (chord ring).
Prefix is normally used in requests. But internally, the id without prefix will be used.

## Web API
### /find_predecessor
#### POST
input:  `{'id': xxxx}`
output: `{'id': xxxx}`

### /get_predecessor
#### POST
input:  `{}`
output: `{'id': xxxx}`

### /set_predecessor
#### POST
input:  `{'id': xxxx}`
output: `{}`

### /find_successor
#### POST
input:  `{'id': xxxx}`
output: `{'id': xxxx}`

### /get_successor
#### POST
input:  `{}`
output: `{'id': xxxx}`

### /closet_preceding_finger
#### POST
input:  `{'id': xxxx}`
output: `{'id': xxxx}`

### /update_finger_table
#### POST
input:  `{'s': xxxx, 'i': x}`
output: `{}`

### /display_finger_table
#### POST
input:  `{}`
output: `{'result':[xx,xx,xx]}`
