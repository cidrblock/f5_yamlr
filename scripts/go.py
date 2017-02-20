import argparse
from yamlr import virtualYamlr

def main():
    """ The main entry point
    """
    parser = argparse.ArgumentParser(description='Dumps bigIP virtual server etc to yaml')
    parser.add_argument('-vs', '--virtual_server', action="store", dest="vs",
                        required=True, help="The name of the virtual server to dump.")
    parser.add_argument('-pt', '--partition', action="store", dest="partition",
                        required=True, help="The name of the parition the virtual server is in.")
    parser.add_argument('-b', '--bigip', action="store", dest="bigip",
                        required=True, help="The fqdn of the bigIP.")
    parser.add_argument('-u', '--username', action="store", dest="username",
                        required=True, help="The username.")
    parser.add_argument('-p', '--password', action="store", dest="password",
                        required=True, help="The password.")
    args = parser.parse_args()
    _response = virtualYamlr(args.vs, args.partition, args.bigip, args.username, args.password)
    print "done"

if __name__ == '__main__':
    main()
