import argparse
import logging
import handlers

logging.basicConfig(level=logging.INFO)

def main():
    # define arguments
    parser = argparse.ArgumentParser(description='helper script for management nodes')
    ex_group = parser.add_mutually_exclusive_group()
    ex_group.add_argument('-r', '--run_node', metavar='NODE_ID [JOIN_BY_NODE_ID]', nargs='+', help='run the chord node with the name(no hash)')
    ex_group.add_argument('-b', '--build_image', action='store_true', help='build the chord image')
    ex_group.add_argument('-c', '--clean_up', metavar='REMOVE_IMAGE', nargs='?', type=bool, const=False, help='clean up and arg is to remove image or not')
    ex_group.add_argument('-n', '--create_network', action='store_true', help='create network')
    ex_group.add_argument('-f', '--display_finger_table', metavar='NODE_ID', nargs='?', type=str, const='-1', help='get finger table, if no NODE_ID, it returns the finger table of the local node.')
    ex_group.add_argument('-d', '--display_data', metavar='NODE_ID', nargs='?', type=str, const='-1', help='display the key value data, if no NODE_ID, it returns the finger table of the local node.')
    ex_group.add_argument('-p', '--remote_put', metavar='NODE_ID KEY VALUE', nargs=3, type=str, help='store key-value pair into the ring via the node. This is application layer put function, so it will put the data into multiple nodes for replication.')
    ex_group.add_argument('-g', '--remote_get', metavar='NODE_ID KEY', nargs=2, type=str, help='get value for the key from the the node, not the ring.')
    ex_group.add_argument('-s', '--sha1', metavar='key', nargs=1, type=str, help='calculate the sha1 hash based on ring size')
    # followings are used internally
    ex_group.add_argument('--local_put', metavar='KEY VALUE', nargs=2, help='store key-value pair into the local node')
    ex_group.add_argument('--local_get', metavar='KEY', nargs=1, type=str, help='get value for the key from the local node')
    ex_group.add_argument('--local_find_successor', metavar='ID', nargs=1, type=str, help='find the successor of the identity')
    # behave according to the arguments
    args = parser.parse_args()
    if args.build_image:
        handlers.build_image()
    elif args.run_node:
        handlers.run_node(args.run_node)
    elif args.clean_up != None:     # could be False
        handlers.clean_up(args.clean_up)
    elif args.create_network:
        handlers.create_network()
    elif args.display_finger_table:
        if args.display_finger_table == '-1':
            handlers.display_finger_table()
        else:
            handlers.display_finger_table(args.display_finger_table)
    elif args.display_data:
        if args.display_data == '-1':
            handlers.display_data()
        else:
            handlers.display_data(args.display_data)
    elif args.remote_put: 
        node_id = args.remote_put[0]
        key = args.remote_put[1]
        value = args.remote_put[2]
        handlers.remote_put(node_id, key, value)
    elif args.local_put:
        key = args.local_put[0]
        value = args.local_put[1]
        handlers.local_put(key, value)
    elif args.remote_get:
        node_id = args.remote_get[0]
        key = args.remote_get[1]
        handlers.remote_get(node_id, key)
    elif args.local_get:
        key = args.local_get[0]
        handlers.local_get(key)
    elif args.local_find_successor:
        identity = args.local_find_successor[0]
        handlers.local_find_successor(identity)
    elif args.sha1:
        handlers.display_hash(args.sha1[0])
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
