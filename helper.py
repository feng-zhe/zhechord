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
    ex_group.add_argument('-f', '--display_finger_table', metavar='NODE_ID', nargs='?', type=str, const='-1', help='get local node\'s finger table')
    ex_group.add_argument('-d', '--display_data', metavar='NODE_ID', nargs='?', type=str, const='-1', help='display the local node\'s key value data')
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
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
