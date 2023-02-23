import sys

def get_hash(usr):
    with open('/etc/shadow','r') as shadow:
        for line in shadow:
            if usr in line:
                return line.split(':')[1]
            
def restore_hash(usr):
    lines = ""
    with open('/etc/shadow','r') as shadow:
        print(shadow.readlines())
        for line in shadow:
            if usr in line:
                with open('/etc/shadow','r') as old_hash:
                    line.replace(get_hash(usr),old_hash.readline())
            lines+=line
    with open('/etc/shadow','w') as shadow:
        shadow.write(lines)
        print(shadow.readlines())
        
if __name__ == '__main__':
    with open(sys.argv[1]+'_hash','w') as hash_file:
        hash_file.write(get_hash(sys.argv[1]))