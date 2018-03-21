import argparse
import logging
import handlers

logging.basicConfig(level=logging.INFO)

def main():
    # define arguments
    parser = argparse.ArgumentParser(description='helper script for management nodes')
    ex_group = parser.add_mutually_exclusive_group()
    ex_group.add_argument('-r', '--run_node', metavar='NODE_NAME', help='run the chord node with the name(no hash)')
    ex_group.add_argument('-b', '--build_image', action='store_true', help='build the chord image')
    ex_group.add_argument('-c', '--clean_up', metavar='REMOVE_IMAGE', nargs='?', type=bool, const=False, help='clean up and arg is to remove image or not')
    ex_group.add_argument('-n', '--create_network', action='store_true', help='create network')
    ex_group.add_argument('-l', '--local_finger_table', action='store_true', help='get local node\'s finger table')
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
    elif args.local_finger_table:
        handlers.local_finger_table()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
