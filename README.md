# ece578_final
The final report for ece 578 advance operating system.
It is to implement the Chord Ring and test it with docker.

## NOTICE
The branch basic is freezed and only for bug fix. Based on teacher's feedback, it seems the focus should be on fault tolerance.
The branch master is the active branch and contains advanced functions.

## TODO
- put(key) and get(key)
- duplication for fault tolerance.

## Container Prefix
Because docker containers must have names starting with alphabets. So The prefix will be 'CR_' (chord ring).
Prefix is normally used in requests. But internally, the id without prefix will be used.

## Identity, Key
Identity is the position on the ring. While the key is the 'key' in key-value pair.
When putting the key and value, the key will first be hashed and get the identity for the key. And this identity will be used to locate the node which contains the key. So as getting.

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

### /notify
#### POST
input:  `{'id': xxxx}`
output: `{}`

### /display_finger_table
#### POST
input:  `{}`
output: `{'result':[xx,xx,xx]}`

### /put
#### POST
input:  `{'key': xxx, 'value':xxx}`
output: `{}`

### /get
#### POST
input:  `{'key': xxx}`
output: `{'value':xxx}`

### /display_data
#### POST
input:  `{}`
output: `{'result':'<dict object in json>'}`
